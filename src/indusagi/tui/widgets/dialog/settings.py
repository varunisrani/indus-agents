"""
Settings Dialog for Indus CLI TUI.

Allows users to configure model, theme, API keys, and other settings.
"""

from __future__ import annotations

import os
from typing import Optional

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.widgets import Static, Input, Button, Select, Switch, Label, TabbedContent, TabPane
from textual.binding import Binding
from rich.text import Text


class SettingsDialog(ModalScreen):
    """Settings dialog for configuring the application."""

    DEFAULT_CSS = """
    SettingsDialog {
        align: center middle;
    }

    #settings-container {
        width: 85;
        height: 90%;
        max-height: 45;
        background: #141414;
        border: thick #fab283;
    }

    #settings-header {
        height: 3;
        padding: 0 2;
        background: #1a1a1a;
        border-bottom: solid #333333;
        content-align: center middle;
    }

    #settings-title {
        text-style: bold;
        color: #fab283;
    }

    #settings-content {
        height: 1fr;
        padding: 1;
    }

    #settings-footer {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-top: solid #333333;
        align: right middle;
    }

    .section-title {
        text-style: bold;
        color: #fab283;
        margin-bottom: 1;
    }

    .field-row {
        height: 3;
        margin-bottom: 1;
    }

    .field-label {
        width: 18;
        padding: 0 1;
    }

    .hint {
        color: #666666;
        padding: 0 1;
        margin-top: 1;
    }

    Select {
        width: 1fr;
    }

    Input {
        width: 1fr;
    }

    Input:focus {
        border: solid #fab283;
    }

    .btn {
        margin-left: 1;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 1;
    }

    VerticalScroll {
        height: 1fr;
    }

    .provider-label {
        color: #50fa7b;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("tab", "focus_next", "Next", show=False),
        Binding("shift+tab", "focus_previous", "Previous", show=False),
    ]

    # Available providers and models
    PROVIDERS = ["OpenAI", "Anthropic", "GLM (Z.AI)", "Groq", "Ollama", "Mistral", "Custom"]

    MODELS = {
        "OpenAI": [
            ("GPT-4o (Best)", "gpt-4o"),
            ("GPT-4o Mini (Fast)", "gpt-4o-mini"),
            ("GPT-4 Turbo", "gpt-4-turbo"),
        ],
        "Anthropic": [
            ("Claude 3.5 Sonnet", "claude-3-5-sonnet-latest"),
            ("Claude 3 Opus", "claude-3-opus-latest"),
            ("Claude 3 Haiku", "claude-3-haiku-20240307"),
        ],
        "GLM (Z.AI)": [
            ("GLM-4.7 (Best)", "glm-4.7"),
            ("GLM-4 Plus", "glm-4-plus"),
            ("GLM-4", "glm-4"),
            ("GLM-4-Flash (Fast)", "glm-4-flash"),
        ],
        "Groq": [
            ("Llama 3.1 70B", "llama-3.1-70b-versatile"),
            ("Mixtral 8x7B", "mixtral-8x7b-32768"),
        ],
        "Ollama": [
            ("Llama 3.2", "llama3.2"),
            ("Mixtral", "mixtral"),
            ("CodeLlama", "codellama"),
        ],
        "Mistral": [
            ("Mistral Large", "mistral-large-latest"),
            ("Mistral Small", "mistral-small-latest"),
            ("Mixtral 8x7B", "open-mixtral-8x7b"),
        ],
        "Custom": [
            ("Custom Model", "custom"),
        ],
    }

    THEMES = [
        ("Dark", "dark"),
        ("Light", "light"),
        ("Catppuccin", "catppuccin"),
        ("Dracula", "dracula"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the settings dialog."""
        with Container(id="settings-container"):
            with Horizontal(id="settings-header"):
                yield Static("Settings", id="settings-title")

            with Container(id="settings-content"):
                with TabbedContent():
                    with TabPane("Model", id="tab-model"):
                        yield from self._compose_model_tab()

                    with TabPane("API Keys", id="tab-api"):
                        yield from self._compose_api_tab()

                    with TabPane("Theme", id="tab-theme"):
                        yield from self._compose_theme_tab()

            with Horizontal(id="settings-footer"):
                yield Button("Cancel", id="btn-cancel", classes="btn")
                yield Button("Save", id="btn-save", variant="primary", classes="btn")

    def _compose_model_tab(self) -> ComposeResult:
        """Model selection tab."""
        with Vertical():
            yield Static("Select AI Provider and Model", classes="section-title")

            with Horizontal(classes="field-row"):
                yield Static("Provider:", classes="field-label")
                yield Select(
                    [(p, p) for p in self.PROVIDERS],
                    id="select-provider",
                    value="OpenAI",
                )

            with Horizontal(classes="field-row"):
                yield Static("Model:", classes="field-label")
                yield Select(
                    self.MODELS["OpenAI"],
                    id="select-model",
                    value="gpt-4o",
                )

            yield Static("", id="model-status", classes="hint")

    def _compose_api_tab(self) -> ComposeResult:
        """API configuration tab."""
        with VerticalScroll():
            yield Static("Configure API Keys (Tab to navigate)", classes="section-title")

            # GLM
            yield Static("GLM (Z.AI)", classes="provider-label")
            with Horizontal(classes="field-row"):
                yield Static("API Key:", classes="field-label")
                yield Input(placeholder="your-glm-api-key", password=True, id="input-glm-key")
            with Horizontal(classes="field-row"):
                yield Static("API URL:", classes="field-label")
                yield Input(
                    value=os.environ.get("GLM_API_BASE", "https://api.z.ai/api/anthropic"),
                    id="input-glm-url"
                )

            # OpenAI
            yield Static("OpenAI", classes="provider-label")
            with Horizontal(classes="field-row"):
                yield Static("API Key:", classes="field-label")
                yield Input(placeholder="sk-...", password=True, id="input-openai-key")
            with Horizontal(classes="field-row"):
                yield Static("API URL:", classes="field-label")
                yield Input(
                    placeholder="https://api.openai.com/v1 (optional)",
                    value=os.environ.get("OPENAI_API_BASE", ""),
                    id="input-openai-url"
                )

            # Anthropic
            yield Static("Anthropic", classes="provider-label")
            with Horizontal(classes="field-row"):
                yield Static("API Key:", classes="field-label")
                yield Input(placeholder="sk-ant-...", password=True, id="input-anthropic-key")
            with Horizontal(classes="field-row"):
                yield Static("API URL:", classes="field-label")
                yield Input(
                    placeholder="https://api.anthropic.com (optional)",
                    value=os.environ.get("ANTHROPIC_BASE_URL", ""),
                    id="input-anthropic-url"
                )

            # Groq
            yield Static("Groq", classes="provider-label")
            with Horizontal(classes="field-row"):
                yield Static("API Key:", classes="field-label")
                yield Input(placeholder="gsk_...", password=True, id="input-groq-key")

            # Ollama
            yield Static("Ollama (Local)", classes="provider-label")
            with Horizontal(classes="field-row"):
                yield Static("URL:", classes="field-label")
                yield Input(
                    value=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
                    id="input-ollama-url"
                )

            # Mistral
            yield Static("Mistral", classes="provider-label")
            with Horizontal(classes="field-row"):
                yield Static("API Key:", classes="field-label")
                yield Input(placeholder="mistral_...", password=True, id="input-mistral-key")
            with Horizontal(classes="field-row"):
                yield Static("API URL:", classes="field-label")
                yield Input(
                    placeholder="https://api.mistral.ai/v1 (optional)",
                    value=os.environ.get("MISTRAL_BASE_URL", ""),
                    id="input-mistral-url"
                )

            yield Static("Keys saved for current session only.", classes="hint")

    def _compose_theme_tab(self) -> ComposeResult:
        """Theme selection tab."""
        with Vertical():
            yield Static("Select Theme", classes="section-title")

            with Horizontal(classes="field-row"):
                yield Static("Theme:", classes="field-label")
                yield Select(
                    self.THEMES,
                    id="select-theme",
                    value="dark",
                )

    def on_mount(self) -> None:
        """Initialize values when dialog opens."""
        try:
            # Set current model
            current_model = getattr(self.app, 'current_model', 'gpt-4o')

            # Find provider for current model
            current_provider = "OpenAI"
            for provider, models in self.MODELS.items():
                if any(m[1] == current_model for m in models):
                    current_provider = provider
                    break

            # Set provider dropdown
            provider_select = self.query_one("#select-provider", Select)
            provider_select.value = current_provider

            # Update model options
            self._update_models(current_provider)

            # Set model dropdown
            model_select = self.query_one("#select-model", Select)
            model_select.value = current_model

            # Update status
            self._update_status(f"Current: {current_provider} / {current_model}")

            # Set theme
            theme_select = self.query_one("#select-theme", Select)
            theme_select.value = getattr(self.app, 'theme_name', 'dark')

        except Exception as e:
            self._update_status(f"Error: {e}")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle dropdown changes."""
        if event.select.id == "select-provider":
            provider = str(event.value)
            self._update_models(provider)
            self._update_status(f"Provider: {provider}")

        elif event.select.id == "select-model":
            model = str(event.value)
            self._update_status(f"Selected: {model}")

    def _update_models(self, provider: str) -> None:
        """Update model dropdown for selected provider."""
        try:
            model_select = self.query_one("#select-model", Select)
            models = self.MODELS.get(provider, [("Custom", "custom")])
            model_select.set_options(models)
            if models:
                model_select.value = models[0][1]
        except Exception:
            pass

    def _update_status(self, text: str) -> None:
        """Update status display."""
        try:
            status = self.query_one("#model-status", Static)
            status.update(text)
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._save_all()

    def _save_all(self) -> None:
        """Save all settings."""
        try:
            # Get values from form
            model_val = self.query_one("#select-model", Select).value
            provider_val = self.query_one("#select-provider", Select).value
            theme_val = self.query_one("#select-theme", Select).value

            glm_key = self.query_one("#input-glm-key", Input).value.strip()
            glm_url = self.query_one("#input-glm-url", Input).value.strip()
            openai_key = self.query_one("#input-openai-key", Input).value.strip()
            openai_url = self.query_one("#input-openai-url", Input).value.strip()
            anthropic_key = self.query_one("#input-anthropic-key", Input).value.strip()
            anthropic_url = self.query_one("#input-anthropic-url", Input).value.strip()
            groq_key = self.query_one("#input-groq-key", Input).value.strip()
            ollama_url = self.query_one("#input-ollama-url", Input).value.strip()
            mistral_key = self.query_one("#input-mistral-key", Input).value.strip()
            mistral_url = self.query_one("#input-mistral-url", Input).value.strip()

            # Save to app state
            if model_val:
                self.app.current_model = str(model_val)
            if provider_val:
                self.app.current_provider = str(provider_val)
            if theme_val:
                self.app.theme_name = str(theme_val)

            # Save API keys to environment
            if glm_key:
                os.environ["GLM_API_KEY"] = glm_key
                # GLM uses Anthropic-compatible API via Z.AI
                os.environ["ANTHROPIC_API_KEY"] = glm_key
            if glm_url:
                os.environ["GLM_API_BASE"] = glm_url
                os.environ["ANTHROPIC_BASE_URL"] = glm_url  # Match what agent.py expects

            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            if openai_url:
                os.environ["OPENAI_API_BASE"] = openai_url

            if anthropic_key:
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            if anthropic_url:
                os.environ["ANTHROPIC_BASE_URL"] = anthropic_url  # Match what agent.py expects

            if groq_key:
                os.environ["GROQ_API_KEY"] = groq_key

            if ollama_url:
                os.environ["OLLAMA_HOST"] = ollama_url

            if mistral_key:
                os.environ["MISTRAL_API_KEY"] = mistral_key
            if mistral_url:
                os.environ["MISTRAL_BASE_URL"] = mistral_url

            # Reinitialize agent bridge
            from indusagi.tui.core.agent_bridge import AgentBridge
            self.app.agent_bridge = AgentBridge(
                model=self.app.current_model,
                provider=self.app.current_provider,
                use_agency=True,
            )

            # Show success
            self.app.notify(f"Settings saved! Model: {self.app.current_model}")
            self.dismiss(True)

        except Exception as e:
            error_text = str(e)[:100].replace("[", "\\[").replace("]", "\\]")
            self.app.notify(f"Error: {error_text}", severity="error")

    def action_close(self) -> None:
        """Close dialog."""
        self.dismiss(None)
