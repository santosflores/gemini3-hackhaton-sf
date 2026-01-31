
import asyncio
import logging
# We don't need ModelRegistry for this simple test
# from google.adk.core.model_registry import ModelRegistry

import sys
import os

# Ensure backend/ dir is in path so we can import 'agents'
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from agents.sub_agents.time.agent import current_time_tool

async def test_agent_tool_wrapper():
    print("Testing functionality of wrapped tool...")
    
    # Check tool definition
    print(f"Tool Name: {current_time_tool.name}")
    print(f"Tool Description: {current_time_tool.description}")
    
    args = {"location": "London"}
    try:
        # FunctionTool.run_async takes (args, tool_context)
        # We pass None for tool_context for this simple test
        result = await current_time_tool.run_async(args=args, tool_context=None)
        print(f"Tool execution result: {result}")
        
        # Verify result is serializable (basic check)
        import json
        json.dumps(result)
        
        assert result['status'] == 'success'
    except Exception as e:
        print(f"Tool execution FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_agent_tool_wrapper())
