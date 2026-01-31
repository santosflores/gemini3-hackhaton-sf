
import asyncio
import logging
import sys
import os

# Ensure backend/ dir is in path so we can import 'agents'
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agents.agent import root_agent
from ag_ui.core import RunAgentInput

async def test_agent_flow():
    print("Testing full agent flow...")
    
    # Construct input
    input_data = RunAgentInput(
        prompt="What time is it in London?",
        threadId="test-thread-1",
        runId="test-run-1",
        state={},
        messages=[],
        tools=[],
        context=[],
        forwardedProps={}
    )
    
    print(f"Running agent with input: {input_data.prompt}")
    
    try:
        # Agent.run returns an async generator yielding events
        async for event in root_agent.run(input_data):
            print(f"Received Event: {event}")
            # If we see a text event or tool call event, print details
            
    except Exception as e:
        print(f"Agent execution FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_agent_flow())
