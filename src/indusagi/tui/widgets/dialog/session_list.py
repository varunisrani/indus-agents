"""
Session List Dialog for Indus CLI TUI.

Shows all sessions and allows switching between them.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, ListView, ListItem, Button
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType


class SessionListItem(ListItem):
    """A session item in the list."""

    def __init__(
        self,
        session_id: str,
        name: str,
        model: str,
        message_count: int,
        updated_at: datetime,
        is_current: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.session_id = session_id
        self.session_name = name
        self.model = model
        self.message_count = message_count
        self.updated_at = updated_at
        self.is_current = is_current

    def compose(self) -> ComposeResult:
        """Compose the session item."""
        yield Static(self._render_item())

    def _render_item(self) -> RenderableType:
        """Render the session item."""
        text = Text()

        # Current indicator
        if self.is_current:
            text.append("● ", style="green bold")
        else:
            text.append("  ", style="")

        # Session icon
        text.append("📝 ", style="")

        # Name
        text.append(self.session_name, style="bold")

        # Model
        text.append(f"  [{self.model}]", style="dim cyan")

        # Message count
        text.append(f"  {self.message_count} msgs", style="dim")

        # Time
        time_str = self._format_time()
        text.append(f"  {time_str}", style="dim italic")

        return text

    def _format_time(self) -> str:
        """Format the updated time."""
        now = datetime.now()
        diff = now - self.updated_at

        if diff.days > 7:
            return self.updated_at.strftime("%b %d")
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"


class SessionListDialog(ModalScreen):
    """
    Dialog for viewing and switching sessions.

    Features:
    - List of all sessions
    - Current session highlighted
    - Search/filter
    - Create new session
    - Delete sessions
    """

    DEFAULT_CSS = """
    SessionListDialog {
        align: center middle;
    }

    #session-dialog-container {
        width: 70;
        max-width: 90%;
        height: auto;
        max-height: 70%;
        background: #141414;
        border: thick #333333;
    }

    #session-dialog-title {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-bottom: solid #333333;
    }

    #session-dialog-title Static {
        text-style: bold;
    }

    #session-search-container {
        height: 3;
        padding: 0 1;
        border-bottom: solid #333333;
    }

    #session-list {
        height: auto;
        max-height: 40;
        padding: 1;
    }

    #session-empty {
        text-align: center;
        color: #808080;
        padding: 2;
    }

    #session-dialog-actions {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-top: solid #333333;
        align: right middle;
    }

    .action-btn {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("n", "new_session", "New", show=False),
        Binding("d", "delete_session", "Delete", show=False),
    ]

    filter_text: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="session-dialog-container"):
            # Title
            with Horizontal(id="session-dialog-title"):
                yield Static("Sessions")

            # Search
            with Container(id="session-search-container"):
                yield Input(
                    placeholder="Search sessions...",
                    id="session-search",
                )

            # Session list
            yield ListView(id="session-list")
            yield Static("No sessions yet", id="session-empty")

            # Actions
            with Horizontal(id="session-dialog-actions"):
                yield Button("New", id="btn-new", classes="action-btn")
                yield Button("Delete", id="btn-delete", classes="action-btn")
                yield Button("Cancel", id="btn-cancel", classes="action-btn")
                yield Button("Select", id="btn-select", variant="primary", classes="action-btn")

    def on_mount(self) -> None:
        """Called when mounted."""
        self._update_list()
        self.query_one("#session-search", Input).focus()

    def _update_list(self) -> None:
        """Update the session list."""
        list_view = self.query_one("#session-list", ListView)
        empty_state = self.query_one("#session-empty", Static)

        list_view.clear()

        # Get sessions from app
        sessions = list(self.app.sessions.values())

        # Filter
        if self.filter_text:
            query = self.filter_text.lower()
            sessions = [
                s for s in sessions
                if query in s.name.lower()
                or query in s.model.lower()
            ]

        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        # Update display
        if sessions:
            empty_state.display = False
            list_view.display = True

            current_id = self.app.current_session_id

            for session in sessions:
                item = SessionListItem(
                    session_id=session.id,
                    name=session.name,
                    model=session.model,
                    message_count=session.message_count,
                    updated_at=session.updated_at,
                    is_current=(session.id == current_id),
                )
                list_view.append(item)
        else:
            empty_state.display = True
            list_view.display = False

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "session-search":
            self.filter_text = event.value
            self._update_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle session selection."""
        if isinstance(event.item, SessionListItem):
            self._select_session(event.item.session_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-cancel":
            self.action_close()
        elif event.button.id == "btn-select":
            self.action_select()
        elif event.button.id == "btn-new":
            self.action_new_session()
        elif event.button.id == "btn-delete":
            self.action_delete_session()

    def action_select(self) -> None:
        """Select the highlighted session."""
        list_view = self.query_one("#session-list", ListView)
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, SessionListItem):
            self._select_session(list_view.highlighted_child.session_id)

    def _select_session(self, session_id: str) -> None:
        """Select and switch to a session."""
        self.app.current_session_id = session_id
        self.dismiss(session_id)
        self.app.push_screen("session")

    def action_new_session(self) -> None:
        """Create a new session."""
        self.dismiss(None)
        self.app.action_new_session()

    def action_delete_session(self) -> None:
        """Delete the highlighted session."""
        list_view = self.query_one("#session-list", ListView)
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, SessionListItem):
            session_id = list_view.highlighted_child.session_id

            # Don't delete current session
            if session_id == self.app.current_session_id:
                self.app.notify("Cannot delete current session", severity="warning")
                return

            # Delete
            if session_id in self.app.sessions:
                del self.app.sessions[session_id]
            if session_id in self.app.messages:
                del self.app.messages[session_id]

            self._update_list()
            self.app.notify("Session deleted")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def watch_filter_text(self, value: str) -> None:
        """React to filter text changes."""
        self._update_list()
