"""
Shared "Improved Agency" preset (Coder <-> Planner) for Anthropic-compatible providers.

This module exists to keep the agency wiring consistent across:
- example scripts (e.g. example_agency_improved_anthropic.py)
- the TUI (src/indusagi/tui/...)
- the packaged CLI entrypoint (src/indusagi/cli.py)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from indusagi import Agent, AgentConfig, Agency
from indusagi.tools import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from indusagi.tools import set_current_agency, registry


@dataclass(frozen=True)
class ImprovedAgencyOptions:
    model: str = "glm-4.7"
    provider: str = "anthropic"
    reasoning_effort: str = "medium"  # kept for API compatibility with examples (not used currently)
    max_handoffs: int = 100
    max_turns: Optional[int] = None  # None lets Agency default; examples typically use 1000
    name: str = "DevAgency_Anthropic"
    coder_prompt_file: Optional[str] = None
    planner_prompt_file: Optional[str] = None
    critic_prompt_file: Optional[str] = None
    use_thread_pool: bool = False
    thread_response_timeout: float = 600.0


def _register_default_tools() -> None:
    """Register default tools in the global registry (idempotent)."""
    for tool_class in [Bash, Read, Edit, Write, Glob, Grep, TodoWrite]:
        try:
            registry.register(tool_class)
        except Exception:
            # Tool might already be registered
            pass


def _handoff_schema() -> dict:
    """Tool schema for handoff_to_agent (used by Agency.process tool-calling)."""
    return {
        "type": "function",
        "function": {
            "name": "handoff_to_agent",
            "description": (
                "Hand off the current task to another agent in the agency. "
                "Use `agent_name` for single handoff or `agent_names` for parallel fan-out. "
                "Results from parallel branches will be aggregated by the Coder (default) unless "
                "aggregation_target is specified."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to hand off to (e.g., 'Planner', 'Coder')",
                    },
                    "agent_names": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": "List of agents to hand off to in parallel (e.g., ['Planner', 'Critic'])",
                    },
                    "message": {
                        "type": "string",
                        "description": "Message or task description for the target agent",
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context or additional information",
                    },
                    "aggregation_target": {
                        "type": "string",
                        "description": "Agent to aggregate parallel results (default: 'Coder')",
                    },
                },
                "required": ["message"],
            },
        },
    }


def create_improved_agency(opts: ImprovedAgencyOptions = ImprovedAgencyOptions()) -> Agency:
    """
    Create the improved Coder <-> Planner (+ Critic) agency (same architecture as example scripts).

    Notes:
    - Prompt files are optional. If not provided / not found, Agent falls back to its default prompt.
    - Tools are registered globally via indusagi.tools.registry.
    """
    _register_default_tools()

    coder = Agent(
        name="Coder",
        role="Code implementation and execution",
        config=AgentConfig(
            model=opts.model,
            provider=opts.provider,
            temperature=1,
            max_tokens=8000,
        ),
        prompt_file=opts.coder_prompt_file,
    )
    coder.context = registry.context

    planner = Agent(
        name="Planner",
        role="Strategic planning and task breakdown specialist",
        config=AgentConfig(
            model=opts.model,
            provider=opts.provider,
            temperature=1,
            max_tokens=16000,
        ),
        prompt_file=opts.planner_prompt_file,
    )
    planner.context = registry.context

    critic = Agent(
        name="Critic",
        role="Risk and quality reviewer (edge cases, failure modes, test ideas)",
        config=AgentConfig(
            model=opts.model,
            provider=opts.provider,
            temperature=1,
            max_tokens=8000,
        ),
        prompt_file=opts.critic_prompt_file,
    )
    critic.context = registry.context

    tools = registry.schemas.copy()
    tools.append(_handoff_schema())

    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner, critic],
        communication_flows=[
            (coder, planner), (planner, coder),
            (coder, critic), (critic, coder),
            (planner, critic), (critic, planner),
        ],
        shared_instructions=None,
        name=opts.name,
        max_handoffs=opts.max_handoffs,
        max_turns=opts.max_turns,
        tools=tools,
        tool_executor=registry,
        use_thread_pool=opts.use_thread_pool,
        thread_response_timeout=opts.thread_response_timeout,
    )

    set_current_agency(agency)
    return agency

