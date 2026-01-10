"""
Sidebar Widget for Indus CLI TUI.

Displays session metadata, tools, and quick actions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Button, Label
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.console import RenderableType


class SidebarSection(Static):
    """A section in the sidebar."""

    def __init__(self, title: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the section."""
        yield Static(self.title, classes="sidebar-section-title")
        yield Vertical(id=f"section-{self.title.lower().replace(' ', '-')}-content")


class ToolListItem(Static):
    """A tool item in the tools list."""

    def __init__(self, name: str, description: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.tool_name = name
        self.description = description

    def render(self) -> RenderableType:
        """Render the tool item."""
        text = Text()
        text.append("⚙ ", style="yellow")
        text.append(self.tool_name, style="bold")
        text.append(f"\n  {self.description[:40]}...", style="dim")
        return text


class SessionInfoWidget(Static):
    """Widget displaying session metadata."""

    def __init__(
        self,
        created_at: datetime,
        updated_at: datetime,
        token_count: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.created_at = created_at
        self.updated_at = updated_at
        self.token_count = token_count

    def render(self) -> RenderableType:
        """Render session info."""
        text = Text()

        # Created
        text.append("Created: ", style="dim")
        text.append(self.created_at.strftime("%Y-%m-%d %H:%M"), style="")
        text.append("\n")

        # Updated
        text.append("Updated: ", style="dim")
        text.append(self.updated_at.strftime("%Y-%m-%d %H:%M"), style="")
        text.append("\n")

        # Token count
        text.append("Tokens: ", style="dim")
        text.append(f"~{self.token_count:,}", style="cyan")

        return text


class Sidebar(Static):
    """
    Sidebar widget for session screen.

    Shows:
    - Session info (created, updated, tokens)
    - Available tools
    - Quick actions
    - Keyboard shortcuts
    """

    DEFAULT_CSS = """
    Sidebar {
        width: 30;
        height: 100%;
        background: #141414;
        border-left: solid #333333;
        padding: 1;
    }

    .sidebar-section-title {
        text-style: bold;
        color: #808080;
        border-bottom: solid #262626;
        padding-bottom: 1;
        margin-bottom: 1;
    }

    .sidebar-section {
        margin-bottom: 2;
    }

    .quick-action-btn {
        width: 100%;
        margin-bottom: 1;
    }

    .shortcut-item {
        margin-bottom: 0;
    }
    """

    is_visible: reactive[bool] = reactive(True)

    def compose(self) -> ComposeResult:
        """Compose the sidebar."""
        with Vertical(id="sidebar-content"):
            # Session Info
            yield Static("Session Info", classes="sidebar-section-title")
            yield Static(id="session-info-placeholder")

            # Tools Section
            yield Static("Available Tools", classes="sidebar-section-title")
            yield Vertical(id="tools-list")

            # Quick Actions
            yield Static("Quick Actions", classes="sidebar-section-title")
            yield Button("New Session", id="btn-new", classes="quick-action-btn")
            yield Button("Clear Chat", id="btn-clear", classes="quick-action-btn")
            yield Button("Export", id="btn-export", classes="quick-action-btn")

            # Shortcuts
            yield Static("Shortcuts", classes="sidebar-section-title")
            yield Static(self._render_shortcuts(), id="shortcuts-list")

    def _render_shortcuts(self) -> RenderableType:
        """Render keyboard shortcuts."""
        shortcuts = [
            ("Ctrl+P", "Command Palette"),
            ("Ctrl+N", "New Session"),
            ("Ctrl+S", "Sessions"),
            ("Ctrl+M", "Select Model"),
            ("Ctrl+L", "Clear Messages"),
            ("Escape", "Back to Home"),
            ("F1", "Help"),
        ]

        text = Text()
        for key, desc in shortcuts:
            text.append(f"{key:12}", style="cyan")
            text.append(f" {desc}\n", style="dim")

        return text

    def on_mount(self) -> None:
        """Called when sidebar is mounted."""
        self._refresh_tools()

    def _refresh_tools(self) -> None:
        """Refresh the tools list."""
        tools_list = self.query_one("#tools-list", Vertical)
        tools_list.remove_children()

        # Get tools from app
        try:
            from indusagi.tools import registry
            for name in registry.list_tools()[:5]:  # Show first 5
                info = registry.get_tool_info(name)
                if info:
                    desc = info.get("description", "No description")[:40]
                    item = ToolListItem(name, desc)
                    tools_list.mount(item)

            if len(registry.list_tools()) > 5:
                more = Static(f"  +{len(registry.list_tools()) - 5} more...", classes="dim")
                tools_list.mount(more)
        except Exception:
            tools_list.mount(Static("Unable to load tools", classes="dim"))

    def update_session_info(
        self,
        created_at: datetime,
        updated_at: datetime,
        token_count: int = 0,
    ) -> None:
        """Update session info display."""
        placeholder = self.query_one("#session-info-placeholder", Static)
        info_widget = SessionInfoWidget(
            created_at=created_at,
            updated_at=updated_at,
            token_count=token_count,
        )
        placeholder.update(info_widget.render())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-new":
            self.app.action_new_session()
        elif event.button.id == "btn-clear":
            # Clear current session messages
            session = self.app.get_current_session()
            if session:
                self.app.messages[session.id] = []
                session.message_count = 0
                self.app.notify("Chat cleared")
        elif event.button.id == "btn-export":
            self.app.notify("Export: Coming soon!")
