"""
Session Header Widget for Indus CLI TUI.

Displays session information at the top of the session screen.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType


class SessionHeader(Static):
    """
    Header widget showing session information.

    Displays:
    - Session name
    - Model/provider
    - Agent name
    - Message count
    - Status indicator
    """

    session_name: reactive[str] = reactive("New Session")
    model: reactive[str] = reactive("gpt-4o")
    agent: reactive[str] = reactive("default")
    message_count: reactive[int] = reactive(0)
    is_processing: reactive[bool] = reactive(False)

    def __init__(
        self,
        session_name: str = "New Session",
        model: str = "gpt-4o",
        agent: str = "default",
        message_count: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.session_name = session_name
        self.model = model
        self.agent = agent
        self.message_count = message_count

    def render(self) -> RenderableType:
        """Render the session header."""
        text = Text()

        # Status indicator
        if self.is_processing:
            text.append("⏳ ", style="yellow blink")
        else:
            text.append("● ", style="green")

        # Session name
        text.append("📝 ", style="")
        text.append(self.session_name, style="bold white")

        # Separator
        text.append("  │  ", style="dim")

        # Model
        text.append("🤖 ", style="")
        text.append(self.model, style="cyan")

        # Separator
        text.append("  │  ", style="dim")

        # Agent
        text.append("👤 ", style="")
        text.append(self.agent, style="magenta")

        # Separator
        text.append("  │  ", style="dim")

        # Message count
        text.append(f"💬 {self.message_count}", style="dim")

        return text

    def update_info(
        self,
        session_name: Optional[str] = None,
        model: Optional[str] = None,
        agent: Optional[str] = None,
        message_count: Optional[int] = None,
        is_processing: Optional[bool] = None,
    ) -> None:
        """Update header information."""
        if session_name is not None:
            self.session_name = session_name
        if model is not None:
            self.model = model
        if agent is not None:
            self.agent = agent
        if message_count is not None:
            self.message_count = message_count
        if is_processing is not None:
            self.is_processing = is_processing

    def watch_session_name(self, value: str) -> None:
        """React to session name changes."""
        self.refresh()

    def watch_model(self, value: str) -> None:
        """React to model changes."""
        self.refresh()

    def watch_is_processing(self, value: bool) -> None:
        """React to processing state changes."""
        self.refresh()
