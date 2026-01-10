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
    # Use shared preset to keep CLI/TUI/examples consistent.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_anthropic_prompts")
    opts = ImprovedAgencyOptions(
        model=model,
        provider="anthropic",
        reasoning_effort=reasoning_effort,
        max_handoffs=max_handoffs,
        max_turns=max_turns,
        name="DevAgency_Anthropic",
        coder_prompt_file=os.path.join(prompt_dir, "coder_instructions.md"),
        planner_prompt_file=os.path.join(prompt_dir, "planner_instructions.md"),
    )
    return create_improved_agency(opts)


# ============================================================================
# Display Functions (Mini Agent Style)
# ============================================================================

def print_agency_banner():
    """Display agency banner in Mini Agent style."""
    banner_text = "[bold bright_cyan]Indus Agents - Multi-Agent System[/bold bright_cyan]\n\n"
    banner_text += "[yellow]Dynamic AI-Controlled Routing: Coder <-> Planner[/yellow]\n"
    banner_text += "[dim]Provider: Anthropic (GLM-4.7 via Z.AI)[/dim]"

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
  [green]5.[/green] Coder reads plan.md and implements
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
    config_table.add_row("Provider:", agency.entry_agent.provider.get_provider_name())
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
    Main entry point - improved agency with dynamic routing using Anthropic.
    """
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(Panel(
            "[red]Error: ANTHROPIC_API_KEY not set in environment[/red]\n\n"
            "Please set it in .env file",
            title="[red]Configuration Error[/red]",
            border_style="red",
            box=box.ROUNDED,
        ))
        return

    # Display banner and workflow
    print_agency_banner()
    print_workflow_explanation()

    # Create agency with GLM-4.7 (via Z.AI Anthropic API)
    console.print("[cyan]Creating development agency...[/cyan]")
    agency = create_development_agency(
        model="glm-4.7",  # ✅ GLM-4.7 via Z.AI Anthropic-compatible API
        reasoning_effort="medium",
        max_handoffs=100
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


if __name__ == "__main__":
    main()
