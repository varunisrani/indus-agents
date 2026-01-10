"""
Command Palette for Indus CLI TUI.

A fuzzy-searchable command palette similar to VS Code / OpenCode.
"""

from __future__ import annotations

from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Static, Input, ListView, ListItem
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType


@dataclass
class Command:
    """A command in the palette."""
    id: str
    title: str
    description: str = ""
    keybind: str = ""
    category: str = "General"
    action: Optional[Callable] = None
    icon: str = "›"


class CommandItem(ListItem):
    """A command item in the list."""

    def __init__(self, command: Command, **kwargs) -> None:
        super().__init__(**kwargs)
        self.command = command

    def compose(self) -> ComposeResult:
        """Compose the command item."""
        yield Static(self._render_item())

    def _render_item(self) -> RenderableType:
        """Render the command item."""
        text = Text()

        # Icon
        text.append(f"{self.command.icon} ", style="cyan")

        # Title
        text.append(self.command.title, style="bold")

        # Category
        if self.command.category:
            text.append(f"  [{self.command.category}]", style="dim magenta")

        # Keybind
        if self.command.keybind:
            text.append(f"  {self.command.keybind}", style="dim cyan")

        # Description
        if self.command.description:
            text.append(f"\n  {self.command.description}", style="dim")

        return text


class CommandPalette(ModalScreen):
    """
    Command palette dialog.

    Features:
    - Fuzzy search for commands
    - Keyboard navigation
    - Keybinding display
    - Category grouping
    """

    DEFAULT_CSS = """
    CommandPalette {
        align: center top;
        padding-top: 5;
    }

    #palette-container {
        width: 70;
        max-width: 90%;
        height: auto;
        max-height: 60%;
        background: #141414;
        border: thick #fab283;
    }

    #palette-input-container {
        height: 3;
        padding: 0 1;
        background: #1a1a1a;
        border-bottom: solid #333333;
    }

    #palette-input {
        width: 100%;
    }

    #palette-list {
        height: auto;
        max-height: 50;
        padding: 1;
    }

    #palette-empty {
        text-align: center;
        color: #808080;
        padding: 2;
    }

    #palette-hint {
        height: 1;
        padding: 0 1;
        background: #1a1a1a;
        border-top: solid #333333;
        color: #808080;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
    ]

    # Reactive
    filter_text: reactive[str] = reactive("")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._commands: List[Command] = []
        self._filtered_commands: List[Command] = []

    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        with Container(id="palette-container"):
            with Container(id="palette-input-container"):
                yield Input(
                    placeholder="Type to search commands...",
                    id="palette-input",
                )

            yield ListView(id="palette-list")
            yield Static("No commands found", id="palette-empty")

            yield Static(
                "↑↓ Navigate │ Enter Select │ Esc Close",
                id="palette-hint",
            )

    def on_mount(self) -> None:
        """Called when mounted."""
        self._register_commands()
        self._update_list()

        # Focus input
        self.query_one("#palette-input", Input).focus()

    def _register_commands(self) -> None:
        """Register available commands."""
        self._commands = [
            # Session commands
            Command(
                id="session.new",
                title="New Session",
                description="Create a new chat session",
                keybind="Ctrl+N",
                category="Session",
                icon="📝",
                action=lambda: self.app.action_new_session(),
            ),
            Command(
                id="session.list",
                title="Switch Session",
                description="Switch to another session",
                keybind="Ctrl+S",
                category="Session",
                icon="📋",
                action=lambda: self.app.action_switch_session(),
            ),
            Command(
                id="session.clear",
                title="Clear Messages",
                description="Clear all messages in current session",
                keybind="Ctrl+L",
                category="Session",
                icon="🗑",
            ),

            # Model commands - Direct model switching
            Command(
                id="model.gpt4o",
                title="GPT-4o (OpenAI)",
                description="Most capable GPT-4 model",
                category="Model",
                icon="🟢",
                action=lambda: self._set_model("gpt-4o"),
            ),
            Command(
                id="model.gpt4o-mini",
                title="GPT-4o Mini (OpenAI)",
                description="Smaller, faster GPT-4o",
                category="Model",
                icon="🟢",
                action=lambda: self._set_model("gpt-4o-mini"),
            ),
            Command(
                id="model.claude-sonnet",
                title="Claude 3.5 Sonnet (Anthropic)",
                description="Best balance of speed and intelligence",
                category="Model",
                icon="🟣",
                action=lambda: self._set_model("claude-3-5-sonnet-latest"),
            ),
            Command(
                id="model.claude-opus",
                title="Claude 3 Opus (Anthropic)",
                description="Most powerful Claude model",
                category="Model",
                icon="🟣",
                action=lambda: self._set_model("claude-3-opus-latest"),
            ),
            Command(
                id="model.llama",
                title="Llama 3.2 (Ollama)",
                description="Local model via Ollama",
                category="Model",
                icon="🦙",
                action=lambda: self._set_model("llama3.2"),
            ),
            Command(
                id="model.groq",
                title="Llama 3.1 70B (Groq)",
                description="Fast inference with Groq",
                category="Model",
                icon="⚡",
                action=lambda: self._set_model("llama-3.1-70b-versatile"),
            ),

            # Theme commands
            Command(
                id="theme.cycle",
                title="Cycle Theme",
                description="Switch to next theme",
                keybind="Ctrl+T",
                category="Theme",
                icon="🎨",
                action=lambda: self.app.action_cycle_theme(),
            ),
            Command(
                id="theme.dark",
                title="Dark Theme",
                description="Switch to dark theme",
                category="Theme",
                icon="🌙",
            ),
            Command(
                id="theme.light",
                title="Light Theme",
                description="Switch to light theme",
                category="Theme",
                icon="☀️",
            ),
            Command(
                id="theme.catppuccin",
                title="Catppuccin Theme",
                description="Switch to Catppuccin Mocha theme",
                category="Theme",
                icon="🐱",
            ),
            Command(
                id="theme.dracula",
                title="Dracula Theme",
                description="Switch to Dracula theme",
                category="Theme",
                icon="🧛",
            ),

            # View commands
            Command(
                id="view.sidebar",
                title="Toggle Sidebar",
                description="Show/hide the sidebar",
                category="View",
                icon="📊",
            ),
            Command(
                id="view.thinking",
                title="Toggle Thinking",
                description="Show/hide AI thinking process",
                category="View",
                icon="💭",
            ),

            # App commands
            Command(
                id="app.settings",
                title="Settings",
                description="Open settings dialog",
                keybind="Ctrl+,",
                category="App",
                icon="⚙️",
                action=lambda: self.app.action_open_settings(),
            ),
            Command(
                id="app.help",
                title="Help",
                description="Show help information",
                keybind="F1",
                category="App",
                icon="❓",
                action=lambda: self.app.action_toggle_help(),
            ),
            Command(
                id="app.quit",
                title="Quit",
                description="Exit the application",
                keybind="Ctrl+Q",
                category="App",
                icon="🚪",
                action=lambda: self.app.action_quit(),
            ),
        ]

        self._filtered_commands = self._commands.copy()

    def _update_list(self) -> None:
        """Update the command list based on filter."""
        list_view = self.query_one("#palette-list", ListView)
        empty_state = self.query_one("#palette-empty", Static)

        list_view.clear()

        # Filter commands
        if self.filter_text:
            query = self.filter_text.lower()
            self._filtered_commands = [
                cmd for cmd in self._commands
                if query in cmd.title.lower()
                or query in cmd.description.lower()
                or query in cmd.category.lower()
            ]
        else:
            self._filtered_commands = self._commands.copy()

        # Update display
        if self._filtered_commands:
            empty_state.display = False
            list_view.display = True

            for cmd in self._filtered_commands:
                item = CommandItem(cmd)
                list_view.append(item)
        else:
            empty_state.display = True
            list_view.display = False

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        self.filter_text = event.value
        self._update_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle command selection."""
        if isinstance(event.item, CommandItem):
            self._execute_command(event.item.command)

    def action_select(self) -> None:
        """Select the highlighted command."""
        list_view = self.query_one("#palette-list", ListView)
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, CommandItem):
            self._execute_command(list_view.highlighted_child.command)

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        list_view = self.query_one("#palette-list", ListView)
        list_view.action_cursor_up()

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        list_view = self.query_one("#palette-list", ListView)
        list_view.action_cursor_down()

    def _execute_command(self, command: Command) -> None:
        """Execute a command."""
        self.dismiss()

        if command.action:
            command.action()
        else:
            # Handle commands without explicit action
            self._handle_command(command.id)

    def _handle_command(self, command_id: str) -> None:
        """Handle command by ID."""
        handlers = {
            "session.clear": self._clear_session,
            "model.gpt4o": lambda: self._set_model("gpt-4o"),
            "model.claude": lambda: self._set_model("claude-3-5-sonnet-latest"),
            "theme.dark": lambda: self._set_theme("dark"),
            "theme.light": lambda: self._set_theme("light"),
            "theme.catppuccin": lambda: self._set_theme("catppuccin"),
            "theme.dracula": lambda: self._set_theme("dracula"),
            "view.sidebar": self._toggle_sidebar,
            "view.thinking": self._toggle_thinking,
        }

        if command_id in handlers:
            handlers[command_id]()
        else:
            self.app.notify(f"Command: {command_id}")

    def _clear_session(self) -> None:
        """Clear current session messages."""
        session = self.app.get_current_session()
        if session:
            self.app.messages[session.id] = []
            session.message_count = 0
            self.app.notify("Messages cleared")

    def _set_model(self, model: str) -> None:
        """Set the model."""
        self.app.current_model = model
        self.app.notify(f"Model: {model}")

    def _set_theme(self, theme: str) -> None:
        """Set the theme."""
        self.app.theme_name = theme
        self.app.notify(f"Theme: {theme}")

    def _toggle_sidebar(self) -> None:
        """Toggle sidebar."""
        self.app.show_sidebar = not self.app.show_sidebar
        self.app.notify("Sidebar toggled")

    def _toggle_thinking(self) -> None:
        """Toggle thinking display."""
        self.app.notify("Toggle thinking: Coming soon!")

    def action_close(self) -> None:
        """Close the palette."""
        self.dismiss()

    def watch_filter_text(self, value: str) -> None:
        """React to filter text changes."""
        self._update_list()
