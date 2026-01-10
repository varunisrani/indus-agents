"""
Session Screen for Indus CLI TUI.

The main chat interface with messages, prompt input, and tools.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Button, Label, TextArea
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel
from rich.console import RenderableType


# ============================================================================
# Message Widget
# ============================================================================

class MessageWidget(Static):
    """Widget for displaying a single message."""

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        model: Optional[str] = None,
        is_streaming: bool = False,
        is_error: bool = False,
        tool_calls: Optional[List[Dict]] = None,
    ) -> None:
        super().__init__()
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.model = model
        self._is_streaming = is_streaming
        self._is_error = is_error
        self.tool_calls = tool_calls or []

        # Set CSS class based on role
        self.add_class(f"message-{role}")
        if is_error:
            self.add_class("message-error")

    def render(self) -> RenderableType:
        """Render the message."""
        # Role label
        role_style = {
            "user": "bold blue",
            "assistant": "bold magenta",
            "tool": "bold yellow",
            "system": "bold cyan",
        }.get(self.role, "bold")

        role_label = self.role.upper()
        if self.model and self.role == "assistant":
            role_label = f"{role_label} ({self.model})"

        # Time
        time_str = self.timestamp.strftime("%H:%M")

        # Build output
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"{role_label}: ", style=role_style)

        if self._is_streaming:
            text.append(self.content)
            text.append("▌", style="blink bold cyan")
        elif self._is_error:
            text.append(self.content, style="red")
        else:
            # Render markdown for assistant messages
            if self.role == "assistant":
                return Panel(
                    Markdown(self.content),
                    title=f"[{time_str}] {role_label}",
                    title_align="left",
                    border_style="magenta",
                    padding=(0, 1),
                )
            else:
                text.append(self.content)

        return text

    def update_content(self, content: str) -> None:
        """Update the message content (for streaming)."""
        self.content = content
        self.refresh()

    def append_content(self, token: str) -> None:
        """Append to the message content (for streaming)."""
        self.content += token
        self.refresh()

    def complete(self) -> None:
        """Mark the message as complete (stop streaming)."""
        self._is_streaming = False
        self.refresh()


# ============================================================================
# Tool Execution Widget
# ============================================================================

class ToolExecutionWidget(Static):
    """Widget for displaying tool execution."""

    def __init__(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        status: str = "running",  # running, success, error
        result: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.tool_name = tool_name
        self.arguments = arguments
        self.status = status
        self.result = result
        self.add_class("tool-execution")

    def render(self) -> RenderableType:
        """Render the tool execution."""
        # Status icon
        status_icon = {
            "running": "⏳",
            "success": "✓",
            "error": "✗",
        }.get(self.status, "●")

        status_style = {
            "running": "yellow",
            "success": "green",
            "error": "red",
        }.get(self.status, "white")

        # Format arguments
        args_str = ", ".join(f"{k}={repr(v)[:30]}" for k, v in self.arguments.items())

        text = Text()
        text.append(f"{status_icon} ", style=status_style)
        text.append(f"{self.tool_name}", style="bold yellow")
        text.append(f"({args_str})", style="dim")

        if self.result:
            text.append("\n  → ", style="dim")
            result_preview = self.result[:100] + "..." if len(self.result) > 100 else self.result
            text.append(result_preview, style="green" if self.status == "success" else "red")

        return text

    def set_result(self, result: str, success: bool = True) -> None:
        """Set the tool result."""
        self.result = result
        self.status = "success" if success else "error"
        self.refresh()


# ============================================================================
# Prompt Input Widget
# ============================================================================

class PromptInput(Static):
    """Enhanced prompt input widget."""

    class Submitted(Message):
        """Fired when input is submitted."""
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def __init__(self) -> None:
        super().__init__()
        self._history: List[str] = []
        self._history_index: int = -1

    def compose(self) -> ComposeResult:
        """Compose the prompt input."""
        with Vertical(id="prompt-wrapper"):
            yield Input(
                placeholder="Type a message... (Enter to send, Shift+Enter for newline)",
                id="prompt-input",
            )
            yield Static(
                "Ctrl+P: Commands | Ctrl+N: New Session | Ctrl+S: Sessions",
                id="prompt-hint",
                classes="prompt-hint",
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()
        if value:
            # Add to history
            self._history.append(value)
            self._history_index = -1

            # Clear input
            event.input.value = ""

            # Post message
            self.post_message(self.Submitted(value))

    def on_key(self, event) -> None:
        """Handle key events for history navigation."""
        input_widget = self.query_one("#prompt-input", Input)

        if event.key == "up" and self._history:
            # Navigate up in history
            if self._history_index == -1:
                self._history_index = len(self._history) - 1
            elif self._history_index > 0:
                self._history_index -= 1
            input_widget.value = self._history[self._history_index]
            event.prevent_default()

        elif event.key == "down" and self._history:
            # Navigate down in history
            if self._history_index >= 0:
                self._history_index += 1
                if self._history_index >= len(self._history):
                    self._history_index = -1
                    input_widget.value = ""
                else:
                    input_widget.value = self._history[self._history_index]
            event.prevent_default()

    def focus_input(self) -> None:
        """Focus the input."""
        self.query_one("#prompt-input", Input).focus()


# ============================================================================
# Session Header Widget
# ============================================================================

class SessionHeader(Static):
    """Header showing session info."""

    def __init__(
        self,
        session_name: str,
        model: str,
        agent: str,
        message_count: int = 0,
    ) -> None:
        super().__init__()
        self.session_name = session_name
        self.model = model
        self.agent = agent
        self.message_count = message_count

    def render(self) -> RenderableType:
        """Render the session header."""
        text = Text()
        text.append("📝 ", style="")
        text.append(self.session_name, style="bold")
        text.append("  |  ", style="dim")
        text.append("🤖 ", style="")
        text.append(self.model, style="cyan")
        text.append("  |  ", style="dim")
        text.append(f"{self.message_count} messages", style="dim")
        return text

    def update_info(self, **kwargs) -> None:
        """Update header info."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.refresh()


# ============================================================================
# Session Screen
# ============================================================================

class SessionScreen(Screen):
    """
    Main chat session screen.

    Layout:
    - Header: Session info
    - Messages: Scrollable message list
    - Prompt: Input area
    """

    BINDINGS = [
        Binding("escape", "go_home", "Back", show=True),
        Binding("ctrl+p", "open_command_palette", "Cmds", show=True, priority=True),
        Binding("slash", "open_command_palette", "Cmds", show=False, priority=True),
        Binding("ctrl+l", "clear_messages", "Clear", show=True),
    ]

    CSS = """
    SessionScreen {
        layout: vertical;
    }

    #session-header {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-bottom: solid #444444;
        content-align: center middle;
    }

    #messages-container {
        height: 1fr;
        padding: 1;
        background: #0d0d0d;
    }

    #prompt-container {
        height: auto;
        min-height: 7;
        padding: 1;
        background: #1a1a1a;
        border-top: solid #444444;
    }

    #prompt-wrapper {
        height: auto;
    }

    #prompt-input {
        height: 3;
        background: #2a2a2a;
        border: solid #555555;
        padding: 0 1;
    }

    #prompt-input:focus {
        border: solid #fab283;
    }

    .prompt-hint {
        color: #888888;
        text-align: center;
        margin-top: 1;
    }

    .message-user {
        margin-bottom: 1;
        padding: 1;
        background: #1a1a1a;
        border-left: tall #8be9fd;
    }

    .message-assistant {
        margin-bottom: 1;
        padding: 1;
        background: #141414;
        border-left: tall #fab283;
    }

    .tool-execution {
        margin: 0 2 1 2;
        padding: 1;
        background: #1a1a1a;
        border-left: tall #e5c07b;
    }

    #processing-indicator {
        text-align: center;
        color: #fab283;
        padding: 1;
    }

    .empty-chat {
        text-align: center;
        color: #666666;
        padding: 4;
        width: 100%;
        height: auto;
        content-align: center middle;
    }
    """

    # Reactive state
    is_processing: reactive[bool] = reactive(False)
    _refresh_scheduled: reactive[bool] = reactive(False)

    def _schedule_refresh(self) -> None:
        """Schedule a single refresh on the next tick (debounced)."""
        if self._refresh_scheduled:
            return
        self._refresh_scheduled = True

        def _do_refresh() -> None:
            self._refresh_scheduled = False
            self._refresh_header()
            self._refresh_messages()

        self.call_later(_do_refresh)

    def compose(self) -> ComposeResult:
        """Compose the session screen."""
        yield Container(id="session-header")
        yield ScrollableContainer(id="messages-container")
        yield Container(PromptInput(), id="prompt-container")

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._refresh_header()
        self._refresh_messages()

        # Focus input
        self.query_one(PromptInput).focus_input()

    def on_screen_resume(self) -> None:
        """Called when screen is resumed."""
        self._refresh_header()
        self._refresh_messages()
        self.query_one(PromptInput).focus_input()

    def _refresh_header(self) -> None:
        """Refresh the session header."""
        header_container = self.query_one("#session-header", Container)
        header_container.remove_children()

        session = self.app.get_current_session()
        if session:
            header = SessionHeader(
                session_name=session.name,
                model=session.model,
                agent=session.agent,
                message_count=session.message_count,
            )
            header_container.mount(header)

    def _refresh_messages(self) -> None:
        """Refresh the messages list."""
        messages_container = self.query_one("#messages-container", ScrollableContainer)
        messages_container.remove_children()

        session = self.app.get_current_session()
        if not session:
            return

        messages = self.app.get_session_messages(session.id)

        if not messages:
            # Show empty state (no ID to avoid duplicate ID errors on refresh)
            empty_msg = Static(
                "💬 Start a conversation!\n\nType your message below and press Enter to send.",
                classes="empty-chat",
            )
            messages_container.mount(empty_msg)
            return

        for msg in messages:
            widget = MessageWidget(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                model=getattr(msg, 'model', None),
                is_streaming=msg.is_streaming,
                is_error=msg.is_error,
                tool_calls=msg.tool_calls,
            )
            messages_container.mount(widget)

            # Add tool execution widgets
            for tool_call in msg.tool_calls:
                tool_widget = ToolExecutionWidget(
                    tool_name=tool_call.get("name", "unknown"),
                    arguments=tool_call.get("arguments", {}),
                    status=tool_call.get("status", "success"),
                    result=tool_call.get("result"),
                )
                messages_container.mount(tool_widget)

        # Scroll to bottom
        messages_container.scroll_end(animate=False)

    def on_prompt_input_submitted(self, event: PromptInput.Submitted) -> None:
        """Handle prompt submission."""
        if self.is_processing:
            self.app.notify("Already processing...", severity="warning")
            return

        # Start processing
        self.is_processing = True
        asyncio.create_task(self._process_message(event.value))

    # ========================================================================
    # App events (streaming + tool events)
    # ========================================================================

    def on_message_submitted(self, message: Message) -> None:
        """Refresh UI when the user message is accepted by the app."""
        self._schedule_refresh()

    def on_streaming_token(self, message: Message) -> None:
        """Refresh UI during streaming (tokens + agent lifecycle logs are delivered as tokens)."""
        self._schedule_refresh()

    def on_tool_executing(self, message: Message) -> None:
        """Refresh UI when a tool starts executing."""
        self._schedule_refresh()

    def on_tool_completed(self, message: Message) -> None:
        """Refresh UI when a tool completes."""
        self._schedule_refresh()

    async def _process_message(self, content: str) -> None:
        """Process a message asynchronously."""
        try:
            # Send message through app
            await self.app.send_message(content)

            # Refresh display
            self._refresh_header()
            self._refresh_messages()

        except Exception as e:
            self.app.notify(f"Error: {e}", severity="error")
        finally:
            self.is_processing = False

    def action_go_home(self) -> None:
        """Go back to home screen."""
        self.app.pop_screen()

    def action_clear_messages(self) -> None:
        """Clear messages in current session."""
        session = self.app.get_current_session()
        if session:
            self.app.messages[session.id] = []
            session.message_count = 0
            self._refresh_messages()
            self._refresh_header()
            self.app.notify("Messages cleared")

    def action_regenerate(self) -> None:
        """Regenerate the last response."""
        self.app.notify("Regenerate: Coming soon!")

    def action_open_command_palette(self) -> None:
        """Open command palette."""
        self.app.action_toggle_command_palette()

    def watch_is_processing(self, processing: bool) -> None:
        """React to processing state changes."""
        messages_container = self.query_one("#messages-container", ScrollableContainer)

        # Remove any existing processing indicator
        for child in messages_container.children:
            if child.id == "processing-indicator":
                child.remove()

        # Add processing indicator if processing
        if processing:
            indicator = Static("⏳ Processing...", id="processing-indicator")
            messages_container.mount(indicator)
            messages_container.scroll_end()
