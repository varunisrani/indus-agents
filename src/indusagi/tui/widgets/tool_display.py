"""
Tool Display Widget for Indus CLI TUI.

Displays tool execution with status, arguments, and results.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
from rich.console import RenderableType
import json


class ToolDisplay(Static):
    """
    Widget for displaying tool execution.

    Shows:
    - Tool name and icon
    - Execution status (running, success, error)
    - Arguments (formatted)
    - Result/output
    - Duration
    """

    DEFAULT_CSS = """
    ToolDisplay {
        padding: 1;
        margin: 0 1 1 1;
        background: #1a1a1a;
        border-left: tall #e5c07b;
    }

    ToolDisplay.running {
        border-left: tall #8be9fd;
    }

    ToolDisplay.success {
        border-left: tall #50fa7b;
    }

    ToolDisplay.error {
        border-left: tall #ff5555;
    }
    """

    # Tool icons mapping
    TOOL_ICONS = {
        "calculator": "🧮",
        "get_time": "🕐",
        "get_date": "📅",
        "get_datetime": "📆",
        "text_uppercase": "🔤",
        "text_lowercase": "🔡",
        "text_reverse": "🔄",
        "text_title_case": "📝",
        "text_count_words": "🔢",
        "bash": "💻",
        "read": "📖",
        "write": "✍️",
        "edit": "✏️",
        "glob": "🔍",
        "grep": "🔎",
        "web_fetch": "🌐",
    }

    # Reactive state
    status: reactive[str] = reactive("running")  # running, success, error
    result: reactive[Optional[str]] = reactive(None)

    def __init__(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        status: str = "running",
        result: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tool_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.arguments = arguments
        self.status = status
        self.result = result
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.tool_id = tool_id

        # Set initial CSS class
        self.add_class(status)

    def render(self) -> RenderableType:
        """Render the tool display."""
        text = Text()

        # Status icon
        status_icons = {
            "running": ("⏳", "yellow"),
            "success": ("✓", "green"),
            "error": ("✗", "red"),
        }
        icon, style = status_icons.get(self.status, ("●", "white"))

        # Tool icon
        tool_icon = self.TOOL_ICONS.get(self.tool_name, "⚙")

        # Header
        text.append(f"{icon} ", style=style)
        text.append(f"{tool_icon} ", style="")
        text.append(self.tool_name, style="bold yellow")

        # Duration
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).total_seconds()
            text.append(f" ({duration:.2f}s)", style="dim")
        elif self.status == "running":
            text.append(" ...", style="dim italic")

        # Arguments
        if self.arguments:
            text.append("\n  ")
            args_str = self._format_arguments()
            text.append(args_str, style="dim cyan")

        # Result
        if self.result is not None:
            text.append("\n  → ", style="dim")
            result_style = "green" if self.status == "success" else "red"
            result_preview = self._format_result()
            text.append(result_preview, style=result_style)

        return text

    def _format_arguments(self) -> str:
        """Format arguments for display."""
        parts = []
        for key, value in self.arguments.items():
            # Truncate long values
            str_value = str(value)
            if len(str_value) > 50:
                str_value = str_value[:47] + "..."
            parts.append(f"{key}={repr(str_value)}")

        return ", ".join(parts)

    def _format_result(self) -> str:
        """Format result for display."""
        if self.result is None:
            return ""

        result = self.result

        # Truncate long results
        if len(result) > 200:
            result = result[:197] + "..."

        # Replace newlines for single-line display
        result = result.replace("\n", " ⏎ ")

        return result

    def set_running(self) -> None:
        """Set status to running."""
        self.status = "running"
        self.start_time = datetime.now()
        self._update_classes()

    def set_success(self, result: str) -> None:
        """Set status to success with result."""
        self.status = "success"
        self.result = result
        self.end_time = datetime.now()
        self._update_classes()

    def set_error(self, error: str) -> None:
        """Set status to error."""
        self.status = "error"
        self.result = error
        self.end_time = datetime.now()
        self._update_classes()

    def _update_classes(self) -> None:
        """Update CSS classes based on status."""
        self.remove_class("running", "success", "error")
        self.add_class(self.status)

    def watch_status(self, value: str) -> None:
        """React to status changes."""
        self._update_classes()
        self.refresh()

    def watch_result(self, value: Optional[str]) -> None:
        """React to result changes."""
        self.refresh()


class ToolExecutionLog(Static):
    """
    A log of tool executions.

    Shows a list of recent tool executions with their status.
    """

    DEFAULT_CSS = """
    ToolExecutionLog {
        height: auto;
        max-height: 20;
        padding: 1;
        background: #141414;
        border: solid #333333;
    }

    .tool-log-title {
        text-style: bold;
        color: #808080;
        margin-bottom: 1;
    }

    .tool-log-empty {
        color: #808080;
        text-align: center;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tools: Dict[str, ToolDisplay] = {}

    def compose(self):
        """Compose the log."""
        yield Static("Tool Executions", classes="tool-log-title")
        yield Static("No tools executed yet", id="empty-state", classes="tool-log-empty")

    def add_tool(
        self,
        tool_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> ToolDisplay:
        """Add a tool execution to the log."""
        # Hide empty state
        try:
            empty = self.query_one("#empty-state")
            empty.display = False
        except Exception:
            pass

        # Create tool display
        tool = ToolDisplay(
            tool_name=tool_name,
            arguments=arguments,
            status="running",
            tool_id=tool_id,
        )

        self._tools[tool_id] = tool
        self.mount(tool)

        return tool

    def update_tool(self, tool_id: str, status: str, result: Optional[str] = None) -> bool:
        """Update a tool's status."""
        if tool_id not in self._tools:
            return False

        tool = self._tools[tool_id]
        if status == "success":
            tool.set_success(result or "")
        elif status == "error":
            tool.set_error(result or "Unknown error")

        return True

    def clear(self) -> None:
        """Clear all tool executions."""
        for tool in self._tools.values():
            tool.remove()
        self._tools.clear()

        # Show empty state
        try:
            empty = self.query_one("#empty-state")
            empty.display = True
        except Exception:
            pass
