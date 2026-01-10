"""
Indus CLI - Main Application

The main TUI application class that orchestrates all components.
Modeled after OpenCode's provider-based architecture.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import json
import time
import os

LOG_PATH = r"c:\Users\Varun israni\indus-agents\.cursor\debug.log"


def _safe_debug_log(payload: dict) -> None:
    """Write a single NDJSON line to the debug log, creating the directory if needed."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as _dbg_file:
            _dbg_file.write(json.dumps(payload) + "\n")
    except Exception:
        pass

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive, var
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, Input, Label
from textual.message import Message
from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class SessionData:
    """Represents a chat session."""
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    model: str = "gpt-4o"
    agent: str = "default"
    message_count: int = 0


@dataclass
class MessageData:
    """Represents a chat message."""
    id: str
    session_id: str
    role: str  # "user", "assistant", "tool", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_name: Optional[str] = None
    tool_result: Optional[str] = None
    is_streaming: bool = False
    is_error: bool = False


# ============================================================================
# Custom Events/Messages
# ============================================================================

class SessionCreated(Message):
    """Fired when a new session is created."""
    def __init__(self, session: SessionData) -> None:
        self.session = session
        super().__init__()


class SessionSelected(Message):
    """Fired when a session is selected."""
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__()


class MessageSubmitted(Message):
    """Fired when user submits a message."""
    def __init__(self, content: str, session_id: str) -> None:
        self.content = content
        self.session_id = session_id
        super().__init__()


class StreamingToken(Message):
    """Fired when a streaming token is received."""
    def __init__(self, token: str, message_id: str) -> None:
        self.token = token
        self.message_id = message_id
        super().__init__()


class ToolExecuting(Message):
    """Fired when a tool starts executing."""
    def __init__(self, tool_name: str, tool_args: Dict[str, Any]) -> None:
        self.tool_name = tool_name
        self.tool_args = tool_args
        super().__init__()


class ToolCompleted(Message):
    """Fired when a tool finishes executing."""
    def __init__(self, tool_name: str, result: str, success: bool = True) -> None:
        self.tool_name = tool_name
        self.result = result
        self.success = success
        super().__init__()


# ============================================================================
# Main Application
# ============================================================================

class IndusApp(App):
    """
    Indus CLI - Terminal User Interface for IndusAGI.

    A modern, feature-rich TUI providing:
    - Interactive chat sessions with AI agents
    - Real-time streaming response display
    - Tool execution visualization
    - Multi-session management
    - Customizable themes and keybindings
    - Command palette for quick actions
    """

    # App metadata
    TITLE = "Indus CLI"
    SUB_TITLE = "AI Agent Interface"

    # CSS files for theming
    CSS_PATH = [
        Path(__file__).parent / "themes" / "base.tcss",
        Path(__file__).parent / "themes" / "dark.tcss",
    ]

    # Default CSS for main layout
    DEFAULT_CSS = """
    Screen {
        background: #0d0d0d;
    }

    #main-container {
        height: 1fr;
        background: #0d0d0d;
    }

    Header {
        background: #1a1a1a;
        color: #fab283;
    }

    Footer {
        background: #1a1a1a;
    }

    FooterKey {
        background: #2a2a2a;
        color: #fab283;
    }
    """

    # Key bindings
    BINDINGS = [
        Binding("ctrl+p", "toggle_command_palette", "Commands", show=True),
        Binding("ctrl+n", "new_session", "New", show=True),
        Binding("ctrl+s", "switch_session", "Sessions", show=False),
        Binding("ctrl+m", "select_model", "Model", show=True),
        Binding("ctrl+t", "cycle_theme", "Theme", show=False),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("escape", "cancel", "Back", show=False),
        Binding("f1", "toggle_help", "Help", show=False),
    ]

    # Reactive state
    current_session_id: reactive[Optional[str]] = reactive(None)
    current_model: reactive[str] = reactive("gpt-4o")
    current_provider: reactive[str] = reactive("OpenAI")
    current_agent: reactive[str] = reactive("default")
    theme_name: reactive[str] = reactive("dark")  # Note: can't use theme_name (reserved by Textual)
    is_processing: reactive[bool] = reactive(False)
    show_sidebar: reactive[bool] = reactive(True)

    def __init__(
        self,
        model: Optional[str] = None,
        agent: Optional[str] = None,
        session: Optional[str] = None,
        theme: Optional[str] = None,
    ):
        """
        Initialize the Indus CLI application.

        Args:
            model: Default model to use (e.g., "gpt-4o")
            agent: Default agent to use
            session: Session ID to resume
            theme: Theme name (dark, light, catppuccin, etc.)
        """
        super().__init__()

        # Configuration
        if model:
            self.current_model = model
        if agent:
            self.current_agent = agent
        if theme:
            self.theme_name = theme

        # State
        self.sessions: Dict[str, SessionData] = {}
        self.messages: Dict[str, List[MessageData]] = {}
        self.agent_bridge = None  # Initialized on mount

        # Resume session if specified
        self._initial_session = session

    def compose(self) -> ComposeResult:
        """Compose the main UI layout."""
        yield Header(show_clock=True)
        yield Container(id="main-container")
        yield Footer()

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Import here to avoid circular imports
        from indusagi.tui.core.agent_bridge import AgentBridge
        from indusagi.tui.screens.home import HomeScreen
        from indusagi.tui.screens.session import SessionScreen

        # Initialize agent bridge with provider
        try:
            self.agent_bridge = AgentBridge(
                model=self.current_model,
                provider=self.current_provider,
                agent=self.current_agent,
                use_agency=True,  # Use multi-agent system
            )
            self.notify(f"Agency initialized: {self.agent_bridge.get_current_agent()}")
        except Exception as e:
            self.notify(f"Failed to initialize agent: {e}", severity="error")
            self.agent_bridge = None

        # Install screens
        self.install_screen(HomeScreen(), name="home")
        self.install_screen(SessionScreen(), name="session")

        # Push initial screen
        if self._initial_session and self._initial_session in self.sessions:
            self.current_session_id = self._initial_session
            await self.push_screen("session")
        else:
            await self.push_screen("home")

    # ========================================================================
    # Session Management
    # ========================================================================

    def create_session(self, name: Optional[str] = None) -> SessionData:
        """Create a new chat session."""
        import uuid

        session_id = f"ses_{uuid.uuid4().hex[:8]}"
        session_name = name or f"Session {len(self.sessions) + 1}"

        session = SessionData(
            id=session_id,
            name=session_name,
            model=self.current_model,
            agent=self.current_agent,
        )

        self.sessions[session_id] = session
        self.messages[session_id] = []

        self.post_message(SessionCreated(session))
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def get_current_session(self) -> Optional[SessionData]:
        """Get the currently active session."""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None

    def get_session_messages(self, session_id: str) -> List[MessageData]:
        """Get all messages for a session."""
        return self.messages.get(session_id, [])

    # ========================================================================
    # Message Handling
    # ========================================================================

    def add_message(self, session_id: str, message: MessageData) -> None:
        """Add a message to a session."""
        if session_id not in self.messages:
            self.messages[session_id] = []
        self.messages[session_id].append(message)

        # Update session
        if session_id in self.sessions:
            self.sessions[session_id].message_count += 1
            self.sessions[session_id].updated_at = datetime.now()

    async def send_message(self, content: str) -> None:
        """Send a message in the current session."""
        import uuid

        if not self.current_session_id:
            self.notify("No active session", severity="warning")
            return

        if self.is_processing:
            self.notify("Already processing a message", severity="warning")
            return

        self.is_processing = True

        try:
            # Add user message
            user_msg = MessageData(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                session_id=self.current_session_id,
                role="user",
                content=content,
            )
            self.add_message(self.current_session_id, user_msg)

            # Post message submitted event
            self.post_message(MessageSubmitted(content, self.current_session_id))

            # Create assistant message
            assistant_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
            assistant_msg = MessageData(
                id=assistant_msg_id,
                session_id=self.current_session_id,
                role="assistant",
                content="",
                is_streaming=True,
            )
            self.add_message(self.current_session_id, assistant_msg)

            # Process with agent
            if self.agent_bridge:
                try:
                    first_token_logged = False
                    #region agent log
                    _safe_debug_log({
                        "sessionId": "debug-session",
                        "runId": "post-fix",
                        "hypothesisId": "H0-app",
                        "location": "tui.IndusApp.send_message",
                        "message": "stream_start",
                        "data": {"content_len": len(content)},
                        "timestamp": int(time.time() * 1000)
                    })
                    #endregion agent log
                    # Stream response
                    async for event in self.agent_bridge.stream_response(content):
                        if event["type"] == "token":
                            # Update message content
                            assistant_msg.content += event.get("content", "")
                            if not first_token_logged:
                                #region agent log
                                _safe_debug_log({
                                    "sessionId": "debug-session",
                                    "runId": "post-fix",
                                    "hypothesisId": "H4",
                                    "location": "tui.IndusApp.send_message",
                                    "message": "first_token_received",
                                    "data": {"length": len(event.get("content", ""))},
                                    "timestamp": int(time.time() * 1000)
                                })
                                #endregion agent log
                                first_token_logged = True
                            self.post_message(StreamingToken(event.get("content", ""), assistant_msg_id))
                        elif event["type"] == "tool_call":
                            # Update assistant message tool call list so SessionScreen can render it
                            tool_call_id = event.get("id")
                            tool_name = event.get("name", "unknown")
                            tool_args = event.get("arguments", {}) or {}
                            if tool_call_id:
                                assistant_msg.tool_calls.append({
                                    "id": tool_call_id,
                                    "name": tool_name,
                                    "arguments": tool_args,
                                    "status": "running",
                                    "result": None,
                                })
                            self.post_message(ToolExecuting(
                                event["name"],
                                event.get("arguments", {})
                            ))
                            # Force a UI refresh tick (SessionScreen will re-render)
                            self.refresh()
                        elif event["type"] == "tool_result":
                            tool_call_id = event.get("id")
                            tool_name = event.get("name", "unknown")
                            tool_result = event.get("result", "")
                            tool_success = event.get("success", True)
                            if tool_call_id:
                                for tc in assistant_msg.tool_calls:
                                    if tc.get("id") == tool_call_id:
                                        tc["status"] = "success" if tool_success else "error"
                                        tc["result"] = tool_result
                                        break
                            self.post_message(ToolCompleted(
                                event["name"],
                                event.get("result", ""),
                                event.get("success", True)
                            ))
                            self.refresh()
                        elif event["type"] == "agent_start":
                            # Show which agent is starting (like terminal_demo)
                            agent = event.get("agent", "Unknown")
                            assistant_msg.content += f"\n[dim]▶ Starting with [{agent}]...[/dim]\n"
                            self.post_message(StreamingToken(f"\n▶ Starting with {agent}...\n", assistant_msg_id))
                            self.refresh()
                        elif event["type"] == "agent_switch":
                            # Show handoff between agents (like terminal_demo HANDOFF logs)
                            from_agent = event.get("from_agent")
                            to_agent = event.get("to_agent", "Unknown")
                            if from_agent:
                                log_msg = f"\n[dim]HANDOFF: [{from_agent}] → [{to_agent}][/dim]\n"
                            else:
                                log_msg = f"\n[dim]▶ [{to_agent}] is working...[/dim]\n"
                            assistant_msg.content += log_msg
                            self.post_message(StreamingToken(log_msg, assistant_msg_id))
                            self.refresh()
                        elif event["type"] == "error":
                            # Log error but continue to get error message
                            error_text = str(event.get('error', 'Unknown'))[:100]
                            # Escape Rich markup characters
                            error_text = error_text.replace("[", "\\[").replace("]", "\\]")
                            self.notify(f"Agent error: {error_text}", severity="warning")
                        elif event["type"] == "done":
                            assistant_msg.is_streaming = False
                            # Force UI refresh to display the completed message
                            self.refresh()
                except Exception as e:
                    assistant_msg.content = f"Error processing message: {e}\n\nPlease check your API key in Settings (Ctrl+P → settings)."
                    assistant_msg.is_error = True
                    assistant_msg.is_streaming = False
                    self.refresh()  # Force UI refresh on error
            else:
                # No agent bridge available
                assistant_msg.content = "No AI provider configured.\n\nPlease configure your API key in Settings (Ctrl+P → settings)."
                assistant_msg.is_error = True
                assistant_msg.is_streaming = False
                self.refresh()  # Force UI refresh

        except Exception as e:
            error_text = str(e)[:100].replace("[", "\\[").replace("]", "\\]")
            self.notify(f"Error: {error_text}", severity="error")
        finally:
            self.is_processing = False
            # Always refresh UI after processing completes
            self.refresh()

    # ========================================================================
    # Actions
    # ========================================================================

    def action_new_session(self) -> None:
        """Create a new session and switch to it."""
        session = self.create_session()
        self.current_session_id = session.id
        self.push_screen("session")
        self.notify(f"Created: {session.name}")

    def action_switch_session(self) -> None:
        """Show session list dialog."""
        from indusagi.tui.widgets.dialog.session_list import SessionListDialog
        self.push_screen(SessionListDialog())

    def action_toggle_command_palette(self) -> None:
        """Toggle the command palette."""
        from indusagi.tui.widgets.dialog.command_palette import CommandPalette
        self.push_screen(CommandPalette())

    def action_select_model(self) -> None:
        """Show model selection dialog."""
        from indusagi.tui.widgets.dialog.model_select import ModelSelectDialog
        self.push_screen(ModelSelectDialog())

    def action_cycle_theme(self) -> None:
        """Cycle through available themes."""
        themes = ["dark", "light", "catppuccin", "dracula"]
        current_index = themes.index(self.theme_name) if self.theme_name in themes else 0
        next_index = (current_index + 1) % len(themes)
        self.theme_name = themes[next_index]
        self.notify(f"Theme: {self.theme_name}")
        # Reload CSS would go here

    def action_toggle_help(self) -> None:
        """Show help dialog."""
        self.notify("Press Ctrl+P for command palette")

    def action_open_settings(self) -> None:
        """Open settings dialog."""
        from indusagi.tui.widgets.dialog.settings import SettingsDialog
        self.push_screen(SettingsDialog())

    def action_cancel(self) -> None:
        """Cancel current operation or close dialog."""
        if len(self.screen_stack) > 1:
            self.pop_screen()

    # ========================================================================
    # Watchers
    # ========================================================================

    def watch_theme_name(self, theme: str) -> None:
        """React to theme changes."""
        # Update CSS path based on theme
        theme_file = Path(__file__).parent / "themes" / f"{theme}.tcss"
        if theme_file.exists():
            # Would reload CSS here
            pass

    def watch_current_model(self, model: str) -> None:
        """React to model changes."""
        if self.agent_bridge:
            self.agent_bridge.set_model(model, self.current_provider)

    def watch_current_provider(self, provider: str) -> None:
        """React to provider changes."""
        if self.agent_bridge:
            self.agent_bridge.set_model(self.current_model, provider)


# ============================================================================
# Entry Point
# ============================================================================

def run_tui(
    model: Optional[str] = None,
    agent: Optional[str] = None,
    session: Optional[str] = None,
    theme: Optional[str] = None,
) -> None:
    """
    Run the Indus CLI TUI.

    Args:
        model: Default model to use
        agent: Default agent to use
        session: Session ID to resume
        theme: Theme name
    """
    app = IndusApp(
        model=model,
        agent=agent,
        session=session,
        theme=theme,
    )
    app.run()


if __name__ == "__main__":
    run_tui()
