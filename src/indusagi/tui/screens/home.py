"""
Home Screen for Indus CLI TUI.

The welcome screen with session list and new session button.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, Center
from textual.widgets import Static, Button, Label, ListView, ListItem
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.console import RenderableType


# ============================================================================
# Session List Item
# ============================================================================

class SessionItem(ListItem):
    """A session item in the session list."""

    def __init__(
        self,
        session_id: str,
        name: str,
        model: str,
        message_count: int,
        updated_at: datetime,
        is_active: bool = False,
    ) -> None:
        super().__init__()
        self.session_id = session_id
        self.session_name = name
        self.model = model
        self.message_count = message_count
        self.updated_at = updated_at
        self._is_active = is_active

    def compose(self) -> ComposeResult:
        """Compose the session item."""
        yield Static(self._render_item(), classes="session-item-content")

    def _render_item(self) -> RenderableType:
        """Render the session item."""
        # Time formatting
        now = datetime.now()
        diff = now - self.updated_at
        if diff.days > 0:
            time_str = f"{diff.days}d ago"
        elif diff.seconds > 3600:
            time_str = f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            time_str = f"{diff.seconds // 60}m ago"
        else:
            time_str = "just now"

        # Build text
        text = Text()
        if self._is_active:
            text.append("● ", style="green bold")
        text.append(self.session_name, style="bold")
        text.append(f"  {self.model}", style="dim cyan")
        text.append(f"  {self.message_count} msgs", style="dim")
        text.append(f"  {time_str}", style="dim italic")

        return text


# ============================================================================
# Logo Widget
# ============================================================================

class Logo(Static):
    """Animated logo widget."""

    LOGO = """
╔═══════════════════════════════════════════╗
║                                           ║
║   ██╗███╗   ██╗██████╗ ██╗   ██╗███████╗  ║
║   ██║████╗  ██║██╔══██╗██║   ██║██╔════╝  ║
║   ██║██╔██╗ ██║██║  ██║██║   ██║███████╗  ║
║   ██║██║╚██╗██║██║  ██║██║   ██║╚════██║  ║
║   ██║██║ ╚████║██████╔╝╚██████╔╝███████║  ║
║   ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚══════╝  ║
║                                           ║
║              CLI  Agent  Interface        ║
║                                           ║
╚═══════════════════════════════════════════╝
"""

    def render(self) -> RenderableType:
        """Render the logo."""
        return Text(self.LOGO, style="bold cyan")


# ============================================================================
# Home Screen
# ============================================================================

class HomeScreen(Screen):
    """
    Home screen for Indus CLI.

    Shows:
    - Logo and welcome message
    - Recent sessions list
    - New session button
    - Quick actions
    """

    BINDINGS = [
        ("n", "new_session", "New Session"),
        ("enter", "select_session", "Open Session"),
        ("d", "delete_session", "Delete"),
        ("r", "rename_session", "Rename"),
    ]

    CSS = """
    HomeScreen {
        align: center middle;
        background: #0d0d0d;
    }

    #home-container {
        width: 80;
        height: auto;
        max-height: 90%;
        padding: 2;
        background: #141414;
        border: solid #333333;
    }

    #logo-container {
        align: center top;
        height: auto;
        margin-bottom: 1;
    }

    #tagline {
        text-align: center;
        color: #888888;
        margin-bottom: 2;
    }

    #actions-container {
        align: center middle;
        height: auto;
        margin-bottom: 2;
    }

    #sessions-container {
        height: auto;
        max-height: 50%;
        margin-top: 1;
        padding: 1;
        background: #1a1a1a;
        border: solid #333333;
    }

    #sessions-title {
        text-style: bold;
        color: #fab283;
        margin-bottom: 1;
    }

    #session-list {
        height: auto;
        max-height: 20;
        background: #1a1a1a;
    }

    #empty-state {
        text-align: center;
        color: #666666;
        padding: 2;
    }

    .action-button {
        margin: 0 1;
    }

    Button {
        min-width: 16;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the home screen."""
        with Container(id="home-container"):
            # Logo
            with Center(id="logo-container"):
                yield Logo()

            # Tagline
            yield Static(
                "Your AI-powered terminal companion",
                id="tagline",
            )

            # Action buttons
            with Center(id="actions-container"):
                with Horizontal():
                    yield Button(
                        "New Session",
                        id="btn-new-session",
                        variant="primary",
                        classes="action-button",
                    )
                    yield Button(
                        "Settings",
                        id="btn-settings",
                        classes="action-button",
                    )
                    yield Button(
                        "Help",
                        id="btn-help",
                        classes="action-button",
                    )

            # Recent sessions
            with Vertical(id="sessions-container"):
                yield Static("Recent Sessions", id="sessions-title")
                yield ListView(id="session-list")
                yield Static(
                    "No sessions yet. Press 'n' or click 'New Session' to start.",
                    id="empty-state",
                )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._refresh_sessions()

    def on_screen_resume(self) -> None:
        """Called when screen is resumed."""
        self._refresh_sessions()

    def _refresh_sessions(self) -> None:
        """Refresh the session list."""
        list_view = self.query_one("#session-list", ListView)
        list_view.clear()

        # Get sessions from app
        app = self.app
        sessions = list(app.sessions.values())

        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        # Show/hide empty state
        empty_state = self.query_one("#empty-state", Static)
        if sessions:
            empty_state.display = False
            list_view.display = True

            # Add session items
            for session in sessions[:10]:  # Show last 10
                item = SessionItem(
                    session_id=session.id,
                    name=session.name,
                    model=session.model,
                    message_count=session.message_count,
                    updated_at=session.updated_at,
                    is_active=(session.id == app.current_session_id),
                )
                list_view.append(item)
        else:
            empty_state.display = True
            list_view.display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-new-session":
            self.action_new_session()
        elif event.button.id == "btn-settings":
            self.app.action_open_settings()
        elif event.button.id == "btn-help":
            self.app.action_toggle_help()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle session selection."""
        if isinstance(event.item, SessionItem):
            self._open_session(event.item.session_id)

    def action_new_session(self) -> None:
        """Create a new session."""
        self.app.action_new_session()

    def action_select_session(self) -> None:
        """Open the selected session."""
        list_view = self.query_one("#session-list", ListView)
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, SessionItem):
            self._open_session(list_view.highlighted_child.session_id)

    def action_delete_session(self) -> None:
        """Delete the selected session."""
        list_view = self.query_one("#session-list", ListView)
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, SessionItem):
            session_id = list_view.highlighted_child.session_id
            if session_id in self.app.sessions:
                del self.app.sessions[session_id]
                if session_id in self.app.messages:
                    del self.app.messages[session_id]
                self._refresh_sessions()
                self.app.notify("Session deleted")

    def action_rename_session(self) -> None:
        """Rename the selected session."""
        self.app.notify("Rename: Coming soon!")

    def _open_session(self, session_id: str) -> None:
        """Open a session."""
        self.app.current_session_id = session_id
        self.app.push_screen("session")
