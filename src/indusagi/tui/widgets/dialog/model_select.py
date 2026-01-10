"""
Model Selection Dialog for Indus CLI TUI.

Allows users to select AI model and provider.
"""

from __future__ import annotations

from typing import List, Optional, Dict
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, ListView, ListItem, Button, Label
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType


@dataclass
class ModelInfo:
    """Information about a model."""
    id: str
    name: str
    provider: str
    description: str = ""
    context_length: int = 0
    is_available: bool = True


class ModelItem(ListItem):
    """A model item in the list."""

    def __init__(self, model: ModelInfo, is_selected: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.is_selected = is_selected

    def compose(self) -> ComposeResult:
        """Compose the model item."""
        yield Static(self._render_item())

    def _render_item(self) -> RenderableType:
        """Render the model item."""
        text = Text()

        # Selection indicator
        if self.is_selected:
            text.append("● ", style="green bold")
        else:
            text.append("  ", style="")

        # Provider icon
        provider_icons = {
            "openai": "🟢",
            "anthropic": "🟣",
            "ollama": "🦙",
            "groq": "⚡",
        }
        icon = provider_icons.get(self.model.provider.lower(), "🤖")
        text.append(f"{icon} ", style="")

        # Model name
        text.append(self.model.name, style="bold")

        # Provider
        text.append(f"  [{self.model.provider}]", style="dim cyan")

        # Context length
        if self.model.context_length:
            text.append(f"  {self.model.context_length // 1000}K ctx", style="dim")

        # Availability
        if not self.model.is_available:
            text.append("  (unavailable)", style="dim red")

        # Description
        if self.model.description:
            text.append(f"\n    {self.model.description}", style="dim")

        return text


class ModelSelectDialog(ModalScreen):
    """
    Dialog for selecting AI model.

    Features:
    - List of available models grouped by provider
    - Current model highlighted
    - Search/filter functionality
    - Quick selection with keyboard
    """

    DEFAULT_CSS = """
    ModelSelectDialog {
        align: center middle;
    }

    #model-dialog-container {
        width: 70;
        max-width: 90%;
        height: auto;
        max-height: 70%;
        background: #141414;
        border: thick #333333;
    }

    #model-dialog-title {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-bottom: solid #333333;
    }

    #model-dialog-title Static {
        text-style: bold;
    }

    #model-search-container {
        height: 3;
        padding: 0 1;
        border-bottom: solid #333333;
    }

    #model-list {
        height: auto;
        max-height: 40;
        padding: 1;
    }

    #model-dialog-actions {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-top: solid #333333;
        align: right middle;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("enter", "select", "Select", show=False),
    ]

    # Available models
    MODELS: List[ModelInfo] = [
        # OpenAI
        ModelInfo(
            id="gpt-4o",
            name="GPT-4o",
            provider="OpenAI",
            description="Most capable GPT-4 model, multimodal",
            context_length=128000,
        ),
        ModelInfo(
            id="gpt-4o-mini",
            name="GPT-4o Mini",
            provider="OpenAI",
            description="Smaller, faster GPT-4o variant",
            context_length=128000,
        ),
        ModelInfo(
            id="gpt-4-turbo",
            name="GPT-4 Turbo",
            provider="OpenAI",
            description="GPT-4 with improved performance",
            context_length=128000,
        ),
        ModelInfo(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            provider="OpenAI",
            description="Fast and cost-effective",
            context_length=16385,
        ),

        # Anthropic
        ModelInfo(
            id="claude-3-5-sonnet-latest",
            name="Claude 3.5 Sonnet",
            provider="Anthropic",
            description="Best balance of intelligence and speed",
            context_length=200000,
        ),
        ModelInfo(
            id="claude-3-opus-latest",
            name="Claude 3 Opus",
            provider="Anthropic",
            description="Most powerful Claude model",
            context_length=200000,
        ),
        ModelInfo(
            id="claude-3-haiku-20240307",
            name="Claude 3 Haiku",
            provider="Anthropic",
            description="Fast and lightweight",
            context_length=200000,
        ),

        # Ollama (local)
        ModelInfo(
            id="llama3.2",
            name="Llama 3.2",
            provider="Ollama",
            description="Meta's latest open model",
            context_length=128000,
        ),
        ModelInfo(
            id="mixtral",
            name="Mixtral 8x7B",
            provider="Ollama",
            description="High-quality mixture of experts",
            context_length=32000,
        ),
        ModelInfo(
            id="codellama",
            name="Code Llama",
            provider="Ollama",
            description="Specialized for code generation",
            context_length=16000,
        ),

        # Groq
        ModelInfo(
            id="llama-3.1-70b-versatile",
            name="Llama 3.1 70B",
            provider="Groq",
            description="Fast inference with Groq",
            context_length=128000,
        ),
        ModelInfo(
            id="mixtral-8x7b-32768",
            name="Mixtral 8x7B",
            provider="Groq",
            description="Fast Mixtral on Groq",
            context_length=32768,
        ),
    ]

    filter_text: reactive[str] = reactive("")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._filtered_models: List[ModelInfo] = self.MODELS.copy()

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="model-dialog-container"):
            # Title
            with Horizontal(id="model-dialog-title"):
                yield Static("Select Model")

            # Search
            with Container(id="model-search-container"):
                yield Input(
                    placeholder="Search models...",
                    id="model-search",
                )

            # Model list
            yield ListView(id="model-list")

            # Actions
            with Horizontal(id="model-dialog-actions"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Select", id="btn-select", variant="primary")

    def on_mount(self) -> None:
        """Called when mounted."""
        self._update_list()
        self.query_one("#model-search", Input).focus()

    def _update_list(self) -> None:
        """Update the model list based on filter."""
        list_view = self.query_one("#model-list", ListView)
        list_view.clear()

        current_model = self.app.current_model

        # Filter models
        if self.filter_text:
            query = self.filter_text.lower()
            self._filtered_models = [
                m for m in self.MODELS
                if query in m.name.lower()
                or query in m.provider.lower()
                or query in m.description.lower()
            ]
        else:
            self._filtered_models = self.MODELS.copy()

        # Add model items
        for model in self._filtered_models:
            is_selected = model.id == current_model
            item = ModelItem(model, is_selected=is_selected)
            list_view.append(item)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "model-search":
            self.filter_text = event.value
            self._update_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle model selection."""
        if isinstance(event.item, ModelItem):
            self._select_model(event.item.model)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-cancel":
            self.action_close()
        elif event.button.id == "btn-select":
            self.action_select()

    def action_select(self) -> None:
        """Select the highlighted model."""
        list_view = self.query_one("#model-list", ListView)
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, ModelItem):
            self._select_model(list_view.highlighted_child.model)

    def _select_model(self, model: ModelInfo) -> None:
        """Select a model."""
        self.app.current_model = model.id
        self.app.notify(f"Model: {model.name}")
        self.dismiss(model.id)

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def watch_filter_text(self, value: str) -> None:
        """React to filter text changes."""
        self._update_list()
