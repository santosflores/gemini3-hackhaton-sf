import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dotenv import load_dotenv
from fastapi import FastAPI
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
# from backend.app.observability import setup_logging, setup_tracing, setup_monitoring

# Load settings
# settings = get_settings()

# Setup Observability
# if settings.GOOGLE_CLOUD_PROJECT:
#     if settings.ENABLE_CLOUD_LOGGING:
#         setup_logging(settings.GOOGLE_CLOUD_PROJECT)
    
#     if settings.ENABLE_CLOUD_MONITORING:
#         setup_monitoring(settings.GOOGLE_CLOUD_PROJECT)

# Wrap the agent in ADKAgent for AG-UI compatibility
agent = ADKAgent(
    adk_agent=root_agent,
    user_id="user", # Default user for this context
)

# Import the agent
# Try importing from backend namespace if running from root, else relative might be needed
# Import the agent
# Try importing from backend namespace if running from root, else relative might be needed
# try:
#     from backend.agents.agent import root_agent as agent
# except ImportError as e:
#     # If we are running inside backend/ or app/ context
#     try:
#         from agents.agent import root_agent as agent
#     except ImportError:
#          print(f"Failed to import agent: {e}")
#          raise e

app = FastAPI(title="FieldHouse API")

# Setup Tracing (needs app instance)
# if settings.GOOGLE_CLOUD_PROJECT and settings.ENABLE_CLOUD_TRACING:
#     setup_tracing(settings.GOOGLE_CLOUD_PROJECT, app)

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

@app.get("/")
def health_check():
    return {"status": "ok"}
