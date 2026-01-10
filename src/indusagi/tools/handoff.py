"""
Handoff Tool - Enables agent-to-agent communication.

This tool allows agents to transfer control to other agents
within an Agency context.
"""
from typing import Optional, TYPE_CHECKING, List

if TYPE_CHECKING:
    from indusagi.agency import Agency
    from indusagi.tools import ToolRegistry

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
    agent_name: Optional[str] = None,
    message: str = "",
    context: Optional[str] = None,
    agent_names: Optional[List[str]] = None,
    aggregation_target: str = "Coder",
    tool_registry: Optional["ToolRegistry"] = None,
) -> str:
    """
    Hand off the current task to another agent.

    Use this tool when:
    - The task requires expertise from one or more specialized agents
    - Strategic planning is needed (handoff to PlannerAgent)
    - Implementation help is needed (handoff to CoderAgent)
    - The current agent cannot complete the task alone

    Args:
        agent_name: Name of the agent to hand off to (single)
        agent_names: List of agents to hand off to (parallel fan-out)
        message: Description of what needs to be done
        context: Additional context to provide
        aggregation_target: Agent that should aggregate parallel results (default: Coder)

    Returns:
        Confirmation message that handoff will occur
    """
    if _current_agency is None:
        return "Error: No agency context available. Handoffs require an Agency."

    # Instead of executing handoff immediately, signal that one is requested
    # The Agency.process() loop will handle the actual handoff
    from indusagi.tools import registry

    registry_ref = tool_registry or registry
    
    # Prevent nested handoffs in parallel branches
    is_parallel = hasattr(registry_ref, "_is_parallel_branch") and registry_ref._is_parallel_branch
    if is_parallel:
        # Log the blocked attempt for visibility
        from rich.console import Console
        console = Console()
        branch_name = getattr(registry_ref, '_name', 'unknown-branch')
        console.print(f"[yellow]WARNING: Blocked nested handoff from {branch_name} (parallel branches cannot handoff)[/yellow]")
        # Do NOT set _pending_handoff for parallel branches - return immediately
        return (
            "WARNING: Handoff not allowed - You are running in a parallel branch. "
            "Parallel branches cannot initiate handoffs. "
            "Complete your assigned task and return results to the aggregator agent."
        )

    # Build target list (allow single or multiple)
    targets: List[str] = []
    if agent_name:
        targets.append(agent_name)
    if agent_names:
        targets.extend(agent_names)

    # Deduplicate while preserving order
    seen = set()
    deduped_targets: List[str] = []
    for t in targets:
        if t and t not in seen:
            deduped_targets.append(t)
            seen.add(t)

    if not deduped_targets:
        return "Error: No agent specified for handoff. Provide agent_name or agent_names."

    mode = "parallel" if len(deduped_targets) > 1 else "single"

    pending: dict = {
        "mode": mode,
        "message": message,
        "context": context,
        "aggregation_target": aggregation_target,
    }

    if mode == "parallel":
        pending["agent_names"] = deduped_targets
    else:
        pending["agent_name"] = deduped_targets[0]

    # Store pending handoff information
    registry_ref._pending_handoff = pending

    # Return confirmation (the actual handoff will happen in Agency.process())
    if mode == "parallel":
        target_list = ", ".join(deduped_targets)
        return f"Parallel handoff scheduled to {target_list}. Message: {message[:100]}..."
    return f"Handoff to {deduped_targets[0]} scheduled. Message: {message[:100]}..."


def register_handoff_tool(tool_registry: "ToolRegistry") -> None:
    """
    Register the handoff_to_agent tool with a registry.

    This function should be called to enable handoff functionality in an agency.

    Args:
        tool_registry: The ToolRegistry instance to register the tool with

    Example:
        >>> from indusagi.tools import registry
        >>> from indusagi.tools.handoff import register_handoff_tool
        >>> register_handoff_tool(registry)
    """
    global _registered
    if not _registered:
        tool_registry.register(handoff_to_agent)
        _registered = True
