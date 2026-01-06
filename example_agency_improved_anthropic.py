"""
Improved Agency Setup - Dynamic AI-Controlled Routing with Anthropic Provider

Based on Agency-Code architecture using Anthropic Provider (GLM-4.7 via Z.AI):
- Coder agent is the entry point (receives all user requests)
- Coder intelligently decides when to handoff to Planner
- Planner creates detailed plans and hands back to Coder
- No separate router needed - intelligence is in the instructions
- Uses GLM-4.7 via Z.AI's Anthropic-compatible API

Usage:
    python example_agency_improved_anthropic.py
"""

import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from indusagi import Agent, AgentConfig, Agency
from indusagi.tools import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from indusagi.tools import handoff_to_agent, set_current_agency, registry
from indusagi.hooks import SystemReminderHook, CompositeHook

# ============================================================================
# Agent Factory Functions (Improved Instructions)
# ============================================================================

def create_planner_agent(model: str = "glm-4.7", reasoning_effort: str = "medium") -> Agent:
    """
    Strategic Planner Agent - Creates detailed implementation plans.
    Uses Anthropic provider (GLM-4.7 via Z.AI).

    Loads prompt from markdown file for better maintainability.
    """
    config = AgentConfig(
        model=model,
        provider="anthropic",
        temperature=0.7,
        max_tokens=16000,  # Increased for comprehensive plan generation
    )

    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_anthropic_prompts")
    prompt_file = os.path.join(prompt_dir, "planner_instructions.md")

    agent = Agent(
        name="Planner",
        role="Strategic planning and task breakdown specialist",
        config=config,
        prompt_file=prompt_file  # ✅ Load from .md file
    )

    return agent


def create_coder_agent(model: str = "glm-4.7", reasoning_effort: str = "medium") -> Agent:
    """
    Coder Agent - Entry point with intelligent handoff to Planner.
    Uses Anthropic provider (GLM-4.7 via Z.AI).

    Loads prompt from markdown file for better maintainability.
    """
    config = AgentConfig(
        model=model,
        provider="anthropic",
        temperature=0.5,
        max_tokens=8000,  # Increased for complex implementations
    )

    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_anthropic_prompts")
    prompt_file = os.path.join(prompt_dir, "coder_instructions.md")

    agent = Agent(
        name="Coder",
        role="Code implementation and execution",
        config=config,
        prompt_file=prompt_file  # ✅ Load from .md file
    )

    return agent


# ============================================================================
# Agency Setup
# ============================================================================

def create_development_agency(
    model: str = "glm-4.7",
    reasoning_effort: str = "medium",
    max_handoffs: int = 100,
    max_turns: Optional[int] = None
) -> Agency:
    """
    Create development agency with intelligent routing using Anthropic provider.

    Architecture:
    - Entry: Coder (receives all requests)
    - Coder decides when to handoff to Planner
    - Planner creates plans and hands back to Coder
    - Bidirectional communication flows
    - All agents use GLM-4.7 via Z.AI's Anthropic API

    Args:
        model: LLM model to use (default: "glm-4.7")
        reasoning_effort: Reasoning effort level (default: "medium")
        max_handoffs: Maximum number of handoffs allowed (default: 100)
        max_turns: Max tool-calling iterations per agent. None uses 1000 (default: None)
    """
    # Register tools in global registry
    for tool_class in [Bash, Read, Edit, Write, Glob, Grep, TodoWrite]:
        registry.register(tool_class)

    # Create agents with Anthropic provider
    coder = create_coder_agent(model=model, reasoning_effort=reasoning_effort)
    coder.context = registry.context

    planner = create_planner_agent(model=model, reasoning_effort=reasoning_effort)
    planner.context = registry.context

    # Get tool schemas and add handoff schema
    tools = registry.schemas.copy()
    handoff_schema = {
        "type": "function",
        "function": {
            "name": "handoff_to_agent",
            "description": "Hand off the current task to another agent in the agency",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to hand off to (e.g., 'Planner', 'Coder')"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message or task description for the target agent"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context or additional information"
                    }
                },
                "required": ["agent_name", "message"]
            }
        }
    }
    tools.append(handoff_schema)

    # Create agency with Coder as entry point (receives all user requests)
    agency = Agency(
        entry_agent=coder,  # ✅ Coder is entry - it decides when to use Planner
        agents=[coder, planner],
        communication_flows=[
            (coder, planner),    # Coder can handoff to Planner
            (planner, coder),    # Planner hands back to Coder
        ],
        shared_instructions=None,
        name="DevAgency_Anthropic",
        max_handoffs=max_handoffs,
        max_turns=max_turns,  # ✅ Uses provided max_turns or 1000 if None
        tools=tools,
        tool_executor=registry
    )

    # Set current agency for handoff tools
    set_current_agency(agency)

    return agency


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """
    Main entry point - improved agency with dynamic routing using Anthropic.
    """
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set in environment")
        print("Please set it in .env file")
        return

    print("=" * 70)
    print("  INDUS-AGENTS - Improved Multi-Agent System (Anthropic)")
    print("  Dynamic AI-Controlled Routing: Coder <-> Planner")
    print("  Provider: Anthropic (GLM-4.7 via Z.AI)")
    print("=" * 70)
    print()
    print("How it works:")
    print("  1. You talk to Coder (entry agent)")
    print("  2. Coder decides: simple task = handle directly")
    print("  3.              : complex task = handoff to Planner")
    print("  4. Planner creates plan.md -> hands back to Coder")
    print("  5. Coder reads plan.md and implements")
    print()
    print("=" * 70)
    print()

    # Create agency with GLM-4.7 (via Z.AI Anthropic API)
    print("Creating development agency...")
    agency = create_development_agency(
        model="glm-4.7",  # ✅ GLM-4.7 via Z.AI Anthropic-compatible API
        reasoning_effort="medium",
        max_handoffs=100
        # max_turns=None uses 1000 as default (increased from 100)
    )

    print(f"Agency: {agency.name}")
    print(f"Entry Agent: {agency.entry_agent.name} (smart router)")
    print(f"Agents: {len(agency.agents)} total")
    print(f"Provider: {agency.entry_agent.provider.get_provider_name()}")
    print(f"Model: {agency.entry_agent.config.model}")
    print()

    # Show flows
    print("Communication Flows:")
    agency.visualize()
    print()

    # Example prompts
    print("=" * 70)
    print("EXAMPLE PROMPTS:")
    print("=" * 70)
    print()
    print("Simple tasks (Coder handles directly):")
    print('  "Create a hello world HTML page"')
    print('  "Create a simple calculator with HTML/CSS/JS"')
    print()
    print("Complex tasks (Coder -> Planner -> Coder):")
    print('  "Create plan.md for a todo app, then implement it"')
    print('  "Plan and build a weather dashboard with API integration"')
    print('  "I need a multi-page website. First create plan.md"')
    print()
    print("=" * 70)
    print()

    # Run terminal demo
    print("Starting interactive demo...")
    print("Commands: /quit, /agents, /handoffs, /logs, /stats")
    print()

    try:
        agency.terminal_demo(show_reasoning=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
