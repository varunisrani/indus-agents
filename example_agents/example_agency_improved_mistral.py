"""
Improved Agency Setup - Dynamic AI-Controlled Routing with Mistral Provider

Based on Agency-Code architecture using Mistral Provider:
- Coder agent is the entry point (receives all user requests)
- Coder intelligently decides when to handoff to Planner
- Planner creates detailed plans and hands back to Coder
- No separate router needed - intelligence is in the instructions
- Uses Mistral's OpenAI-compatible API

Usage:
    python example_agency_improved_mistral.py
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

def create_planner_agent(model: Optional[str] = None, reasoning_effort: str = "medium") -> Agent:
    """
    Strategic Planner Agent - Creates detailed implementation plans.
    Uses Mistral provider.

    Loads prompt from markdown file for better maintainability.
    """
    model = model or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    config = AgentConfig(
        model=model,
        provider="mistral",
        temperature=1,
        max_tokens=16000,  # Increased for comprehensive plan generation
    )

    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_prompts")
    prompt_file = os.path.join(prompt_dir, "planner_instructions.md")

    agent = Agent(
        name="Planner",
        role="Strategic planning and task breakdown specialist",
        config=config,
        prompt_file=prompt_file  # ✅ Load from .md file
    )

    return agent


def create_coder_agent(model: Optional[str] = None, reasoning_effort: str = "medium") -> Agent:
    """
    Coder Agent - Entry point with intelligent handoff to Planner.
    Uses Mistral provider.

    Loads prompt from markdown file for better maintainability.
    """
    model = model or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    config = AgentConfig(
        model=model,
        provider="mistral",
        temperature=1,
        max_tokens=8000,  # Increased for complex implementations
    )

    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_prompts")
    prompt_file = os.path.join(prompt_dir, "coder_instructions.md")

    agent = Agent(
        name="Coder",
        role="Code implementation and execution",
        config=config,
        prompt_file=prompt_file  # ✅ Load from .md file
    )

    return agent


def create_critic_agent(model: Optional[str] = None, reasoning_effort: str = "medium") -> Agent:
    """
    Critic Agent - Risk, QA, and review specialist for plans and code.
    Uses Mistral provider.

    Loads prompt from markdown file for better maintainability.
    """
    model = model or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    config = AgentConfig(
        model=model,
        provider="mistral",
        temperature=1,
        max_tokens=8000,  # For comprehensive risk analysis
    )

    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_prompts")
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
    model: Optional[str] = None,
    reasoning_effort: str = "medium",
    max_handoffs: int = 100,
    max_turns: Optional[int] = None,
    use_thread_pool: bool = False,
    thread_response_timeout: float = 600.0,
) -> Agency:
    """
    Create development agency with intelligent routing using Mistral provider.

    Architecture:
    - Entry: Coder (receives all requests)
    - Coder decides when to handoff to Planner
    - Planner creates plans and hands back to Coder
    - Bidirectional communication flows
    - All agents use Mistral's API

    Args:
        model: LLM model to use (default: MISTRAL_MODEL env var or "mistral-large-latest")
        reasoning_effort: Reasoning effort level (default: "medium")
        max_handoffs: Maximum number of handoffs allowed (default: 100)
        max_turns: Max tool-calling iterations per agent. None uses 1000 (default: None)
        use_thread_pool: Run each agent in isolated thread with separate resources (default: False)
        thread_response_timeout: Timeout for thread responses in seconds (default: 600.0)
    """
    # Use shared preset to keep CLI/TUI/examples consistent
    from indusagi.presets.improved_anthropic_agency import ImprovedAgencyOptions, create_improved_agency

    model = model or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_agency_improved_prompts")
    opts = ImprovedAgencyOptions(
        model=model,
        provider="mistral",
        reasoning_effort=reasoning_effort,
        max_handoffs=max_handoffs,
        max_turns=max_turns,
        name="DevAgency_Mistral",
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
    banner_text += "[dim]Provider: Mistral[/dim]"

    console.print()
    console.print(Panel(
        banner_text,
        box=box.DOUBLE_EDGE,
        border_style="bright_cyan",
        padding=(1, 2),
        width=70,
    ))
    console.print()


def display_agency_config(agency: Agency):
    """Display current configuration."""
    config_table = Table(
        title="Agency Configuration",
        box=box.ROUNDED,
        show_header=False
    )
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="white")

    config_table.add_row("Agents:", f"{len(agency.agents)}")
    config_table.add_row("Provider:", agency.entry_agent.provider.get_provider_name())
    config_table.add_row("Model:", agency.entry_agent.config.model)
    config_table.add_row("Tools:", f"{len(registry.tools)} available")

    console.print(config_table)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run the improved agency demo."""
    print_agency_banner()

    # Create agency
    agency = create_development_agency()

    # Display config
    display_agency_config(agency)

    # Set current agency for handoff tools
    set_current_agency(agency)

    # Interactive loop
    console.print("\n[bold green]Agency ready! Type your request or 'exit' to quit.[/bold green]\n")

    while True:
        try:
            user_input = input("\n[User] > ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("\n[bold yellow]Goodbye![/bold yellow]")
                break

            if not user_input:
                continue

            response = agency.run(user_input)
            console.print(f"\n[bold blue]Assistant:[/bold blue] {response}")

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted. Goodbye![/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error: {str(e)}[/bold red]")


if __name__ == "__main__":
    main()
