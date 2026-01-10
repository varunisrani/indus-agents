"""
Message List Widget for Indus CLI TUI.

Scrollable container for displaying chat messages.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel
from rich.console import RenderableType


class MessageWidget(Static):
    """
    Widget for displaying a single chat message.

    Supports:
    - User, assistant, tool, and system messages
    - Markdown rendering for assistant responses
    - Streaming indicator
    - Error display
    - Timestamps
    """

    DEFAULT_CSS = """
    MessageWidget {
        padding: 1;
        margin-bottom: 1;
        border-left: tall #333333;
    }

    MessageWidget.user {
        border-left: tall #8be9fd;
        background: #1a1a1a;
    }

    MessageWidget.assistant {
        border-left: tall #fab283;
        background: #141414;
    }

    MessageWidget.tool {
        border-left: tall #e5c07b;
        background: #1a1a1a;
    }

    MessageWidget.system {
        border-left: tall #8be9fd;
        background: #1a1a1a;
    }

    MessageWidget.error {
        border-left: tall #ff5555;
        background: #1a0a0a;
    }

    MessageWidget.streaming {
        border-left: tall #fab283;
    }
    """

    content: reactive[str] = reactive("")
    is_streaming: reactive[bool] = reactive(False)

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        model: Optional[str] = None,
        is_streaming: bool = False,
        is_error: bool = False,
        message_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.model = model
        self.is_streaming = is_streaming
        self.is_error = is_error
        self.message_id = message_id

        # Add CSS classes based on role
        self.add_class(role)
        if is_error:
            self.add_class("error")
        if is_streaming:
            self.add_class("streaming")

    def render(self) -> RenderableType:
        """Render the message."""
        # Role styling
        role_styles = {
            "user": ("bold blue", "You"),
            "assistant": ("bold magenta", "Assistant"),
            "tool": ("bold yellow", "Tool"),
            "system": ("bold cyan", "System"),
        }

        style, label = role_styles.get(self.role, ("bold", self.role.upper()))

        # Model suffix for assistant
        if self.model and self.role == "assistant":
            label = f"{label} ({self.model})"

        # Time
        time_str = self.timestamp.strftime("%H:%M")

        # Build header
        header = Text()
        header.append(f"[{time_str}] ", style="dim")
        header.append(label, style=style)

        # Content
        if self.is_error:
            content_text = Text(self.content, style="red")
        elif self.role == "assistant" and not self.is_streaming:
            # Use markdown for completed assistant messages
            return Panel(
                Markdown(self.content) if self.content else Text("..."),
                title=str(header),
                title_align="left",
                border_style="magenta" if not self.is_error else "red",
                padding=(0, 1),
            )
        else:
            content_text = Text(self.content)

        # Add streaming cursor
        if self.is_streaming:
            content_text.append("▌", style="blink bold cyan")

        # Combine
        result = Text()
        result.append_text(header)
        result.append("\n")
        result.append_text(content_text)

        return result

    def append_token(self, token: str) -> None:
        """Append a streaming token."""
        self.content += token
        self.refresh()

    def complete_streaming(self) -> None:
        """Mark message as complete."""
        self.is_streaming = False
        self.remove_class("streaming")
        self.refresh()

    def watch_content(self, value: str) -> None:
        """React to content changes."""
        self.refresh()

    def watch_is_streaming(self, value: bool) -> None:
        """React to streaming state changes."""
        if value:
            self.add_class("streaming")
        else:
            self.remove_class("streaming")
        self.refresh()


class MessageList(ScrollableContainer):
    """
    Scrollable list of messages.

    Features:
    - Auto-scroll to bottom on new messages
    - Efficient updates for streaming
    - Message grouping
    """

    DEFAULT_CSS = """
    MessageList {
        height: 100%;
        padding: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._message_widgets: Dict[str, MessageWidget] = {}

    def add_message(
        self,
        message_id: str,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        model: Optional[str] = None,
        is_streaming: bool = False,
        is_error: bool = False,
    ) -> MessageWidget:
        """Add a message to the list."""
        widget = MessageWidget(
            role=role,
            content=content,
            timestamp=timestamp,
            model=model,
            is_streaming=is_streaming,
            is_error=is_error,
            message_id=message_id,
        )

        self._message_widgets[message_id] = widget
        self.mount(widget)
        self.scroll_end(animate=False)

        return widget

    def update_message(self, message_id: str, content: str) -> bool:
        """Update a message's content."""
        if message_id in self._message_widgets:
            self._message_widgets[message_id].content = content
            return True
        return False

    def append_to_message(self, message_id: str, token: str) -> bool:
        """Append a token to a streaming message."""
        if message_id in self._message_widgets:
            self._message_widgets[message_id].append_token(token)
            self.scroll_end(animate=False)
            return True
        return False

    def complete_message(self, message_id: str) -> bool:
        """Mark a message as complete."""
        if message_id in self._message_widgets:
            self._message_widgets[message_id].complete_streaming()
            return True
        return False

    def get_message(self, message_id: str) -> Optional[MessageWidget]:
        """Get a message widget by ID."""
        return self._message_widgets.get(message_id)

    def clear_messages(self) -> None:
        """Remove all messages."""
        self._message_widgets.clear()
        self.remove_children()

    def load_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Load a list of messages."""
        self.clear_messages()

        for msg in messages:
            self.add_message(
                message_id=msg.get("id", str(len(self._message_widgets))),
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp"),
                model=msg.get("model"),
                is_streaming=msg.get("is_streaming", False),
                is_error=msg.get("is_error", False),
            )
