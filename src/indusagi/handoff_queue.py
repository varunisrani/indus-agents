"""
Thread-safe handoff queue for coordinating isolated agent threads.

Agents exchange `HandoffMessage` instances via dedicated queues so every agent
has an isolated communication channel. Coordinators can also wait for specific
responses by message_id (used to correlate replies with requests).
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class HandoffMessage:
    """
    Message payload exchanged between coordinator and agents.

    Attributes:
        type: Semantic type: "task", "handoff_request", "handoff_response", "shutdown".
        from_agent: Sender agent name (or "coordinator").
        to_agent: Target agent name (or "coordinator").
        content: Arbitrary payload (prompt text, summary, etc.).
        message_id: Unique identifier so responses can correlate with requests.
        reply_to: Optional name of agent expected to receive follow-up responses.
    """

    type: str
    from_agent: str
    to_agent: str
    content: Any
    message_id: str
    reply_to: Optional[str] = None


class HandoffQueue:
    """Central broker that routes messages between agents and coordinator."""

    def __init__(self) -> None:
        self._agent_queues: Dict[str, "queue.Queue[HandoffMessage]"] = {}
        self._response_waiters: Dict[str, "queue.Queue[HandoffMessage]"] = {}
        self._lock = threading.Lock()

    def register_agent(self, agent_name: str) -> None:
        """Ensure an agent has a dedicated inbound queue."""
        with self._lock:
            if agent_name not in self._agent_queues:
                self._agent_queues[agent_name] = queue.Queue()

    def send_to_agent(self, message: HandoffMessage) -> None:
        """Send a message to the target agent."""
        with self._lock:
            if message.to_agent not in self._agent_queues:
                self._agent_queues[message.to_agent] = queue.Queue()
            target_queue = self._agent_queues[message.to_agent]
        target_queue.put(message)

    def receive_for_agent(
        self, agent_name: str, timeout: Optional[float] = None
    ) -> HandoffMessage:
        """Blocking receive for a specific agent."""
        with self._lock:
            if agent_name not in self._agent_queues:
                self._agent_queues[agent_name] = queue.Queue()
            agent_queue = self._agent_queues[agent_name]
        return agent_queue.get(timeout=timeout)

    def register_response_waiter(self, message_id: str) -> None:
        """Prepare a response queue for a future reply."""
        with self._lock:
            if message_id not in self._response_waiters:
                self._response_waiters[message_id] = queue.Queue(maxsize=1)

    def deliver_response(self, message: HandoffMessage) -> bool:
        """
        Deliver a response to the waiter that is tracking the message_id.

        Returns:
            True if a waiter consumed the response, False if no waiter exists.
        """
        with self._lock:
            waiter = self._response_waiters.get(message.message_id)
        if waiter:
            waiter.put(message)
            return True
        return False

    def wait_for_response(
        self, message_id: str, timeout: Optional[float] = None
    ) -> Optional[HandoffMessage]:
        """
        Block until the response identified by message_id arrives or timeout expires.
        """
        with self._lock:
            waiter = self._response_waiters.setdefault(message_id, queue.Queue(maxsize=1))
        try:
            return waiter.get(timeout=timeout)
        except queue.Empty:
            return None
        finally:
            with self._lock:
                self._response_waiters.pop(message_id, None)
