"""Lifecycle hooks for agent execution."""

from abc import ABC
from typing import Any, Optional, List, Dict

class AgentHooks(ABC):
    """
    Base class for agent lifecycle hooks.

    Hooks are called at various points during agent processing,
    allowing for customization of behavior, logging, and monitoring.
    """

    async def on_start(self, context: Any, agent: Any) -> None:
        """Called when agent starts processing."""
        pass

    async def on_end(self, context: Any, agent: Any, output: str) -> None:
        """Called when agent finishes processing."""
        pass

    async def on_tool_start(self, context: Any, agent: Any, tool: Any) -> None:
        """Called before tool execution."""
        pass

    async def on_tool_end(self, context: Any, agent: Any, tool: Any, result: str) -> None:
        """Called after tool execution."""
        pass

    async def on_llm_start(self, context: Any, agent: Any, messages: List[Dict]) -> None:
        """Called before LLM inference."""
        pass

    async def on_llm_end(self, context: Any, agent: Any, response: Any) -> None:
        """Called after LLM response."""
        pass

    async def on_handoff(self, context: Any, agent: Any, source_agent: str) -> None:
        """Called when agent receives a handoff."""
        pass


class SystemReminderHook(AgentHooks):
    """
    Injects periodic reminders about critical instructions.

    This hook monitors tool call counts and injects reminders
    at specified intervals to reinforce important guidelines.
    """

    def __init__(self, tool_call_interval: int = 15):
        """
        Initialize the reminder hook.

        Args:
            tool_call_interval: Number of tool calls between reminders
        """
        self.tool_call_count = 0
        self.tool_call_interval = tool_call_interval
        self.pending_reminder: Optional[str] = None

    async def on_tool_end(self, context: Any, agent: Any, tool: Any, result: str) -> None:
        """Track tool calls and inject reminders when interval is reached."""
        self.tool_call_count += 1
        if self.tool_call_count >= self.tool_call_interval:
            self._inject_reminder()
            self.tool_call_count = 0

    def _inject_reminder(self) -> None:
        """Set the pending reminder content."""
        self.pending_reminder = """<system-reminder>
- Read file before Edit (safety requirement)
- Use TodoWrite for task tracking
- Mark todos as in_progress before execution
- Complete tasks one at a time
</system-reminder>"""

    def get_and_clear_reminder(self) -> Optional[str]:
        """Get pending reminder and clear it."""
        reminder = self.pending_reminder
        self.pending_reminder = None
        return reminder

    def reset(self) -> None:
        """Reset the hook state."""
        self.tool_call_count = 0
        self.pending_reminder = None


class ToolLoggingHook(AgentHooks):
    """Hook that logs all tool usage for debugging and monitoring."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.tool_history: List[Dict] = []

    async def on_tool_start(self, context: Any, agent: Any, tool: Any) -> None:
        """Log tool start."""
        tool_name = getattr(tool, 'name', str(tool))
        if self.verbose:
            print(f"[{agent.name if hasattr(agent, 'name') else 'Agent'}] Starting: {tool_name}")

    async def on_tool_end(self, context: Any, agent: Any, tool: Any, result: str) -> None:
        """Log tool completion and record in history."""
        tool_name = getattr(tool, 'name', str(tool))
        self.tool_history.append({
            "tool": tool_name,
            "result_preview": result[:200] if len(result) > 200 else result,
            "success": "error" not in result.lower()
        })
        if self.verbose:
            status = "✓" if "error" not in result.lower() else "✗"
            print(f"[{agent.name if hasattr(agent, 'name') else 'Agent'}] Completed: {tool_name} [{status}]")


def create_system_reminder_hook(interval: int = 15) -> SystemReminderHook:
    """
    Factory for creating system reminder hooks.

    Args:
        interval: Number of tool calls between reminders

    Returns:
        Configured SystemReminderHook instance
    """
    return SystemReminderHook(tool_call_interval=interval)


def create_logging_hook(verbose: bool = True) -> ToolLoggingHook:
    """
    Factory for creating tool logging hooks.

    Args:
        verbose: Whether to print tool usage

    Returns:
        Configured ToolLoggingHook instance
    """
    return ToolLoggingHook(verbose=verbose)
