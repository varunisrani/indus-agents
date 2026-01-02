"""
Handoff Tool - Enables agent-to-agent communication.

This tool allows agents to transfer control to other agents
within an Agency context.
"""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from my_agent_framework.agency import Agency
    from my_agent_framework.tools import ToolRegistry

# Global agency reference (set at runtime)
_current_agency: Optional["Agency"] = None
_registered: bool = False


def set_current_agency(agency: "Agency") -> None:
    """Set the current agency context for handoff tools."""
    global _current_agency
    _current_agency = agency


def get_current_agency() -> Optional["Agency"]:
    """Get the current agency context."""
    return _current_agency


def handoff_to_agent(
    agent_name: str,
    message: str,
    context: Optional[str] = None
) -> str:
    """
    Hand off the current task to another agent.

    Use this tool when:
    - The task requires expertise from a specialized agent
    - Strategic planning is needed (handoff to PlannerAgent)
    - Implementation help is needed (handoff to CoderAgent)
    - The current agent cannot complete the task alone

    Args:
        agent_name: Name of the agent to hand off to
        message: Description of what needs to be done
        context: Additional context to provide

    Returns:
        The target agent's response
    """
    if _current_agency is None:
        return "Error: No agency context available. Handoffs require an Agency."

    # Find current agent (the one calling this tool)
    # This is a simplification - in practice, would need to track this
    current = _current_agency.entry_agent

    if not _current_agency.can_handoff(current.name, agent_name):
        allowed = _current_agency.get_allowed_handoffs(current.name)
        return f"Error: Cannot handoff to {agent_name}. Allowed: {allowed}"

    result = _current_agency.handoff(
        from_agent=current,
        to_agent_name=agent_name,
        message=message,
        context={"additional_context": context} if context else None
    )

    if result.success:
        return result.response
    else:
        return f"Handoff failed: {result.error}"


def register_handoff_tool(tool_registry: "ToolRegistry") -> None:
    """
    Register the handoff_to_agent tool with a registry.

    This function should be called to enable handoff functionality in an agency.

    Args:
        tool_registry: The ToolRegistry instance to register the tool with

    Example:
        >>> from my_agent_framework.tools import registry
        >>> from my_agent_framework.tools.handoff import register_handoff_tool
        >>> register_handoff_tool(registry)
    """
    global _registered
    if not _registered:
        tool_registry.register(handoff_to_agent)
        _registered = True
