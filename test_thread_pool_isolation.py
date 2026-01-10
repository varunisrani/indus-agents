"""
Unit tests to verify thread-pool isolation for agents.

These tests avoid hitting real LLM providers by using lightweight dummy agents.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from indusagi.agency import Agency


@dataclass
class DummyProvider:
    """Minimal provider stub for testing."""

    def get_provider_name(self) -> str:
        return "dummy-provider"


class DummyAgent:
    """Minimal agent stub compatible with Agency for testing purposes."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.role = "dummy"
        self.provider = DummyProvider()
        self.config = type("Config", (), {"model": "dummy-model"})
        self.context = None

    def process_with_tools(
        self,
        message: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Any] = None,
        max_turns: Optional[int] = None,
        on_max_turns_reached: Optional[Any] = None,
        event_callback: Optional[Any] = None,
    ) -> str:
        return f"{self.name} processed: {message}"

    def process(self, message: str) -> str:
        return f"{self.name} processed: {message}"


def test_thread_pool_creates_isolated_agents():
    """Ensure each agent gets its own tool registry/context in thread-pool mode."""
    coder = DummyAgent("Coder")
    planner = DummyAgent("Planner")
    critic = DummyAgent("Critic")

    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner, critic],
        communication_flows=[(coder, planner), (planner, coder), (coder, critic)],
        use_thread_pool=True,
        tools=[],
        tool_executor=None,
    )

    assert agency.handoff_queue is not None
    assert set(agency._isolated_agents.keys()) == {"Coder", "Planner", "Critic"}

    registries = [iso.tool_registry for iso in agency._isolated_agents.values()]
    # Each isolated agent should have its own ToolRegistry/context instance.
    assert len({id(reg) for reg in registries}) == 3
    assert len({id(reg.context) for reg in registries}) == 3

    # Run a simple request and ensure it completes without handoffs.
    result = agency.process("hello", use_tools=True, tools=[], tool_executor=None)
    assert "Coder processed: hello" in result.response
    assert result.final_agent == "Coder"

    agency.shutdown()
