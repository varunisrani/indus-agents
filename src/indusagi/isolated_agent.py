"""
Helpers for running each Agent inside its own worker thread with isolated
resources (provider connection, tool registry, context).
"""

from __future__ import annotations

import queue
import threading
import time
from typing import Any, Callable, Optional

from indusagi.agent import Agent
from indusagi.handoff_queue import HandoffMessage, HandoffQueue
from indusagi.tools import ToolRegistry, registry as global_tool_registry


class IsolatedAgent:
    """
    Wraps an Agent so it can run inside a dedicated thread with isolated tools.

    Each isolated agent:
      - Forks the global ToolRegistry to avoid shared state/collisions.
      - Clones tool context for branch-local mutations.
      - Processes messages pulled from the HandoffQueue.
      - Pushes responses (including pending handoffs) back to the coordinator.
    """

    def __init__(
        self,
        agent: Agent,
        handoff_queue: HandoffQueue,
        *,
        max_turns: Optional[int] = None,
        event_callback: Optional[Callable[[dict], None]] = None,
        tools: Optional[list] = None,
    ) -> None:
        self.agent = agent
        self.handoff_queue = handoff_queue
        self.max_turns = max_turns
        self.event_callback = event_callback
        self.tools = tools  # Full tools list including handoff_to_agent
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._run_loop,
            name=f"{agent.name}-thread",
            daemon=True,
        )

        # Give this agent its own tool registry/context.
        self.tool_registry: ToolRegistry = global_tool_registry.fork(
            name=f"{agent.name}-registry",
            is_parallel_branch=False,
        )
        self.agent.context = self.tool_registry.context

    def start(self) -> None:
        """Start the agent thread."""
        self._thread.start()

    def join(self, timeout: Optional[float] = None) -> None:
        """Wait for the agent thread to finish."""
        self._thread.join(timeout=timeout)

    def _run_loop(self) -> None:
        """Main worker loop: receive tasks, run agent, send responses."""
        while not self._stop_event.is_set():
            try:
                message = self.handoff_queue.receive_for_agent(self.agent.name, timeout=0.5)
            except queue.Empty:
                continue

            if message.type == "shutdown":
                break

            start_time = time.time()
            response_text = ""
            success = True
            error = None

            try:
                # Use the full tools list (including handoff) if provided, else registry schemas
                tools_to_use = self.tools if self.tools is not None else self.tool_registry.schemas
                response_text = self.agent.process_with_tools(
                    message.content,
                    tools=tools_to_use,
                    tool_executor=self.tool_registry,
                    max_turns=self.max_turns,
                    event_callback=self.event_callback,
                )
            except Exception as exc:  # pragma: no cover - defensive
                success = False
                error = str(exc)
                response_text = f"[ERROR] {exc}"
            finally:
                processing_time = time.time() - start_time

            pending_handoff = getattr(self.tool_registry, "_pending_handoff", None)
            # Reset pending handoff for the next request
            self.tool_registry._pending_handoff = None

            payload: dict[str, Any] = {
                "agent": self.agent.name,
                "response": response_text,
                "success": success,
                "error": error,
                "processing_time": processing_time,
                "pending_handoff": pending_handoff,
            }

            reply_to = message.reply_to or "coordinator"
            reply = HandoffMessage(
                type="handoff_response",
                from_agent=self.agent.name,
                to_agent=reply_to,
                content=payload,
                message_id=message.message_id,
            )
            # Deliver response to the waiter (coordinator) using message_id correlation
            delivered = self.handoff_queue.deliver_response(reply)
            if not delivered:
                # Fallback: send to agent queue if no waiter exists
                self.handoff_queue.send_to_agent(reply)

        self._stop_event.set()

    def stop(self) -> None:
        """Signal the thread to shut down (coordinator also sends shutdown message)."""
        self._stop_event.set()
