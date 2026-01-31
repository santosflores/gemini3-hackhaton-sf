from typing import Any, Dict, List, Optional
from copilotkit import Agent
from google.adk import Agent as ADKAgent

class ADKCopilotAgent(Agent):
    def __init__(self, adk_agent: ADKAgent, name: str, description: str):
        super().__init__(name=name, description=description)
        self.adk_agent = adk_agent

    async def stream(self, messages: List[Dict[str, Any]]) -> Any:
        if not messages:
            return

        # Extract the last user message
        last_message = messages[-1]
        user_input = last_message.get("content", "")

        # TODO: Handle full history if ADK supports it
        # For now, we pass the user input to the agent
        
        try:
            # Demonstration of streaming text
            # CAUTION: This assumes adk_agent has a .model property with .generate_content
            # This is likely where it fails if the API doesn't match.
            print(f"DEBUG: Starting stream for input: {user_input}", flush=True)
            
            # Temporary fallback: Just yield a hardcoded string if ADK integration isn't ready
            # response = self.adk_agent.model.generate_content(user_input, stream=True)
            # for chunk in response:
            #    if chunk.text:
            #        yield {
            #            "type": "text",
            #            "content": chunk.text
            #        }
            
            yield {
                "type": "text",
                "content": f"Echo: {user_input}"
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Fallback for debugging
            yield {
                "type": "text",
                "content": f"Error interacting with agent: {str(e)}"
            }

    async def execute(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        # Return the async generator for StreamingResponse
        return self.stream(messages)

    async def get_state(self, **kwargs) -> Any:
        return {}


