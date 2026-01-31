"""
This file is the entry point for all agents.
It imports all sub-agents and makes them available for use.
"""

from google.adk import Agent

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='orchestrator',
    description="A strategic partner for retail businesses, guiding them to optimal physical locations that foster growth and profitability.",
    instruction="""Your primary role is to orchestrate the retail location analysis.
1. Start by greeting the user.
2. Check if the `TARGET_LOCATION` (Geographic area to analyze (e.g., "Indiranagar, Bangalore")) and `BUSINESS_TYPE` (Type of business (e.g., "coffee shop", "bakery", "gym")) have been provided.
3. If they are missing, **ask the user clarifying questions to get the required information.**
4. Once you have the necessary details, call the `IntakeAgent` tool to process them.
5. After the `IntakeAgent` is successful, delegate the full analysis to the `LocationStrategyPipeline`.
Your main function is to manage this workflow conversationally.""",
    # sub_agents=[location_strategy_pipeline],
    # tools=[AgentTool(intake_agent)],  # Part 0: Parse user request
)