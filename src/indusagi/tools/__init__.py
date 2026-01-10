"""
Tools Package - Base tool classes and development tools.
"""
from typing import Dict, List, Any, Optional
import threading

from .base import BaseTool, ToolContext, get_tool_context
from .dev import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from .handoff import handoff_to_agent, set_current_agency, get_current_agency, register_handoff_tool


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self):
        self._tools: Dict[str, type[BaseTool]] = {}
        self.context = get_tool_context()  # Shared context for all tools
        self._pending_handoff: Dict[str, Any] | None = None  # For agency handoffs
        self._write_lock = threading.RLock()
        self._mutating_tools = {"edit", "write"}
        self._name = "root"
        self._is_parallel_branch = False  # Flag to prevent nested handoffs in parallel branches

    def register(self, tool_class: type[BaseTool]) -> None:
        """Register a tool class."""
        self._tools[tool_class.name] = tool_class

    def _clone_context(self) -> ToolContext:
        """Clone tool context when forking registries."""
        if hasattr(self.context, "clone"):
            return self.context.clone()  # type: ignore[no-any-return]
        return self.context

    def fork(self, name: Optional[str] = None, is_parallel_branch: bool = True) -> "ToolRegistry":
        """
        Create a forked registry with shared tool definitions but isolated state.

        - Shares _tools so schemas stay consistent.
        - Clones context and pending handoff to avoid race conditions.
        - Shares a write lock to serialize mutating tools across branches.
        - Marks as parallel branch to prevent nested handoffs.
        """
        clone = ToolRegistry()
        clone._tools = self._tools  # share definitions
        clone.context = self._clone_context()
        clone._pending_handoff = None
        clone._write_lock = self._write_lock  # serialize writes globally
        clone._mutating_tools = self._mutating_tools
        clone._name = name or f"{self._name}-fork"
        clone._is_parallel_branch = is_parallel_branch  # Mark as parallel branch
        return clone

    def execute(self, name: str, **kwargs) -> str:
        """Execute a tool by name with given arguments."""
        if name not in self._tools:
            # Check if it's the handoff tool
            if name == "handoff_to_agent":
                return handoff_to_agent(tool_registry=self, **kwargs)
            raise ValueError(f"Tool '{name}' not found in registry")

        tool_class = self._tools[name]
        tool_instance = tool_class(**kwargs)
        # Attach context override so branches can run in isolation
        setattr(tool_instance, "_context", self.context)

        if tool_class.name in self._mutating_tools:
            with self._write_lock:
                return tool_instance.execute()
        return tool_instance.execute()

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for OpenAI function calling."""
        schemas = []
        for tool_class in self._tools.values():
            schemas.append(tool_class.get_schema())
        return schemas

    def get_tool_names(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())


# Global registry instance
registry = ToolRegistry()

__all__ = [
    # Base classes
    "BaseTool",
    "ToolContext",
    "get_tool_context",
    # Development tools
    "Bash",
    "Read",
    "Edit",
    "Write",
    "Glob",
    "Grep",
    "TodoWrite",
    # Handoff tools
    "handoff_to_agent",
    "set_current_agency",
    "get_current_agency",
    "register_handoff_tool",
    # Compatibility exports (to be implemented)
    "registry",
    "ToolRegistry",
]
