"""
This file is the entry point for all agents.
It imports all sub-agents and makes them available for use.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional

from google.adk import Agent
from google.adk.tools import FunctionTool
from .sub_agents.time.agent import currentTimeAgent
from .sub_agents.nano_banana.agent import nanoBananaAgent

# Get the project root directory (gemini3-hackhaton-sf)
PROJECT_ROOT = Path(__file__).parent.parent.parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"
INFERENCE_SCRIPT = PROJECT_ROOT / "backend/agents/inference.py"


def run_video_inference(video_filename: str) -> dict:
    """Run the video inference analysis on an uploaded video file.
    
    This tool executes the inference.py script to analyze a football play video
    and predict the most likely plays based on pre-snap formations.
    
    Args:
        video_filename: The filename of the uploaded video to analyze 
                       (e.g., "chiefs_vs_ravens.mp4")
    
    Returns:
        A dictionary containing the analysis results including:
        - status: "success" or "error"
        - final_paragraph: The predicted play analysis as a single paragraph
        - offense_defense: Team identification and positioning
        - motion_detected: Whether pre-snap motion was detected
        - error: Error message if something went wrong
    """
    # Construct the full path to the video
    video_path = UPLOADS_DIR / video_filename
    
    if not video_path.exists():
        return json.dumps({
            "status": "error",
            "message": f"Video file not found: {video_filename}",
            "searched_path": str(video_path)
        })
    
    if not INFERENCE_SCRIPT.exists():
        return json.dumps({
            "status": "error", 
            "message": f"Inference script not found at: {INFERENCE_SCRIPT}"
        })
    
    try:
        # Run the inference script
        import sys
        result = subprocess.run(
            [sys.executable, str(INFERENCE_SCRIPT), str(video_path)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=300,  # 5 minute timeout
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        if result.returncode != 0:
            return json.dumps({
                "status": "error",
                "message": "Inference script failed",
                "stderr": result.stderr[:1000] if result.stderr else None,
                "stdout": result.stdout[:1000] if result.stdout else None
            })
        
        # Find the most recent output directory for this video
        output_dir = PROJECT_ROOT / "backend" / "inference_outputs"
        video_stem = video_path.stem
        
        # Find matching output directories
        matching_dirs = sorted(
            [d for d in output_dir.iterdir() if d.is_dir() and video_stem in d.name],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not matching_dirs:
            return json.dumps({
                "status": "error",
                "message": "No output directory found after inference",
                "stdout": result.stdout[-500:] if result.stdout else None
            })
        
        latest_output = matching_dirs[0]
        
        # Read the combined results
        combined_file = latest_output / "combined_run.json"
        if combined_file.exists():
            with open(combined_file, 'r') as f:
                combined_data = json.load(f)
            
            return json.dumps({
                "status": "success",
                "final_paragraph": combined_data.get("final_paragraph", ""),
                "offense_defense": combined_data.get("stage1_offense_defense", {}),
                "motion_detected": combined_data.get("stage2_motion_cv", {}).get("motion_detected", False),
                "motion_timing": combined_data.get("stage2_motion_cv", {}).get("timing_guess", "unknown"),
                "output_directory": str(latest_output)
            })
        else:
            # Fallback: read the paragraph file directly
            paragraph_file = latest_output / "final_paragraph.txt"
            if paragraph_file.exists():
                return json.dumps({
                    "status": "success",
                    "final_paragraph": paragraph_file.read_text(),
                    "output_directory": str(latest_output)
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Could not find output files",
                    "output_directory": str(latest_output)
                })
                
    except subprocess.TimeoutExpired:
        return json.dumps({
            "status": "error",
            "message": "Inference timed out after 5 minutes"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        })


# Create the tool from the function
video_inference_tool = FunctionTool(func=run_video_inference)


root_agent = Agent(
    model='gemini-2.5-flash',
    name='default', 
    description="You are an AI coaching assistant that helps analyze football plays from video.",
    instruction="""Your primary role is to help coaches analyze football plays.

1. Start by greeting the user warmly and introducing yourself as their AI coaching assistant.
2. Ask the user to share a video of the play they want to analyze.
3. Once the user uploads a video, use the `run_video_inference` tool with the video filename to analyze it.
4. Present the analysis results to the user in a clear, actionable format:
   - Identify the offensive and defensive formations
   - Note any pre-snap motion detected
   - Share the predicted play concepts (ranked by likelihood)
   - Provide coaching insights based on the analysis

Be conversational and supportive. If the analysis fails, help troubleshoot and ask for another video.
""",
    sub_agents=[currentTimeAgent, nanoBananaAgent],
    tools=[video_inference_tool],
    output_key="final_paragraph",
)