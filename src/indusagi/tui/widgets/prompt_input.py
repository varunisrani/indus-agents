"""
Prompt Input Widget for Indus CLI TUI.

Enhanced text input with history, autocomplete, and multi-line support.
"""

from __future__ import annotations

from typing import List, Optional, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input, TextArea
from textual.message import Message
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text
from rich.console import RenderableType


class PromptInput(Static):
    """
    Enhanced prompt input widget.

    Features:
    - Single-line input with Enter to submit
    - History navigation with Up/Down arrows
    - Hints for keyboard shortcuts
    - Processing state indicator
    """

    DEFAULT_CSS = """
    PromptInput {
        height: auto;
        padding: 1;
    }

    #prompt-input-field {
        height: 3;
    }

    #prompt-status {
        height: 1;
        padding-top: 1;
    }

    .hint {
        color: #808080;
        text-align: center;
    }

    .processing {
        color: #fab283;
        text-align: center;
    }
    """

    class Submitted(Message):
        """Fired when the user submits input."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    # Reactive state
    is_processing: reactive[bool] = reactive(False)
    placeholder: reactive[str] = reactive("Type a message... (Enter to send)")

    def __init__(
        self,
        placeholder: str = "Type a message... (Enter to send)",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self._history: List[str] = []
        self._history_index: int = -1
        self._temp_input: str = ""

    def compose(self) -> ComposeResult:
        """Compose the prompt input."""
        yield Input(
            placeholder=self.placeholder,
            id="prompt-input-field",
        )
        yield Static(id="prompt-status", classes="hint")

    def on_mount(self) -> None:
        """Called when mounted."""
        self._update_status()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()

        if not value:
            return

        if self.is_processing:
            return

        # Add to history
        if not self._history or self._history[-1] != value:
            self._history.append(value)
        self._history_index = -1
        self._temp_input = ""

        # Clear input
        event.input.value = ""

        # Post submission event
        self.post_message(self.Submitted(value))

    def on_key(self, event) -> None:
        """Handle key events."""
        input_field = self.query_one("#prompt-input-field", Input)

        if event.key == "up":
            self._navigate_history(-1, input_field)
            event.prevent_default()
            event.stop()

        elif event.key == "down":
            self._navigate_history(1, input_field)
            event.prevent_default()
            event.stop()

    def _navigate_history(self, direction: int, input_field: Input) -> None:
        """Navigate through input history."""
        if not self._history:
            return

        # Save current input if starting navigation
        if self._history_index == -1 and direction == -1:
            self._temp_input = input_field.value

        # Calculate new index
        new_index = self._history_index + direction

        if new_index < -1:
            new_index = -1
        elif new_index >= len(self._history):
            new_index = len(self._history) - 1

        # Update input
        if new_index == -1:
            input_field.value = self._temp_input
        else:
            input_field.value = self._history[-(new_index + 1)]

        self._history_index = new_index

    def _update_status(self) -> None:
        """Update the status line."""
        status = self.query_one("#prompt-status", Static)

        if self.is_processing:
            status.update(Text("⏳ Processing...", style="yellow"))
            status.remove_class("hint")
            status.add_class("processing")
        else:
            hints = "Ctrl+P: Commands │ Ctrl+N: New │ ↑↓: History"
            status.update(Text(hints, style="dim"))
            status.remove_class("processing")
            status.add_class("hint")

    def watch_is_processing(self, value: bool) -> None:
        """React to processing state changes."""
        self._update_status()

        # Disable/enable input
        input_field = self.query_one("#prompt-input-field", Input)
        input_field.disabled = value

    def focus_input(self) -> None:
        """Focus the input field."""
        self.query_one("#prompt-input-field", Input).focus()

    def set_value(self, value: str) -> None:
        """Set the input value."""
        self.query_one("#prompt-input-field", Input).value = value

    def get_value(self) -> str:
        """Get the current input value."""
        return self.query_one("#prompt-input-field", Input).value

    def clear(self) -> None:
        """Clear the input."""
        self.query_one("#prompt-input-field", Input).value = ""
        self._history_index = -1


class MultiLinePromptInput(Static):
    """
    Multi-line prompt input using TextArea.

    Features:
    - Multi-line editing
    - Ctrl+Enter to submit
    - Syntax highlighting for code
    """

    DEFAULT_CSS = """
    MultiLinePromptInput {
        height: auto;
        min-height: 5;
        max-height: 15;
        padding: 1;
    }

    #prompt-textarea {
        height: auto;
        min-height: 3;
        max-height: 12;
    }

    #prompt-multi-status {
        height: 1;
        padding-top: 1;
        color: #808080;
        text-align: center;
    }
    """

    class Submitted(Message):
        """Fired when the user submits input."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    is_processing: reactive[bool] = reactive(False)

    BINDINGS = [
        Binding("ctrl+enter", "submit", "Submit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the multi-line input."""
        yield TextArea(id="prompt-textarea")
        yield Static(
            "Ctrl+Enter to send │ Ctrl+P: Commands",
            id="prompt-multi-status",
        )

    def action_submit(self) -> None:
        """Submit the current input."""
        textarea = self.query_one("#prompt-textarea", TextArea)
        value = textarea.text.strip()

        if not value or self.is_processing:
            return

        # Clear and submit
        textarea.clear()
        self.post_message(self.Submitted(value))

    def watch_is_processing(self, value: bool) -> None:
        """React to processing state changes."""
        textarea = self.query_one("#prompt-textarea", TextArea)
        textarea.disabled = value

        status = self.query_one("#prompt-multi-status", Static)
        if value:
            status.update("⏳ Processing...")
        else:
            status.update("Ctrl+Enter to send │ Ctrl+P: Commands")

    def focus_input(self) -> None:
        """Focus the text area."""
        self.query_one("#prompt-textarea", TextArea).focus()
