"""
This file is the entry point for all agents.
It imports all sub-agents and makes them available for use.
"""

from google.adk import Agent
from .sub_agents.time.agent import currentTimeAgent
root_agent = Agent(
    model='gemini-2.5-flash',
    name='default', 
    description="You are an orchestrator agent that is in charge of finding the intent of the user and delegating the task to the appropriate sub-agent.",
    instruction="""Your primary role is to orchestrate the next play analysis.
1. Start by greeting the user.
2. Ask for a video of the play.
3. Send the video to the `NextPlayAgent` tool to process it.
4. After the `NextPlayAgent` is successful, delegate the full analysis to the `NextPlayPipeline`.
""",
    sub_agents=[currentTimeAgent],
    # tools=[AgentTool(intake_agent)],  # Part 0: Parse user request
)