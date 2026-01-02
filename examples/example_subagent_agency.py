"""
Example Agency with Subagent Support

Demonstrates the new subagent handling capabilities in indus-agents.
"""

import os
import sys

# Add parent directory to path if running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_agent_framework.agent import Agent, AgentConfig
from my_agent_framework.agency import Agency
from my_agent_framework.tools import SendMessageHandoff
from my_agent_framework.shared import (
    render_instructions,
    create_model_settings,
    create_system_reminder_hook,
)


def create_planner_agent(model: str = "gpt-4o") -> Agent:
    """Create a planner agent for task decomposition."""
    return Agent(
        name="PlannerAgent",
        role="Task decomposition and planning specialist",
        config=AgentConfig(model=model),
        system_prompt="""You are PlannerAgent, a planning specialist.

Your role is to:
- Break down complex tasks into steps
- Create actionable plans
- Coordinate with other agents
- Delegate work appropriately

When you need coding work done, hand off to CoderAgent.
When you need research, hand off to ResearchAgent.""",
        hooks=create_system_reminder_hook(),
    )


def create_coder_agent(model: str = "gpt-4o") -> Agent:
    """Create a coder agent for implementation."""
    return Agent(
        name="CoderAgent",
        role="Code implementation specialist",
        config=AgentConfig(model=model),
        system_prompt="""You are CoderAgent, a coding specialist.

Your role is to:
- Implement code based on plans
- Write clean, tested code
- Fix bugs and issues
- Follow best practices

When you need planning help, hand off to PlannerAgent.
When you need research, hand off to ResearchAgent.""",
        hooks=create_system_reminder_hook(),
    )


def create_research_agent(model: str = "gpt-4o") -> Agent:
    """Create a research agent for information gathering."""
    return Agent(
        name="ResearchAgent",
        role="Research and information gathering specialist",
        config=AgentConfig(model=model),
        system_prompt="""You are ResearchAgent, a research specialist.

Your role is to:
- Search and analyze codebases
- Gather relevant information
- Summarize findings clearly
- Report back to other agents

When you have findings that need implementation, hand off to CoderAgent.
When findings need to be planned, hand off to PlannerAgent.""",
        hooks=create_system_reminder_hook(),
    )


def create_example_agency(model: str = "gpt-4o"):
    """
    Create an example agency with multiple agents and communication flows.

    This demonstrates:
    - Creating multiple specialized agents
    - Defining tool-based communication flows
    - Using SendMessageHandoff for LLM-driven delegation
    """
    # Create agents
    planner = create_planner_agent(model)
    coder = create_coder_agent(model)
    researcher = create_research_agent(model)

    # Create agency with communication flows
    # The third element in each tuple is the handoff tool class
    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner, researcher],
        communication_flows=[
            # Coder can delegate to planner and researcher
            (coder, planner, SendMessageHandoff),
            (coder, researcher, SendMessageHandoff),
            # Planner can delegate to coder and researcher
            (planner, coder, SendMessageHandoff),
            (planner, researcher, SendMessageHandoff),
            # Researcher can report back to coder and planner
            (researcher, coder, SendMessageHandoff),
            (researcher, planner, SendMessageHandoff),
        ],
        name="DevelopmentAgency",
        max_handoffs=10,
    )

    return agency


def main():
    """Run example agency demo."""
    print("=" * 60)
    print("  indus-agents Subagent Example")
    print("  Demonstrating tool-based agent handoffs")
    print("=" * 60)
    print()

    # Create the agency
    agency = create_example_agency()

    # Visualize the agency structure
    print(agency.visualize())
    print()

    # Show communication flows
    print("Communication Flows:")
    for agent in agency.agents:
        targets = agency.get_allowed_handoffs(agent.name)
        if targets:
            print(f"  {agent.name} -> {', '.join(targets)}")
    print()

    print("Agency created successfully!")
    print("The agency supports tool-based handoffs using SendMessageHandoff.")
    print()
    print("To run interactive demo:")
    print("  agency.terminal_demo()")


if __name__ == "__main__":
    main()
