import os
import sys
import json
import time
import random
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

import cv2
import chromadb
from chromadb.config import Settings

from google import genai
from google.genai import errors as genai_errors


# ======================================================
# CONFIG
# ======================================================

FAST_MODEL = "gemini-2.5-flash-lite"
FINAL_MODEL = "gemini-3-flash-preview"
EMBED_MODEL = "text-embedding-004"

# We will only send first 6 seconds to Gemini
CLIP_START_SEC = 0
CLIP_DURATION_SEC = 6

# Frame times within the clipped segment
FRAME_TIMES_SEC = [0, 2, 4]

# CV motion thresholds
MOTION_RATIO_THRESHOLD = 0.012
DIFF_THRESHOLD = 25
BLUR_KERNEL = (7, 7)

# Gemini retry/backoff
MAX_API_RETRIES = 5
BACKOFF_BASE_SEC = 0.6
BACKOFF_MAX_SEC = 8.0

# Upload ACTIVE polling (avoids FAILED_PRECONDITION)
POLL_INTERVAL_SEC = 1.0
MAX_WAIT_SEC = 90.0

# Chroma (your persisted folder)
CHROMA_DIR = "chroma_store"
COLLECTION_NAME = "nfl_clips"
TOP_K = 4

OUTPUT_DIR = "inference_outputs"


# ======================================================
# INPUT
# ======================================================

VIDEO_PATH = sys.argv[1] if len(sys.argv) > 1 else None
if not VIDEO_PATH:
    raise RuntimeError("Usage: python inference.py <video_file>")

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("Set GEMINI_API_KEY environment variable")

client = genai.Client()


# ======================================================
# PROMPTS
# ======================================================

OFF_DEF_PROMPT = r"""
You are an NFL film analyst.

TASK:
Identify which side of the screen is OFFENSE and which is DEFENSE in this pre-snap frame.

Be VERY explicit:
- Identify jersey colors for offense and defense (e.g., "white", "red", "blue", "black").
- Identify team names ONLY if clearly visible via logo/wordmark/helmet marking.
- If team identity is unclear, use "unknown".
- Do NOT use jersey color to decide offense vs defense.

Rules:
1) Use the line of scrimmage (ball or center stance).
2) Offense = side with center + QB alignment (shotgun/under center).
3) Defense = opposing unit.
4) If unclear, output "unknown".

Return STRICT JSON ONLY (no markdown, no extra text):
{
  "offense_side": "left | right | unknown",
  "defense_side": "left | right | unknown",
  "offense_team": "string | unknown",
  "defense_team": "string | unknown",
  "offense_jersey_color": "string | unknown",
  "defense_jersey_color": "string | unknown",
  "confidence": "high | medium | low",
  "reasoning": "short explanation"
}
"""

MASTER_PROMPT_WITH_RAG = r"""
ROLE
You are an expert NFL defensive coordinator with 15+ years of film-room experience.

YOU ARE GIVEN
- A short pre-snap video clip (first 6 seconds)
- OFFENSE/DEFENSE assignment JSON (GROUND TRUTH)
- CV motion detection JSON (GROUND TRUTH)
- RAG retrieved past clip JSONs (examples) for schematic calibration only

HARD RULES
- Output MUST be exactly ONE paragraph.
- NO bullets, NO lists, NO headings, NO JSON, NO markdown.
- Do NOT mention probabilities or percentages.
- Analyze ONLY pre-snap info (ignore post-snap results).
- Use OFF/DEF JSON as TRUE and explicitly mention offense/defense team names + jersey colors.
- Use CV motion JSON as TRUE for whether motion happened and roughly when.
- Use RAG examples ONLY to calibrate typical concepts/terminology; do NOT invent team-specific claims.

WHAT THE PARAGRAPH MUST INCLUDE
- Offense vs defense side + team names (or "unknown") + jersey colors
- Offensive formation and any pre-snap motion
- Defensive front/shell
- Top 3 most likely play concepts in ranked order (most → least likely)
- Brief justification tied strictly to alignment/motion/shell

Return exactly ONE paragraph and nothing else.
"""


# ======================================================
# UTIL
# ======================================================

def ensure_dirs():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def require_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        raise RuntimeError("ffmpeg not installed. Run: brew install ffmpeg")

def safe_slug(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in s)

def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def cut_subclip(input_video: str, out_video: str, start_sec: int, dur_sec: int) -> None:
    """
    Creates a new video containing only [start_sec, start_sec+dur_sec).
    Uses stream copy if possible; falls back to re-encode if needed.
    """
    # Try fast stream copy first (very fast)
    cmd_copy = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-t", str(dur_sec),
        "-i", input_video,
        "-c", "copy",
        out_video
    ]
    p = subprocess.run(cmd_copy, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if p.returncode == 0 and Path(out_video).exists() and Path(out_video).stat().st_size > 0:
        return

    # Fallback: re-encode (slower but reliable)
    cmd_reencode = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-t", str(dur_sec),
        "-i", input_video,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        out_video
    ]
    subprocess.run(cmd_reencode, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def extract_frames_at_times(video: str, out_dir: str, times_sec: List[int]) -> List[Path]:
    frames = []
    for t in times_sec:
        out = Path(out_dir) / f"frame_t{t}.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", "-q:v", "2", str(out)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        frames.append(out)
    return frames


# ======================================================
# Gemini helpers
# ======================================================

def call_model_with_backoff(model_name: str, contents: List[Any]) -> str:
    delay = BACKOFF_BASE_SEC
    last_err = None

    for attempt in range(MAX_API_RETRIES):
        try:
            resp = client.models.generate_content(model=model_name, contents=contents)
            txt = getattr(resp, "text", None)
            return (txt or "").strip()
        except genai_errors.ServerError as e:
            last_err = e
            msg = str(e).lower()
            if "503" in msg or "unavailable" in msg or "overloaded" in msg:
                jitter = random.uniform(0.0, 0.35 * delay)
                sleep_for = min(BACKOFF_MAX_SEC, delay + jitter)
                print(f"⚠️  {model_name} overloaded (503). Retry {attempt+1}/{MAX_API_RETRIES} in {sleep_for:.2f}s...")
                time.sleep(sleep_for)
                delay = min(BACKOFF_MAX_SEC, delay * 1.7)
                continue
            raise

    raise RuntimeError(f"Model call failed after retries. Last error: {last_err}")

def parse_json_loose(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Empty model output")
    t = text.strip()
    try:
        return json.loads(t)
    except Exception:
        s, e = t.find("{"), t.rfind("}")
        if s == -1 or e == -1 or e <= s:
            raise ValueError("No JSON object found in model output")
        return json.loads(t[s:e+1])

def generate_json(model_name: str, contents: List[Any], attempts: int = 2) -> Dict[str, Any]:
    last_err = None
    for _ in range(attempts):
        try:
            raw = call_model_with_backoff(model_name, contents)
            return parse_json_loose(raw)
        except Exception as e:
            last_err = e
            contents = contents + ["Return ONLY valid JSON. No markdown. No extra text. No trailing commas."]
    raise RuntimeError(f"Failed to get JSON from {model_name}. Last error: {last_err}")


# ======================================================
# Upload ACTIVE polling
# ======================================================

def wait_until_active(file_obj) -> object:
    file_name = getattr(file_obj, "name", None) or getattr(file_obj, "id", None) or str(file_obj)
    start = time.time()

    while True:
        if time.time() - start > MAX_WAIT_SEC:
            raise RuntimeError(f"Timed out waiting for file ACTIVE: {file_name}")

        cur = client.files.get(name=file_name)
        state = getattr(cur, "state", None)
        state_str = str(state).upper() if state is not None else "UNKNOWN"

        if "ACTIVE" in state_str:
            return cur
        if "FAILED" in state_str:
            raise RuntimeError(f"Upload FAILED: {file_name} state={state_str}")

        time.sleep(POLL_INTERVAL_SEC)

def upload_and_wait(path: str):
    f = client.files.upload(file=path)
    return wait_until_active(f)


# ======================================================
# CV motion
# ======================================================

def _read_gray(path: Path) -> Any:
    img = cv2.imread(str(path))
    if img is None:
        raise RuntimeError(f"Could not read frame: {path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, BLUR_KERNEL, 0)
    return gray

def motion_score_between(a_gray, b_gray) -> float:
    diff = cv2.absdiff(a_gray, b_gray)
    _, thr = cv2.threshold(diff, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
    return float(cv2.countNonZero(thr)) / float(thr.size)

def detect_motion_cv(frame_paths: List[Path]) -> Dict[str, Any]:
    g0 = _read_gray(frame_paths[0])
    g2 = _read_gray(frame_paths[1])
    g4 = _read_gray(frame_paths[2])

    r02 = motion_score_between(g0, g2)
    r24 = motion_score_between(g2, g4)

    motion_detected = (r02 > MOTION_RATIO_THRESHOLD) or (r24 > MOTION_RATIO_THRESHOLD)

    timing = "none"
    if motion_detected:
        timing = "early_to_mid (0->2s)" if r02 >= r24 else "mid_to_late (2->4s)"

    return {
        "frame_times_sec": FRAME_TIMES_SEC,
        "method": "opencv_absdiff_threshold",
        "thresholds": {
            "motion_ratio_threshold": MOTION_RATIO_THRESHOLD,
            "diff_threshold": DIFF_THRESHOLD
        },
        "pairwise_motion_ratio": {
            "t0_to_t2": round(r02, 6),
            "t2_to_t4": round(r24, 6)
        },
        "motion_detected": bool(motion_detected),
        "timing_guess": timing
    }


# ======================================================
# Chroma RAG
# ======================================================

def get_collection():
    db = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    # get_or_create avoids crashing if name mismatch
    return db.get_or_create_collection(COLLECTION_NAME)

def embed_query_text(text: str) -> List[float]:
    res = client.models.embed_content(model=EMBED_MODEL, contents=text)

    # SDK variants
    if hasattr(res, "embeddings") and res.embeddings:
        emb0 = res.embeddings[0]
        if hasattr(emb0, "values"):
            return list(emb0.values)

    if isinstance(res, dict):
        embs = res.get("embeddings") or []
        if embs and "values" in embs[0]:
            return list(embs[0]["values"])

    raise RuntimeError("Could not parse embedding response")

def build_rag_query(off_def: Dict[str, Any], motion_cv: Dict[str, Any]) -> str:
    return (
        "NFL pre-snap similarity query.\n"
        f"offense_side={off_def.get('offense_side')}, defense_side={off_def.get('defense_side')}\n"
        f"offense_color={off_def.get('offense_jersey_color')}, defense_color={off_def.get('defense_jersey_color')}\n"
        f"motion_detected={motion_cv.get('motion_detected')}, timing={motion_cv.get('timing_guess')}\n"
        f"motion_ratios={motion_cv.get('pairwise_motion_ratio')}\n"
    )

def retrieve_rag_examples(off_def: Dict[str, Any], motion_cv: Dict[str, Any], top_k: int = TOP_K) -> List[Dict[str, Any]]:
    col = get_collection()
    qtext = build_rag_query(off_def, motion_cv)
    qemb = embed_query_text(qtext)

    # res = col.query(
    #     query_embeddings=[qemb],
    #     n_results=top_k,
    #     include=["documents", "metadatas", "ids", "distances"]
    # )

    # ids = res.get("ids", [[]])[0]
    # docs = res.get("documents", [[]])[0]
    # metas = res.get("metadatas", [[]])[0]
    # dists = res.get("distances", [[]])[0]


    res = col.query(
    query_embeddings=[qemb],
    n_results=top_k,
    include=["documents", "metadatas", "distances"]
)

    ids = res.get("ids", [[]])[0]                 # IDs are ALWAYS returned
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    out = []
    for i in range(len(ids)):
        out.append({
            "id": ids[i],
            "distance": dists[i],
            "metadata": metas[i],
            "document": docs[i],  # stored JSON string
        })
    return out


# ======================================================
# MAIN
# ======================================================

def main():
    ensure_dirs()
    require_ffmpeg()

    input_video = Path(VIDEO_PATH).expanduser().resolve()
    if not input_video.exists():
        raise RuntimeError(f"Video not found: {input_video}")

    video_name = input_video.stem
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_base = Path(OUTPUT_DIR) / f"{safe_slug(video_name)}__{run_id}"
    out_base.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        # 1) Cut first 6 seconds into a temp clip
        clipped_path = Path(tmp) / f"{video_name}_first{CLIP_DURATION_SEC}s.mp4"
        cut_subclip(str(input_video), str(clipped_path), CLIP_START_SEC, CLIP_DURATION_SEC)

        # 2) Extract frames from the clipped segment
        print("🎞 Extracting frames from first 6 seconds (0s,2s,4s)")
        frame_paths = extract_frames_at_times(str(clipped_path), tmp, FRAME_TIMES_SEC)

        # 3) CV motion (fast, local)
        print("⚡ CV motion")
        motion_cv = detect_motion_cv(frame_paths)
        write_json(out_base / "stage2_motion_cv.json", motion_cv)

        # 4) Upload frames + clipped video (ONLY the 6s clip gets sent)
        print("⏳ Uploading 3 frames + 6s video clip")
        frame_files = [upload_and_wait(str(p)) for p in frame_paths]
        video_file = upload_and_wait(str(clipped_path))

        # 5) Stage 1: Offense vs Defense (fast model)
        print("⚡ Offense vs Defense")
        try:
            off_def = generate_json(FAST_MODEL, [frame_files[0], OFF_DEF_PROMPT], attempts=2)
        except Exception as e:
            off_def = {
                "offense_side": "unknown",
                "defense_side": "unknown",
                "offense_team": "unknown",
                "defense_team": "unknown",
                "offense_jersey_color": "unknown",
                "defense_jersey_color": "unknown",
                "confidence": "low",
                "reasoning": f"fallback_due_to_error: {str(e)[:200]}"
            }
        write_json(out_base / "stage1_offense_defense.json", off_def)

        # 6) RAG
        print("📚 RAG lookup")
        examples = retrieve_rag_examples(off_def, motion_cv, top_k=TOP_K)
        write_json(out_base / "rag_examples.json", {"top_k": TOP_K, "examples": examples})

        # 7) Final prediction (one paragraph) — uses ONLY first 6 seconds video
        print("🧠 Final inference (one paragraph, top 3 plays, no probabilities)")
        final_text = call_model_with_backoff(
            FINAL_MODEL,
            [
                video_file,
                "OFFENSE/DEFENSE ASSIGNMENT JSON (GROUND TRUTH):\n" + json.dumps(off_def),
                "CV MOTION JSON (GROUND TRUTH):\n" + json.dumps(motion_cv),
                "RAG EXAMPLES (stored JSON strings):\n" + json.dumps(examples),
                MASTER_PROMPT_WITH_RAG
            ]
        ).strip()

        # Enforce single paragraph
        final_one_paragraph = " ".join(final_text.split())
        (out_base / "final_paragraph.txt").write_text(final_one_paragraph, encoding="utf-8")

        combined = {
            "meta": {
                "input_video": str(input_video),
                "clipped_video_sent_to_gemini": str(clipped_path),
                "clip_window_sec": {"start": CLIP_START_SEC, "duration": CLIP_DURATION_SEC},
                "video_name": video_name,
                "run_id": run_id,
                "models": {
                    "fast_model_offdef": FAST_MODEL,
                    "final_model": FINAL_MODEL,
                    "embed_model": EMBED_MODEL
                },
                "chroma": {
                    "dir": CHROMA_DIR,
                    "collection": COLLECTION_NAME,
                    "top_k": TOP_K
                }
            },
            "stage1_offense_defense": off_def,
            "stage2_motion_cv": motion_cv,
            "rag_examples": examples,
            "final_paragraph": final_one_paragraph
        }
        write_json(out_base / "combined_run.json", combined)

        print("\n✅ FINAL OUTPUT\n")
        print(final_one_paragraph)
        print(f"\n✅ Saved to: {out_base}\n")


if __name__ == "__main__":
    main()