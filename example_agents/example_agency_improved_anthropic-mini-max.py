"""
Improved Agency Setup - Dynamic AI-Controlled Routing with MiniMax Provider

Based on Agency-Code architecture using MiniMax Provider (MiniMax-M2.1):
- Coder agent is the entry point (receives all user requests)
- Coder intelligently decides when to handoff to Planner
- Planner creates detailed plans and hands back to Coder
- No separate router needed - intelligence is in the instructions
- Uses MiniMax-M2.1 via MiniMax's Anthropic-compatible API

Setup:
    1. Get MiniMax API key from https://platform.minimax.io/
    2. Set MINIMAX_API_KEY in .env file
    3. Set MINIMAX_BASE_URL=https://api.minimax.io/anthropic (or https://api.minimaxi.com/anthropic for China)

Usage:
    python example_agency_improved_anthropic-mini-max.py
"""

import os
import argparse
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from indusagi import Agent, AgentConfig, Agency
from indusagi.tools import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from indusagi.tools import handoff_to_agent, set_current_agency, registry
from indusagi.hooks import SystemReminderHook, CompositeHook
from indusagi.presets.improved_anthropic_agency import ImprovedAgencyOptions, create_improved_agency

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Initialize Rich console
console = Console()

# ============================================================================
# Agent Factory Functions (Improved Instructions)
# ============================================================================

def create_planner_agent(model: str = "MiniMax-M2.1", reasoning_effort: str = "medium") -> Agent:
    """
    Strategic Planner Agent - Creates detailed implementation plans.
    Uses MiniMax provider (MiniMax-M2.1).

    Loads prompt from markdown file for better maintainability.
    """
    config = AgentConfig(
        model=model,
        provider="anthropic",  # Uses Anthropic-compatible API
        temperature=1,
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


def create_coder_agent(model: str = "MiniMax-M2.1", reasoning_effort: str = "medium") -> Agent:
    """
    Coder Agent - Entry point with intelligent handoff to Planner.
    Uses MiniMax provider (MiniMax-M2.1).

    Loads prompt from markdown file for better maintainability.
    """
    config = AgentConfig(
        model=model,
        provider="anthropic",  # Uses Anthropic-compatible API
        temperature=1,
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


def create_critic_agent(model: str = "MiniMax-M2.1", reasoning_effort: str = "medium") -> Agent:
    """
    Critic Agent - Risk, QA, and review specialist for plans and code.
    Uses MiniMax provider (MiniMax-M2.1).

    Loads prompt from markdown file for better maintainability.
    """
    config = AgentConfig(
        model=model,
        provider="anthropic",  # Uses Anthropic-compatible API
        temperature=1,
        max_tokens=8000,  # For comprehensive risk analysis
    )

    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_anthropic_prompts")
    prompt_file = os.path.join(prompt_dir, "critic_instructions.md")

    agent = Agent(
        name="Critic",
        role="Risk and quality reviewer (edge cases, failure modes, test ideas)",
        config=config,
        prompt_file=prompt_file  # ✅ Load from .md file
    )

    return agent


# ============================================================================
# Agency Setup
# ============================================================================

def create_development_agency(
    model: str = "MiniMax-M2.1",
    reasoning_effort: str = "medium",
    max_handoffs: int = 100,
    max_turns: Optional[int] = None,
    use_thread_pool: bool = False,
    thread_response_timeout: float = 600.0,
) -> Agency:
    """
    Create development agency with intelligent routing using MiniMax provider.

    Architecture:
    - Entry: Coder (receives all requests)
    - Coder decides when to handoff to Planner
    - Planner creates plans and hands back to Coder
    - Bidirectional communication flows
    - All agents use MiniMax-M2.1 via MiniMax's Anthropic-compatible API

    Args:
        model: LLM model to use (default: "MiniMax-M2.1")
        reasoning_effort: Reasoning effort level (default: "medium")
        max_handoffs: Maximum number of handoffs allowed (default: 100)
        max_turns: Max tool-calling iterations per agent. None uses 1000 (default: None)
        use_thread_pool: Run each agent in isolated thread with separate resources (default: False)
        thread_response_timeout: Timeout for thread responses in seconds (default: 600.0)
    """
    # Register tools
    for tool_class in [Bash, Read, Edit, Write, Glob, Grep, TodoWrite]:
        try:
            registry.register(tool_class)
        except Exception:
            pass  # Tool might already be registered

    # Create agents with MiniMax
    coder = create_coder_agent(model=model, reasoning_effort=reasoning_effort)
    coder.context = registry.context

    planner = create_planner_agent(model=model, reasoning_effort=reasoning_effort)
    planner.context = registry.context

    critic = create_critic_agent(model=model, reasoning_effort=reasoning_effort)
    critic.context = registry.context

    # Get tool schemas and add handoff schema
    tools = registry.schemas.copy()
    handoff_schema = {
        "type": "function",
        "function": {
            "name": "handoff_to_agent",
            "description": "Hand off the current task to another agent(s) in the agency. Supports single or parallel handoffs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to hand off to (e.g., 'Planner', 'Coder', 'Critic'). Use this for single handoffs."
                    },
                    "agent_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent names for parallel handoffs (e.g., ['Planner', 'Critic'])"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message or task description for the target agent(s)"
                    },
                    "aggregation_target": {
                        "type": "string",
                        "description": "Agent to aggregate parallel results (default: 'Coder')"
                    }
                },
                "required": ["message"]
            }
        }
    }
    tools.append(handoff_schema)

    # Create agency
    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner, critic],
        communication_flows=[
            (coder, planner), (planner, coder),
            (coder, critic), (critic, coder),
            (planner, critic), (critic, planner),
        ],
        shared_instructions=None,
        name="DevAgency_MiniMax",
        max_handoffs=max_handoffs,
        max_turns=max_turns,
        tools=tools,
        tool_executor=registry,
        use_thread_pool=use_thread_pool,
        thread_response_timeout=thread_response_timeout,
    )

    # Set current agency for handoff tools
    set_current_agency(agency)

    return agency


# ============================================================================
# Display Functions (Mini Agent Style)
# ============================================================================

def print_agency_banner():
    """Display agency banner in Mini Agent style."""
    banner_text = "[bold bright_cyan]Indus Agents - Multi-Agent System[/bold bright_cyan]\n\n"
    banner_text += "[yellow]Dynamic AI-Controlled Routing: Coder <-> Planner <-> Critic[/yellow]\n"
    banner_text += "[dim]Provider: MiniMax (MiniMax-M2.1)[/dim]"

    console.print()
    console.print(Panel(
        banner_text,
        box=box.DOUBLE_EDGE,
        border_style="bright_cyan",
        padding=(1, 2),
        width=70,
    ))
    console.print()


def print_workflow_explanation():
    """Display workflow explanation."""
    workflow = """[bold cyan]How it works:[/bold cyan]

  [green]1.[/green] You talk to [bright_blue]Coder[/bright_blue] (entry agent)
  [green]2.[/green] Coder decides: simple task = handle directly
  [green]3.[/green]              : complex task = handoff to [bright_blue]Planner[/bright_blue]
  [green]4.[/green] Planner creates plan.md -> hands back to [bright_blue]Coder[/bright_blue]
  [green]5.[/green] Optional: Coder can fan out to [bright_blue]Planner[/bright_blue] + [bright_blue]Critic[/bright_blue] in parallel
  [green]6.[/green] Coder merges parallel outputs and implements
"""

    console.print(Panel(
        workflow,
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2),
        width=70,
    ))
    console.print()


def print_agency_config(agency):
    """Display agency configuration in table."""
    config_table = Table.grid(padding=(0, 2))
    config_table.add_column(style="cyan", justify="left", width=20)
    config_table.add_column(style="white", justify="left")

    config_table.add_row("Agency:", agency.name)
    config_table.add_row("Entry Agent:", f"[bright_blue]{agency.entry_agent.name}[/bright_blue] (smart router)")
    config_table.add_row("Total Agents:", str(len(agency.agents)))
    config_table.add_row("Provider:", "MiniMax (Anthropic-compatible)")
    config_table.add_row("Model:", agency.entry_agent.config.model)

    console.print(Panel(
        config_table,
        title="[bright_cyan]Agency Configuration[/bright_cyan]",
        box=box.ROUNDED,
        border_style="bright_cyan",
        padding=(1, 2),
    ))
    console.print()


def print_example_prompts():
    """Display example prompts."""
    examples = """[bold yellow]Simple tasks (Coder handles directly):[/bold yellow]
  [green]-[/green] "Create a hello world HTML page"
  [green]-[/green] "Create a simple calculator with HTML/CSS/JS"

[bold yellow]Complex tasks (Coder -> Planner -> Coder):[/bold yellow]
  [green]-[/green] "Create plan.md for a todo app, then implement it"
  [green]-[/green] "Plan and build a weather dashboard with API integration"
  [green]-[/green] "I need a multi-page website. First create plan.md"
[bold yellow]Parallel handoffs (Coder fans out to multiple agents):[/bold yellow]
  [green]-[/green] "Run Planner + Critic in parallel for a spec and risk list"
  [green]-[/green] "Ask Planner and Coder to explore two options, then summarize"
"""

    console.print(Panel(
        examples,
        title="[bright_cyan]Example Prompts[/bright_cyan]",
        box=box.ROUNDED,
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print()


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """
    Main entry point - improved agency with dynamic routing using MiniMax.
    """
    # Check for API key and set up environment
    api_key = os.getenv("MINIMAX_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print(Panel(
            "[red]Error: MINIMAX_API_KEY not set in environment[/red]\n\n"
            "Please set it in .env file:\n"
            "MINIMAX_API_KEY=your-minimax-api-key\n"
            "MINIMAX_BASE_URL=https://api.minimax.io/anthropic\n\n"
            "Get your API key at: https://platform.minimax.io/",
            title="[red]Configuration Error[/red]",
            border_style="red",
            box=box.ROUNDED,
        ))
        return
    
    # Set environment variables for MiniMax
    # The AnthropicProvider will use these
    os.environ["ANTHROPIC_API_KEY"] = api_key
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/anthropic")
    os.environ["ANTHROPIC_BASE_URL"] = base_url
    
    console.print(f"[dim]Using MiniMax API endpoint: {base_url}[/dim]\n")

    parser = argparse.ArgumentParser(description="Improved Agency Demo (MiniMax)")
    parser.add_argument(
        "--thread-pool",
        action="store_true",
        help="Run each agent in an isolated worker thread with separate tools",
    )
    parser.add_argument(
        "--thread-timeout",
        type=float,
        default=600.0,
        help="Seconds to wait for a threaded agent response before timing out",
    )
    args = parser.parse_args()

    # Display banner and workflow
    print_agency_banner()
    print_workflow_explanation()

    # Create agency with MiniMax-M2.1
    console.print("[cyan]Creating development agency...[/cyan]")
    agency = create_development_agency(
        model="MiniMax-M2.1",  # ✅ MiniMax-M2.1 via MiniMax API
        reasoning_effort="medium",
        max_handoffs=100,
        use_thread_pool=args.thread_pool,
        thread_response_timeout=args.thread_timeout,
        # max_turns=None uses 1000 as default (increased from 100)
    )

    # Display configuration
    print_agency_config(agency)

    # Show flows
    console.print(Panel(
        "[bold]Communication Flows:[/bold]",
        box=box.ROUNDED,
        border_style="dim",
    ))
    agency.visualize()
    console.print()

    # Show examples
    print_example_prompts()

    # Run terminal demo
    console.print(Panel(
        "[cyan]Starting interactive demo...[/cyan]\n\n"
        "[dim]Commands: /quit, /agents, /handoffs, /logs, /stats[/dim]",
        box=box.ROUNDED,
        border_style="green",
    ))
    console.print()

    try:
        agency.terminal_demo(show_reasoning=False)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user. Exiting...[/yellow]")
    except Exception as e:
        console.print(Panel(
            f"[red]{str(e)}[/red]",
            title="[red]Error[/red]",
            border_style="red",
            box=box.ROUNDED,
        ))
        import traceback
        traceback.print_exc()
    finally:
        agency.shutdown()


if __name__ == "__main__":
    main()
