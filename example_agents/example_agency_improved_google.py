"""
Improved Agency Setup - Dynamic AI-Controlled Routing with Google Gemini Provider

Based on Agency-Code architecture using Google Gemini:
- Coder agent is the entry point (receives all user requests)
- Coder intelligently decides when to handoff to Planner
- Planner creates detailed plans and hands back to Coder
- No separate router needed - intelligence is in the instructions

Usage:
    python example_agency_improved_google.py
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from indusagi import Agent, AgentConfig, Agency
from indusagi.presets.improved_anthropic_agency import (
    ImprovedAgencyOptions,
    create_improved_agency,
)

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.panel import Panel
from rich import box

# Initialize Rich console
console = Console()

# ============================================================================
# Agent Factory Functions (Improved Instructions)
# ============================================================================


def create_planner_agent(model: Optional[str] = None) -> Agent:
    """
    Strategic Planner Agent - Creates detailed implementation plans.
    Uses Google Gemini provider.

    Loads prompt from markdown file for better maintainability.
    """
    model = model or os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    config = AgentConfig(
        model=model,
        provider="google",
        temperature=1,
        max_tokens=16000,  # Increased for comprehensive plan generation
    )

    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_google_prompts")
    prompt_file = os.path.join(prompt_dir, "planner_instructions.md")

    return Agent(
        name="Planner",
        role="Strategic planning and task breakdown specialist",
        config=config,
        prompt_file=prompt_file,
    )


def create_coder_agent(model: Optional[str] = None) -> Agent:
    """
    Coder Agent - Entry point with intelligent handoff to Planner.
    Uses Google Gemini provider.

    Loads prompt from markdown file for better maintainability.
    """
    model = model or os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    config = AgentConfig(
        model=model,
        provider="google",
        temperature=1,
        max_tokens=8000,  # Increased for complex implementations
    )

    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_google_prompts")
    prompt_file = os.path.join(prompt_dir, "coder_instructions.md")

    return Agent(
        name="Coder",
        role="Code implementation and execution",
        config=config,
        prompt_file=prompt_file,
    )


def create_critic_agent(model: Optional[str] = None) -> Agent:
    """
    Critic Agent - Risk, QA, and review specialist for plans and code.
    Uses Google Gemini provider.

    Loads prompt from markdown file for better maintainability.
    """
    model = model or os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    config = AgentConfig(
        model=model,
        provider="google",
        temperature=1,
        max_tokens=8000,  # For comprehensive risk analysis
    )

    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_google_prompts")
    prompt_file = os.path.join(prompt_dir, "critic_instructions.md")

    return Agent(
        name="Critic",
        role="Risk and quality reviewer (edge cases, failure modes, test ideas)",
        config=config,
        prompt_file=prompt_file,
    )


# ============================================================================
# Agency Setup
# ============================================================================


def create_development_agency(
    model: Optional[str] = None,
    reasoning_effort: str = "medium",
    max_handoffs: int = 100,
    max_turns: Optional[int] = None,
    use_thread_pool: bool = False,
    thread_response_timeout: float = 600.0,
) -> Agency:
    """
    Create development agency with intelligent routing using Google Gemini provider.

    Architecture:
    - Entry: Coder (receives all requests)
    - Coder decides when to handoff to Planner
    - Planner creates plans and hands back to Coder
    - Bidirectional communication flows
    """
    model = model or os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_google_prompts")
    opts = ImprovedAgencyOptions(
        model=model,
        provider="google",
        reasoning_effort=reasoning_effort,
        max_handoffs=max_handoffs,
        max_turns=max_turns,
        name="DevAgency_Google",
        coder_prompt_file=os.path.join(prompt_dir, "coder_instructions.md"),
        planner_prompt_file=os.path.join(prompt_dir, "planner_instructions.md"),
        critic_prompt_file=os.path.join(prompt_dir, "critic_instructions.md"),
        use_thread_pool=use_thread_pool,
        thread_response_timeout=thread_response_timeout,
    )
    return create_improved_agency(opts)


# ============================================================================
# Display Functions (Mini Agent Style)
# ============================================================================


def print_agency_banner():
    """Display agency banner in Mini Agent style."""
    banner_text = "[bold bright_cyan]Indus Agents - Multi-Agent System[/bold bright_cyan]\n\n"
    banner_text += "[yellow]Dynamic AI-Controlled Routing: Coder <-> Planner[/yellow]\n"
    banner_text += "[dim]Provider: Google Gemini[/dim]"

    console.print()
    console.print(
        Panel(
            banner_text,
            box=box.DOUBLE_EDGE,
            border_style="bright_cyan",
            padding=(1, 2),
            width=70,
        )
    )
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

    console.print(
        Panel(
            workflow,
            box=box.ROUNDED,
            border_style="cyan",
            padding=(1, 2),
            width=70,
        )
    )
    console.print()


def print_agent_config():
    """Display agent configuration."""
    config_text = """[bold]Agents:[/bold]
- [bright_blue]Coder[/bright_blue] (Entry point)
- [bright_blue]Planner[/bright_blue] (Strategic planning)
- [bright_blue]Critic[/bright_blue] (Risk/QA review)

[bold]Provider:[/bold] Google Gemini
[bold]Model:[/bold] {model}
"""

    console.print(
        Panel(
            config_text.format(model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")),
            box=box.ROUNDED,
            border_style="green",
            padding=(1, 2),
            width=70,
        )
    )
    console.print()


# ============================================================================
# Main Demo Runner
# ============================================================================


def run_interactive_agency():
    """Run the interactive agency demo."""
    print_agency_banner()
    print_workflow_explanation()
    print_agent_config()

    agency = create_development_agency()

    console.print(Panel(
        "[bold]Communication Flows:[/bold]\n- Coder -> Planner\n- Planner -> Coder\n- Coder -> Critic (optional)\n- Critic -> Coder",
        box=box.ROUNDED,
        border_style="dim",
    ))
    console.print(agency.visualize())
    console.print()

    agency.terminal_demo(show_reasoning=False)


if __name__ == "__main__":
    run_interactive_agency()
