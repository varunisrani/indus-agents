"""SendMessageHandoff tool for inter-agent communication."""

from typing import Optional, ClassVar, Dict, Any, TYPE_CHECKING, List
from pydantic import Field
from .base import BaseTool

if TYPE_CHECKING:
    from ..agency import Agency

# Global state for agency context and call stack
_current_agency: Optional["Agency"] = None
_agent_call_stack: List[str] = []


def set_current_agency(agency: "Agency") -> None:
    """
    Set the current agency context for handoff operations.

    Args:
        agency: The Agency instance to use for handoffs
    """
    global _current_agency
    _current_agency = agency


def get_current_agency() -> Optional["Agency"]:
    """
    Get the current agency context.

    Returns:
        Current Agency instance or None
    """
    return _current_agency


def clear_current_agency() -> None:
    """Clear the current agency context."""
    global _current_agency, _agent_call_stack
    _current_agency = None
    _agent_call_stack = []


def push_agent(agent_name: str) -> None:
    """
    Push an agent onto the call stack.

    Args:
        agent_name: Name of the agent to push
    """
    _agent_call_stack.append(agent_name)


def pop_agent() -> Optional[str]:
    """
    Pop an agent from the call stack.

    Returns:
        Name of the popped agent or None if stack is empty
    """
    return _agent_call_stack.pop() if _agent_call_stack else None


def get_current_agent() -> Optional[str]:
    """
    Get the current agent (top of call stack).

    Returns:
        Name of current agent or None if stack is empty
    """
    return _agent_call_stack[-1] if _agent_call_stack else None


def get_call_stack() -> List[str]:
    """
    Get a copy of the current call stack.

    Returns:
        List of agent names in call order
    """
    return _agent_call_stack.copy()


class SendMessageHandoff(BaseTool):
    """
    Hand off a task to another agent in the agency.

    Use this tool when you need specialized expertise from another agent
    or want to delegate a subtask. The target agent must be in your
    allowed communication flows.

    Example:
        To get research help:
        >>> tool = SendMessageHandoff(
        ...     to_agent="ResearchAgent",
        ...     message="Research the latest Python testing frameworks"
        ... )
    """

    name: ClassVar[str] = "send_message_handoff"
    description: ClassVar[str] = """Hand off a task to another agent in the agency.
    Use when you need specialized expertise or want to delegate a subtask.
    The target agent must be in your allowed communication flows."""

    to_agent: str = Field(
        ...,
        description="Name of the agent to hand off to (must be in allowed flows)"
    )
    message: str = Field(
        ...,
        description="The task or message for the target agent. Be specific about what you need."
    )
    context_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context data to pass to the target agent"
    )

    def execute(self) -> str:
        """
        Execute the handoff to another agent.

        Returns:
            Response from the target agent or error message
        """
        global _current_agency

        if _current_agency is None:
            return "Error: No agency context available. Cannot perform handoff."

        # Determine current agent
        current_agent_name = get_current_agent()
        if not current_agent_name:
            # Fall back to entry agent if no agent is on the stack
            current_agent_name = _current_agency.entry_agent.name

        # Get the current agent object
        current_agent = _current_agency.get_agent(current_agent_name)
        if not current_agent:
            return f"Error: Current agent '{current_agent_name}' not found in agency"

        # Check if handoff is allowed
        if not _current_agency.can_handoff(current_agent_name, self.to_agent):
            allowed = _current_agency.get_allowed_handoffs(current_agent_name)
            if allowed:
                return (
                    f"Error: Cannot hand off from {current_agent_name} to {self.to_agent}. "
                    f"Allowed targets: {', '.join(allowed)}"
                )
            else:
                return (
                    f"Error: {current_agent_name} has no allowed handoff targets. "
                    "Check your communication_flows configuration."
                )

        # Push target agent onto call stack before handoff
        push_agent(self.to_agent)

        try:
            # Execute the handoff
            result = _current_agency.handoff(
                from_agent=current_agent,
                to_agent_name=self.to_agent,
                message=self.message,
                context=self.context_data
            )

            if result.success:
                return f"[Response from {self.to_agent}]\n\n{result.response}"
            else:
                return f"Handoff failed: {result.error}"

        finally:
            # Pop target agent from call stack after handoff completes
            pop_agent()


class SendMessageToCoordinator(BaseTool):
    """
    Send a message back to the coordinator/entry agent.

    Use this when a subtask is complete and you need to report back
    to the main coordinating agent.
    """

    name: ClassVar[str] = "send_message_to_coordinator"
    description: ClassVar[str] = """Send a message back to the coordinator/entry agent.
    Use when reporting results or when a subtask is complete."""

    message: str = Field(
        ...,
        description="The message or results to send to the coordinator"
    )
    task_completed: bool = Field(
        default=True,
        description="Whether the assigned task has been completed"
    )

    def execute(self) -> str:
        """
        Execute the message to coordinator.

        Returns:
            Confirmation of message sent
        """
        global _current_agency

        if _current_agency is None:
            return "Error: No agency context available."

        coordinator_name = _current_agency.entry_agent.name
        current_agent = get_current_agent()

        status = "completed" if self.task_completed else "in progress"

        return (
            f"[Message to {coordinator_name}]\n"
            f"From: {current_agent or 'unknown'}\n"
            f"Status: Task {status}\n\n"
            f"{self.message}"
        )


# Convenience function to create handoff tool dynamically
def create_handoff_tool(allowed_targets: List[str]) -> type:
    """
    Create a customized handoff tool with constrained targets.

    Args:
        allowed_targets: List of agent names that can be handed off to

    Returns:
        Customized SendMessageHandoff class
    """
    targets_str = ", ".join(allowed_targets)

    class ConstrainedHandoff(SendMessageHandoff):
        description: ClassVar[str] = f"""Hand off a task to another agent.
        Allowed targets: {targets_str}"""

        def execute(self) -> str:
            if self.to_agent not in allowed_targets:
                return f"Error: Can only hand off to: {targets_str}"
            return super().execute()

    return ConstrainedHandoff
