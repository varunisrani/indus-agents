"""
State Management for Indus CLI TUI.

Provides reactive state management similar to OpenCode's sync.tsx pattern.
Uses dataclasses and observer pattern for state updates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import json
from pathlib import Path


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class SessionStatus(str, Enum):
    """Session status types."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class ToolCallData:
    """Represents a tool call within a message."""
    id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    status: str = "pending"  # pending, running, success, error
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class MessageData:
    """Represents a chat message."""
    id: str
    session_id: str
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: List[ToolCallData] = field(default_factory=list)
    is_streaming: bool = False
    is_error: bool = False
    error_message: Optional[str] = None
    model: Optional[str] = None
    tokens_used: int = 0

    @classmethod
    def create_user_message(cls, session_id: str, content: str) -> "MessageData":
        """Create a user message."""
        return cls(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            role=MessageRole.USER,
            content=content,
        )

    @classmethod
    def create_assistant_message(cls, session_id: str, model: Optional[str] = None) -> "MessageData":
        """Create an empty assistant message (for streaming)."""
        return cls(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content="",
            is_streaming=True,
            model=model,
        )


@dataclass
class SessionData:
    """Represents a chat session."""
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    model: str = "gpt-4o"
    agent: str = "default"
    status: SessionStatus = SessionStatus.IDLE
    message_count: int = 0
    total_tokens: int = 0

    @classmethod
    def create(cls, name: Optional[str] = None, model: str = "gpt-4o", agent: str = "default") -> "SessionData":
        """Create a new session."""
        session_id = f"ses_{uuid.uuid4().hex[:8]}"
        return cls(
            id=session_id,
            name=name or f"Session {session_id[-4:]}",
            model=model,
            agent=agent,
        )


@dataclass
class ProviderConfig:
    """LLM provider configuration."""
    name: str
    api_key_env: str
    models: List[str]
    is_available: bool = False


@dataclass
class AppState:
    """
    Central application state.

    Similar to OpenCode's sync.tsx store structure.
    """
    # Sessions
    sessions: Dict[str, SessionData] = field(default_factory=dict)
    current_session_id: Optional[str] = None

    # Messages (keyed by session_id)
    messages: Dict[str, List[MessageData]] = field(default_factory=dict)

    # Providers
    providers: List[ProviderConfig] = field(default_factory=list)
    current_provider: str = "openai"
    current_model: str = "gpt-4o"

    # Agent
    current_agent: str = "default"

    # UI State
    theme: str = "dark"
    show_sidebar: bool = True
    show_thinking: bool = False
    show_timestamps: bool = True

    # Processing
    is_processing: bool = False

    def get_current_session(self) -> Optional[SessionData]:
        """Get the current session."""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None

    def get_session_messages(self, session_id: str) -> List[MessageData]:
        """Get messages for a session."""
        return self.messages.get(session_id, [])

    def get_current_messages(self) -> List[MessageData]:
        """Get messages for the current session."""
        if self.current_session_id:
            return self.get_session_messages(self.current_session_id)
        return []


class StateManager:
    """
    Manages application state with observer pattern.

    Provides methods for state updates and notifies listeners.
    Similar to OpenCode's reconcile() pattern for efficient updates.
    """

    def __init__(self, initial_state: Optional[AppState] = None):
        """Initialize state manager."""
        self.state = initial_state or AppState()
        self._listeners: Dict[str, Set[Callable]] = {}

    # ========================================================================
    # Observer Pattern
    # ========================================================================

    def subscribe(self, event: str, callback: Callable) -> Callable:
        """Subscribe to state changes."""
        if event not in self._listeners:
            self._listeners[event] = set()
        self._listeners[event].add(callback)

        # Return unsubscribe function
        def unsubscribe():
            self._listeners[event].discard(callback)
        return unsubscribe

    def notify(self, event: str, data: Any = None) -> None:
        """Notify listeners of state change."""
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in state listener: {e}")

    # ========================================================================
    # Session Management
    # ========================================================================

    def create_session(self, name: Optional[str] = None) -> SessionData:
        """Create a new session."""
        session = SessionData.create(
            name=name,
            model=self.state.current_model,
            agent=self.state.current_agent,
        )
        self.state.sessions[session.id] = session
        self.state.messages[session.id] = []

        self.notify("session_created", session)
        return session

    def select_session(self, session_id: str) -> bool:
        """Select a session as current."""
        if session_id in self.state.sessions:
            self.state.current_session_id = session_id
            self.notify("session_selected", session_id)
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.state.sessions:
            del self.state.sessions[session_id]
            if session_id in self.state.messages:
                del self.state.messages[session_id]
            if self.state.current_session_id == session_id:
                self.state.current_session_id = None
            self.notify("session_deleted", session_id)
            return True
        return False

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a session."""
        if session_id in self.state.sessions:
            self.state.sessions[session_id].name = new_name
            self.state.sessions[session_id].updated_at = datetime.now()
            self.notify("session_updated", session_id)
            return True
        return False

    # ========================================================================
    # Message Management
    # ========================================================================

    def add_message(self, message: MessageData) -> None:
        """Add a message to a session."""
        session_id = message.session_id
        if session_id not in self.state.messages:
            self.state.messages[session_id] = []

        self.state.messages[session_id].append(message)

        # Update session
        if session_id in self.state.sessions:
            session = self.state.sessions[session_id]
            session.message_count += 1
            session.updated_at = datetime.now()

        self.notify("message_added", message)

    def update_message(self, message_id: str, **updates) -> bool:
        """Update a message by ID."""
        for session_id, messages in self.state.messages.items():
            for i, msg in enumerate(messages):
                if msg.id == message_id:
                    for key, value in updates.items():
                        if hasattr(msg, key):
                            setattr(msg, key, value)
                    self.notify("message_updated", msg)
                    return True
        return False

    def append_to_message(self, message_id: str, content: str) -> bool:
        """Append content to a streaming message."""
        for session_id, messages in self.state.messages.items():
            for msg in messages:
                if msg.id == message_id:
                    msg.content += content
                    self.notify("message_streaming", {"id": message_id, "content": content})
                    return True
        return False

    def complete_message(self, message_id: str, tokens_used: int = 0) -> bool:
        """Mark a message as complete (stop streaming)."""
        return self.update_message(
            message_id,
            is_streaming=False,
            tokens_used=tokens_used,
        )

    # ========================================================================
    # Tool Call Management
    # ========================================================================

    def add_tool_call(self, message_id: str, tool_call: ToolCallData) -> bool:
        """Add a tool call to a message."""
        for session_id, messages in self.state.messages.items():
            for msg in messages:
                if msg.id == message_id:
                    msg.tool_calls.append(tool_call)
                    self.notify("tool_call_added", {"message_id": message_id, "tool_call": tool_call})
                    return True
        return False

    def update_tool_call(self, message_id: str, tool_call_id: str, **updates) -> bool:
        """Update a tool call status."""
        for session_id, messages in self.state.messages.items():
            for msg in messages:
                if msg.id == message_id:
                    for tc in msg.tool_calls:
                        if tc.id == tool_call_id:
                            for key, value in updates.items():
                                if hasattr(tc, key):
                                    setattr(tc, key, value)
                            self.notify("tool_call_updated", {"message_id": message_id, "tool_call": tc})
                            return True
        return False

    # ========================================================================
    # UI State
    # ========================================================================

    def set_processing(self, is_processing: bool) -> None:
        """Set processing state."""
        self.state.is_processing = is_processing
        if self.state.current_session_id:
            session = self.state.sessions.get(self.state.current_session_id)
            if session:
                session.status = SessionStatus.PROCESSING if is_processing else SessionStatus.IDLE
        self.notify("processing_changed", is_processing)

    def set_theme(self, theme: str) -> None:
        """Set theme."""
        self.state.theme = theme
        self.notify("theme_changed", theme)

    def set_model(self, model: str) -> None:
        """Set current model."""
        self.state.current_model = model
        self.notify("model_changed", model)

    def toggle_sidebar(self) -> bool:
        """Toggle sidebar visibility."""
        self.state.show_sidebar = not self.state.show_sidebar
        self.notify("sidebar_toggled", self.state.show_sidebar)
        return self.state.show_sidebar

    # ========================================================================
    # Persistence
    # ========================================================================

    def save_to_file(self, filepath: Path) -> None:
        """Save state to file."""
        data = {
            "sessions": {
                sid: {
                    "id": s.id,
                    "name": s.name,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                    "model": s.model,
                    "agent": s.agent,
                    "message_count": s.message_count,
                }
                for sid, s in self.state.sessions.items()
            },
            "current_session_id": self.state.current_session_id,
            "current_model": self.state.current_model,
            "current_agent": self.state.current_agent,
            "theme": self.state.theme,
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps(data, indent=2))

    def load_from_file(self, filepath: Path) -> bool:
        """Load state from file."""
        if not filepath.exists():
            return False

        try:
            data = json.loads(filepath.read_text())

            # Restore sessions
            for sid, sdata in data.get("sessions", {}).items():
                self.state.sessions[sid] = SessionData(
                    id=sdata["id"],
                    name=sdata["name"],
                    created_at=datetime.fromisoformat(sdata["created_at"]),
                    updated_at=datetime.fromisoformat(sdata["updated_at"]),
                    model=sdata.get("model", "gpt-4o"),
                    agent=sdata.get("agent", "default"),
                    message_count=sdata.get("message_count", 0),
                )
                self.state.messages[sid] = []  # Messages loaded separately

            self.state.current_session_id = data.get("current_session_id")
            self.state.current_model = data.get("current_model", "gpt-4o")
            self.state.current_agent = data.get("current_agent", "default")
            self.state.theme = data.get("theme", "dark")

            return True
        except Exception as e:
            print(f"Error loading state: {e}")
            return False


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get the global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
