import os

APP_NAME = "GeminiHackathonAgent"
FAST_MODEL = "gemini-2.5-flash"

# Ensure API Key is loaded
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY is not set in environment variables.")
