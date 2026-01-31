import logging
import json
from typing import Optional
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from google.adk import Agent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

# Basic city-to-timezone mapping for demonstration purposes
# In a production environment, use a library like `timezonefinder` or `geopy`
CITY_TO_TIMEZONE = {
    "london": "Europe/London",
    "new york": "America/New_York",
    "san francisco": "America/Los_Angeles",
    "tokyo": "Asia/Tokyo",
    "paris": "Europe/Paris",
    "sydney": "Australia/Sydney",
    "mumbai": "Asia/Kolkata",
    "dubai": "Asia/Dubai",
    "singapore": "Asia/Singapore",
    "monterrey": "America/Monterrey",
    "mexico city": "America/Mexico_City",
    "bangalore": "Asia/Kolkata",
}

def get_current_time(location: str) -> dict:
    """Get the current time in a given location.

    Args:
        location: The location to get the time for (e.g., "London", "New York").

    Returns:
        A dictionary containing the status, time, location, and timezone.
    """
    clean_location = location.lower().split(',')[0].strip()
    
    timezone_str = CITY_TO_TIMEZONE.get(clean_location)
    
    if not timezone_str:
        # Fallback: Try to find if the location is in the keys
        for city, tz in CITY_TO_TIMEZONE.items():
            if city in clean_location or clean_location in city:
                timezone_str = tz
                break
    
    if not timezone_str:
         return json.dumps({
            "status": "error",
            "message": f"Could not resolve timezone for location: {location}. Please provide a major city name like 'London', 'New York', 'Tokyo'.",
            "data": {"location": location}
        })

    try:
        tz = ZoneInfo(timezone_str)
        now = datetime.now(tz)
        return json.dumps({
            "status": "success",
            "data": {
                "time": now.strftime("%H:%M:%S"),
                "location": location,
                "timezone": timezone_str
            }
        })
    except Exception as e:
        logger.error(f"Error getting time for {location}: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Error calculating time: {str(e)}",
            "data": {"location": location}
        })

# FunctionTool uses the function's docstring and signature for the tool definition
current_time_tool = FunctionTool(func=get_current_time)

currentTimeAgent = Agent(
    name="currentTimeAgent",
    model="gemini-3-flash-preview", # Matching the root agent's model family usually
    description="Current time agent",
    instruction="You are a time agent that can get the current time in a given location.",
    tools=[current_time_tool],
    # output_key='time' # ADK Python might not use outputKey in the same way as TS
)
