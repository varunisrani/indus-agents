"""
Base Dialog for Indus CLI TUI.

Provides a foundation for modal dialogs.
"""

from __future__ import annotations

from typing import Optional, Callable

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Label
from textual.binding import Binding
from rich.text import Text
from rich.console import RenderableType


class BaseDialog(ModalScreen):
    """
    Base class for modal dialogs.

    Provides:
    - Modal overlay with backdrop
    - Title bar
    - Content area
    - Action buttons
    - Escape to close
    """

    DEFAULT_CSS = """
    BaseDialog {
        align: center middle;
    }

    #dialog-backdrop {
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
    }

    #dialog-container {
        width: 60;
        max-width: 80%;
        height: auto;
        max-height: 80%;
        background: #141414;
        border: thick #333333;
        padding: 0;
    }

    #dialog-title-bar {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-bottom: solid #333333;
    }

    #dialog-title {
        text-style: bold;
        color: #ffffff;
    }

    #dialog-content {
        padding: 1;
        height: auto;
    }

    #dialog-actions {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-top: solid #333333;
        align: right middle;
    }

    .dialog-button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
    ]

    def __init__(
        self,
        title: str = "Dialog",
        show_close_button: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.dialog_title = title
        self.show_close_button = show_close_button

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog-container"):
            # Title bar
            with Horizontal(id="dialog-title-bar"):
                yield Static(self.dialog_title, id="dialog-title")

            # Content area (override in subclass)
            with Vertical(id="dialog-content"):
                yield from self.compose_content()

            # Action buttons
            with Horizontal(id="dialog-actions"):
                yield from self.compose_actions()

    def compose_content(self) -> ComposeResult:
        """
        Compose the dialog content.

        Override this method in subclasses to add content.
        """
        yield Static("Dialog content goes here")

    def compose_actions(self) -> ComposeResult:
        """
        Compose the action buttons.

        Override this method in subclasses to add buttons.
        """
        if self.show_close_button:
            yield Button("Close", id="btn-close", classes="dialog-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-close":
            self.action_close()

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss()


class ConfirmDialog(BaseDialog):
    """
    Confirmation dialog with Yes/No buttons.
    """

    def __init__(
        self,
        title: str = "Confirm",
        message: str = "Are you sure?",
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs,
    ) -> None:
        super().__init__(title=title, show_close_button=False, **kwargs)
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    def compose_content(self) -> ComposeResult:
        """Compose the confirmation message."""
        yield Static(self.message, id="confirm-message")

    def compose_actions(self) -> ComposeResult:
        """Compose Yes/No buttons."""
        yield Button("Cancel", id="btn-cancel", classes="dialog-button")
        yield Button("Confirm", id="btn-confirm", variant="primary", classes="dialog-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-confirm":
            if self.on_confirm:
                self.on_confirm()
            self.dismiss(True)
        elif event.button.id == "btn-cancel":
            if self.on_cancel:
                self.on_cancel()
            self.dismiss(False)


class AlertDialog(BaseDialog):
    """
    Alert dialog with a single OK button.
    """

    def __init__(
        self,
        title: str = "Alert",
        message: str = "",
        alert_type: str = "info",  # info, warning, error, success
        **kwargs,
    ) -> None:
        super().__init__(title=title, **kwargs)
        self.message = message
        self.alert_type = alert_type

    def compose_content(self) -> ComposeResult:
        """Compose the alert message."""
        # Icon based on type
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
        }
        icon = icons.get(self.alert_type, "ℹ️")

        yield Static(f"{icon}  {self.message}", id="alert-message")

    def compose_actions(self) -> ComposeResult:
        """Compose OK button."""
        yield Button("OK", id="btn-ok", variant="primary", classes="dialog-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-ok":
            self.dismiss()


class InputDialog(BaseDialog):
    """
    Dialog with text input.
    """

    def __init__(
        self,
        title: str = "Input",
        prompt: str = "Enter value:",
        default_value: str = "",
        placeholder: str = "",
        on_submit: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(title=title, show_close_button=False, **kwargs)
        self.prompt = prompt
        self.default_value = default_value
        self.placeholder = placeholder
        self.on_submit = on_submit

    def compose_content(self) -> ComposeResult:
        """Compose the input field."""
        from textual.widgets import Input

        yield Static(self.prompt, id="input-prompt")
        yield Input(
            value=self.default_value,
            placeholder=self.placeholder,
            id="input-field",
        )

    def compose_actions(self) -> ComposeResult:
        """Compose Cancel/OK buttons."""
        yield Button("Cancel", id="btn-cancel", classes="dialog-button")
        yield Button("OK", id="btn-ok", variant="primary", classes="dialog-button")

    def on_mount(self) -> None:
        """Focus the input field."""
        from textual.widgets import Input
        self.query_one("#input-field", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        from textual.widgets import Input

        if event.button.id == "btn-ok":
            value = self.query_one("#input-field", Input).value
            if self.on_submit:
                self.on_submit(value)
            self.dismiss(value)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_input_submitted(self, event) -> None:
        """Handle Enter key in input."""
        from textual.widgets import Input

        value = self.query_one("#input-field", Input).value
        if self.on_submit:
            self.on_submit(value)
        self.dismiss(value)
