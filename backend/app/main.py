import sys
import os
import warnings
from pathlib import Path

# Suppress Pydantic V2 warnings from libraries using V1 style
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

# Handle .env loading
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    print(f"Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env not found at {env_path}, attempting default load")
    load_dotenv()
from ag_ui_adk import add_adk_fastapi_endpoint
from ag_ui_adk.adk_agent import ADKAgent
from backend.agents.agent import root_agent
# from backend.app.config import get_settings
# Wrap the agent in ADKAgent for AG-UI compatibility
agent = ADKAgent(
    adk_agent=root_agent,
    user_id="user", # Default user for this context
)

app = FastAPI(title="FieldHouse API")

# Register AG-UI endpoint
add_adk_fastapi_endpoint(app, agent, path="/agent-default")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now as per user request for client access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads folder in project root
UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_path = UPLOADS_DIR / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": file.filename, "path": str(file_path)}

from backend.agents.inference import analyze_video
from fastapi import HTTPException

@app.post("/analyze")
async def run_analysis(video_filename: str):
    video_path = UPLOADS_DIR / video_filename
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video {video_filename} not found in uploads")
    
    try:
        result = analyze_video(str(video_path))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
