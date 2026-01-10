"""
Session Manager for Indus CLI TUI.

Handles session persistence, loading, and management.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from indusagi.tui.core.state import SessionData, MessageData, MessageRole


@dataclass
class SessionFile:
    """Metadata for a session file."""
    id: str
    name: str
    model: str
    agent: str
    created_at: str
    updated_at: str
    message_count: int


class SessionManager:
    """
    Manages session persistence and lifecycle.

    Features:
    - Save/load sessions to disk
    - Session history management
    - Auto-save functionality
    - Session export/import
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the session manager.

        Args:
            data_dir: Directory for storing session data.
                     Defaults to ~/.indusagi/sessions/
        """
        if data_dir is None:
            data_dir = Path.home() / ".indusagi" / "sessions"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_index_file = self.data_dir / "index.json"
        self._sessions_cache: Dict[str, SessionData] = {}

    # ========================================================================
    # Session CRUD
    # ========================================================================

    def create_session(
        self,
        name: Optional[str] = None,
        model: str = "gpt-4o",
        agent: str = "default",
    ) -> SessionData:
        """Create a new session."""
        session_id = f"ses_{uuid.uuid4().hex[:8]}"
        session_name = name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        session = SessionData(
            id=session_id,
            name=session_name,
            model=model,
            agent=agent,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self._sessions_cache[session_id] = session
        self._update_index()

        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get a session by ID."""
        # Check cache first
        if session_id in self._sessions_cache:
            return self._sessions_cache[session_id]

        # Try to load from disk
        session_file = self._get_session_file(session_id)
        if session_file.exists():
            return self._load_session_from_file(session_file)

        return None

    def list_sessions(self) -> List[SessionData]:
        """List all sessions."""
        self._load_index()
        return list(self._sessions_cache.values())

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions_cache:
            del self._sessions_cache[session_id]

        # Delete files
        session_file = self._get_session_file(session_id)
        messages_file = self._get_messages_file(session_id)

        if session_file.exists():
            session_file.unlink()
        if messages_file.exists():
            messages_file.unlink()

        self._update_index()
        return True

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a session."""
        session = self.get_session(session_id)
        if session:
            session.name = new_name
            session.updated_at = datetime.now()
            self.save_session(session)
            return True
        return False

    # ========================================================================
    # Persistence
    # ========================================================================

    def save_session(self, session: SessionData) -> None:
        """Save a session to disk."""
        self._sessions_cache[session.id] = session

        # Save session metadata
        session_file = self._get_session_file(session.id)
        session_data = {
            "id": session.id,
            "name": session.name,
            "model": session.model,
            "agent": session.agent,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": session.message_count,
            "total_tokens": session.total_tokens,
        }
        session_file.write_text(json.dumps(session_data, indent=2))

        self._update_index()

    def save_messages(self, session_id: str, messages: List[MessageData]) -> None:
        """Save messages for a session."""
        messages_file = self._get_messages_file(session_id)

        messages_data = []
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "session_id": msg.session_id,
                "role": msg.role.value if isinstance(msg.role, MessageRole) else msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "is_error": msg.is_error,
                "model": msg.model,
                "tokens_used": msg.tokens_used,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": tc.arguments,
                        "result": tc.result,
                        "status": tc.status,
                    }
                    for tc in msg.tool_calls
                ] if msg.tool_calls else [],
            }
            messages_data.append(msg_dict)

        messages_file.write_text(json.dumps(messages_data, indent=2))

        # Update session message count
        session = self.get_session(session_id)
        if session:
            session.message_count = len(messages)
            session.updated_at = datetime.now()
            self.save_session(session)

    def load_messages(self, session_id: str) -> List[MessageData]:
        """Load messages for a session."""
        messages_file = self._get_messages_file(session_id)

        if not messages_file.exists():
            return []

        try:
            data = json.loads(messages_file.read_text())
            messages = []

            for msg_dict in data:
                msg = MessageData(
                    id=msg_dict["id"],
                    session_id=msg_dict["session_id"],
                    role=MessageRole(msg_dict["role"]) if msg_dict["role"] in [r.value for r in MessageRole] else msg_dict["role"],
                    content=msg_dict["content"],
                    timestamp=datetime.fromisoformat(msg_dict["timestamp"]),
                    is_error=msg_dict.get("is_error", False),
                    model=msg_dict.get("model"),
                    tokens_used=msg_dict.get("tokens_used", 0),
                )
                messages.append(msg)

            return messages
        except Exception as e:
            print(f"Error loading messages: {e}")
            return []

    # ========================================================================
    # Export/Import
    # ========================================================================

    def export_session(self, session_id: str, output_path: Path) -> bool:
        """Export a session to a file."""
        session = self.get_session(session_id)
        if not session:
            return False

        messages = self.load_messages(session_id)

        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "session": {
                "id": session.id,
                "name": session.name,
                "model": session.model,
                "agent": session.agent,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
            },
            "messages": [
                {
                    "role": msg.role.value if isinstance(msg.role, MessageRole) else msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in messages
            ],
        }

        output_path.write_text(json.dumps(export_data, indent=2))
        return True

    def export_session_markdown(self, session_id: str, output_path: Path) -> bool:
        """Export a session as Markdown."""
        session = self.get_session(session_id)
        if not session:
            return False

        messages = self.load_messages(session_id)

        lines = [
            f"# {session.name}",
            "",
            f"**Model:** {session.model}",
            f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
        ]

        for msg in messages:
            role = msg.role.value.upper() if isinstance(msg.role, MessageRole) else msg.role.upper()
            lines.append(f"### {role}")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
            lines.append("---")
            lines.append("")

        output_path.write_text("\n".join(lines))
        return True

    def import_session(self, input_path: Path) -> Optional[SessionData]:
        """Import a session from a file."""
        try:
            data = json.loads(input_path.read_text())

            # Create new session with imported data
            session = self.create_session(
                name=data["session"]["name"] + " (imported)",
                model=data["session"]["model"],
                agent=data["session"].get("agent", "default"),
            )

            # Import messages
            messages = []
            for msg_data in data.get("messages", []):
                msg = MessageData(
                    id=f"msg_{uuid.uuid4().hex[:8]}",
                    session_id=session.id,
                    role=MessageRole(msg_data["role"]),
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]) if "timestamp" in msg_data else datetime.now(),
                )
                messages.append(msg)

            self.save_messages(session.id, messages)
            return session

        except Exception as e:
            print(f"Error importing session: {e}")
            return None

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.data_dir / f"{session_id}.json"

    def _get_messages_file(self, session_id: str) -> Path:
        """Get the file path for session messages."""
        return self.data_dir / f"{session_id}_messages.json"

    def _load_session_from_file(self, session_file: Path) -> Optional[SessionData]:
        """Load a session from a file."""
        try:
            data = json.loads(session_file.read_text())
            session = SessionData(
                id=data["id"],
                name=data["name"],
                model=data.get("model", "gpt-4o"),
                agent=data.get("agent", "default"),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                message_count=data.get("message_count", 0),
                total_tokens=data.get("total_tokens", 0),
            )
            self._sessions_cache[session.id] = session
            return session
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def _load_index(self) -> None:
        """Load the sessions index."""
        if not self.sessions_index_file.exists():
            return

        try:
            data = json.loads(self.sessions_index_file.read_text())
            for session_id in data.get("sessions", []):
                if session_id not in self._sessions_cache:
                    session_file = self._get_session_file(session_id)
                    if session_file.exists():
                        self._load_session_from_file(session_file)
        except Exception as e:
            print(f"Error loading index: {e}")

    def _update_index(self) -> None:
        """Update the sessions index."""
        index_data = {
            "updated_at": datetime.now().isoformat(),
            "sessions": list(self._sessions_cache.keys()),
        }
        self.sessions_index_file.write_text(json.dumps(index_data, indent=2))


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
