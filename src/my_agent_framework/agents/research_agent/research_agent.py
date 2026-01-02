"""
Research Agent Factory

A specialized agent for research and information gathering tasks.
"""

import os
from typing import Optional
from my_agent_framework.agent import Agent, AgentConfig
from my_agent_framework.shared.agent_utils import (
    render_instructions,
    select_instructions_file,
    create_model_settings,
)
from my_agent_framework.shared.system_hooks import create_system_reminder_hook

current_dir = os.path.dirname(os.path.abspath(__file__))


def create_research_agent(
    model: str = "gpt-4o",
    reasoning_effort: str = "medium",
    config: Optional[AgentConfig] = None,
    enable_hooks: bool = True,
) -> Agent:
    """
    Factory function for Research Agent.

    Args:
        model: Model to use
        reasoning_effort: Reasoning effort level
        config: Optional AgentConfig override
        enable_hooks: Whether to enable lifecycle hooks

    Returns:
        Configured Research Agent instance
    """
    instructions_file = select_instructions_file(current_dir, model)
    instructions = render_instructions(instructions_file, model)

    agent_config = config or AgentConfig.from_env()
    agent_config.model = model

    model_settings = create_model_settings(model, reasoning_effort)
    hooks = create_system_reminder_hook() if enable_hooks else None

    return Agent(
        name="ResearchAgent",
        role="Research and information gathering specialist",
        config=agent_config,
        system_prompt=instructions,
        hooks=hooks,
        model_settings=model_settings,
    )


ResearchAgent = create_research_agent
