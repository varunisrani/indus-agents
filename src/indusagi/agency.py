"""
Agency - Multi-Agent Orchestration System

Provides Agency Swarm-like orchestration for indus-agents.
"""
import os
import uuid
from typing import List, Dict, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import concurrent.futures as futures

from indusagi.agent import Agent
from indusagi.tool_usage_logger import tool_logger
from indusagi.handoff_queue import HandoffQueue, HandoffMessage
from indusagi.isolated_agent import IsolatedAgent


class HandoffType(Enum):
    """Types of agent handoff mechanisms."""
    MESSAGE = "message"
    FULL_CONTEXT = "full_context"


@dataclass
class HandoffResult:
    """Result of an agent handoff."""
    success: bool
    response: str
    from_agent: str
    to_agent: str
    processing_time: float
    error: Optional[str] = None


@dataclass
class ParallelResult:
    """Result of a parallel branch execution."""
    agent: str
    response: str
    processing_time: float
    success: bool
    error: Optional[str] = None


@dataclass
class AgencyResponse:
    """Response from agency processing."""
    response: str
    agents_used: List[str]
    handoffs: List[HandoffResult]
    total_time: float
    final_agent: str
    parallel_results: Optional[List[ParallelResult]] = None


class Agency:
    """
    Multi-agent orchestration system with defined communication flows.

    Similar to Agency Swarm's Agency class, this manages multiple agents
    and their inter-communication patterns.

    Example:
        >>> planner = create_planner_agent()
        >>> coder = create_coder_agent()
        >>> agency = Agency(
        ...     entry_agent=coder,
        ...     agents=[coder, planner],
        ...     communication_flows=[
        ...         (coder, planner),  # coder can hand off to planner
        ...         (planner, coder),  # planner can hand off to coder
        ...     ],
        ...     name="DevAgency",
        ...     shared_instructions="./project-overview.md"
        ... )
        >>> response = agency.process("Build a REST API")
    """

    def __init__(
        self,
        entry_agent: Agent,
        agents: Optional[List[Agent]] = None,
        communication_flows: Optional[List[Tuple[Agent, Agent]]] = None,
        shared_instructions: Optional[str] = None,
        name: str = "Agency",
        max_handoffs: int = 10,
        max_turns: Optional[int] = 100,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Any] = None,
        use_thread_pool: bool = False,
        thread_response_timeout: float = 600.0,
    ):
        """
        Initialize an Agency.

        Args:
            entry_agent: The agent that receives initial user input
            agents: List of all agents in the agency
            communication_flows: List of (source, target) tuples defining allowed handoffs
            shared_instructions: Path to shared instructions file
            name: Name of this agency
            max_handoffs: Maximum number of handoffs allowed per request
            max_turns: Maximum number of tool-calling iterations per agent. None uses default of 1000. (default: 100)
            tools: List of tool schemas for function calling
            tool_executor: Tool executor instance
        """
        self.entry_agent = entry_agent
        self.name = name
        self.max_handoffs = max_handoffs
        # Handle None max_turns - use large default (1000)
        self.max_turns = 1000 if max_turns is None else max_turns
        self.tools = tools or []
        self.tool_executor = tool_executor
        self.use_thread_pool = use_thread_pool
        self.thread_response_timeout = thread_response_timeout

        # Build agent registry
        self.agents = agents or [entry_agent]
        self._agent_map: Dict[str, Agent] = {a.name: a for a in self.agents}

        # Build communication graph
        self._flows: Dict[str, List[str]] = {}
        if communication_flows:
            for source, target in communication_flows:
                if source.name not in self._flows:
                    self._flows[source.name] = []
                self._flows[source.name].append(target.name)

        # Load shared instructions
        self._shared_context = ""
        if shared_instructions and os.path.exists(shared_instructions):
            with open(shared_instructions, "r") as f:
                self._shared_context = f.read()

        # Shared state across all agents
        self._shared_state: Dict[str, Any] = {}

        # Handoff history for current request
        self._handoff_history: List[HandoffResult] = []

        # Thread-pool mode helpers
        self.handoff_queue: Optional[HandoffQueue] = None
        self._isolated_agents: Dict[str, IsolatedAgent] = {}
        if self.use_thread_pool:
            self._initialize_thread_pool()

    def _initialize_thread_pool(self) -> None:
        """Spin up isolated agent threads and their shared handoff queue."""
        self.handoff_queue = HandoffQueue()
        self.handoff_queue.register_agent("coordinator")
        for agent in self.agents:
            self.handoff_queue.register_agent(agent.name)
            isolated = IsolatedAgent(
                agent,
                self.handoff_queue,
                max_turns=self.max_turns,
                tools=self.tools,  # Pass full tools list including handoff_to_agent
            )
            self._isolated_agents[agent.name] = isolated
            isolated.start()

    def shutdown(self) -> None:
        """Gracefully stop agent threads (only relevant in thread-pool mode)."""
        if not self.use_thread_pool or not self.handoff_queue:
            return

        for agent in self.agents:
            shutdown_message = HandoffMessage(
                type="shutdown",
                from_agent="coordinator",
                to_agent=agent.name,
                content="shutdown",
                message_id=str(uuid.uuid4()),
            )
            self.handoff_queue.send_to_agent(shutdown_message)

        for isolated in self._isolated_agents.values():
            isolated.join(timeout=2.0)

    def _run_agent_threadpool_call(
        self,
        agent: Agent,
        message: str,
        emit: Callable[[dict], None],
    ) -> Tuple[str, bool, Optional[str], float, Optional[Dict[str, Any]]]:
        """Dispatch work to an isolated agent thread and wait for the result."""
        if not self.handoff_queue:
            raise RuntimeError("Thread pool not initialized")
        isolated = self._isolated_agents.get(agent.name)
        if not isolated:
            raise ValueError(f"No isolated agent for {agent.name}")

        isolated.event_callback = emit
        message_id = str(uuid.uuid4())
        self.handoff_queue.register_response_waiter(message_id)
        task = HandoffMessage(
            type="task",
            from_agent="coordinator",
            to_agent=agent.name,
            content=message,
            message_id=message_id,
            reply_to="coordinator",
        )
        self.handoff_queue.send_to_agent(task)

        response_msg = self.handoff_queue.wait_for_response(
            message_id, timeout=self.thread_response_timeout
        )
        if response_msg is None:
            raise TimeoutError(
                f"Timed out waiting for agent '{agent.name}' response in thread pool mode"
            )

        payload = response_msg.content or {}
        response_text = payload.get("response", "")
        success = payload.get("success", True)
        error = payload.get("error")
        processing_time = float(payload.get("processing_time", 0.0))
        pending_handoff = payload.get("pending_handoff")

        return response_text, success, error, processing_time, pending_handoff

    def _run_parallel_threadpool(
        self,
        targets: List[Agent],
        message: str,
        emit: Callable[[dict], None],
    ) -> Tuple[List[ParallelResult], List[Tuple[str, Dict[str, Any]]]]:
        """
        Send the same message to several agents concurrently and gather results.

        Returns:
            branch_results: List of ParallelResult with status per agent.
            pending_handoffs: List of (agent_name, handoff_dict) for unexpected handoffs.
        """
        if not self.handoff_queue:
            raise RuntimeError("Thread pool not initialized")

        pending_ids: List[Tuple[str, Agent]] = []
        for agent in targets:
            isolated = self._isolated_agents.get(agent.name)
            if not isolated:
                continue
            isolated.event_callback = emit
            message_id = str(uuid.uuid4())
            self.handoff_queue.register_response_waiter(message_id)
            task = HandoffMessage(
                type="task",
                from_agent="coordinator",
                to_agent=agent.name,
                content=message,
                message_id=message_id,
                reply_to="coordinator",
            )
            self.handoff_queue.send_to_agent(task)
            pending_ids.append((message_id, agent))

        branch_results: List[ParallelResult] = []
        pending_handoffs: List[Tuple[str, Dict[str, Any]]] = []
        for message_id, agent in pending_ids:
            response_msg = self.handoff_queue.wait_for_response(
                message_id, timeout=self.thread_response_timeout
            )
            if response_msg is None:
                branch_results.append(
                    ParallelResult(
                        agent=agent.name,
                        response="[Timeout]",
                        processing_time=self.thread_response_timeout,
                        success=False,
                        error="Timeout waiting for response",
                    )
                )
                continue

            payload = response_msg.content or {}
            pending = payload.get("pending_handoff")
            if pending:
                pending_handoffs.append((agent.name, pending))

            branch_results.append(
                ParallelResult(
                    agent=agent.name,
                    response=payload.get("response", ""),
                    processing_time=float(payload.get("processing_time", 0.0)),
                    success=payload.get("success", True),
                    error=payload.get("error"),
                )
            )

        return branch_results, pending_handoffs

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return self._agent_map.get(name)

    def list_agents(self) -> List[str]:
        """List all agent names in the agency."""
        return list(self._agent_map.keys())

    def can_handoff(self, from_agent: str, to_agent: str) -> bool:
        """Check if handoff is allowed between agents."""
        return to_agent in self._flows.get(from_agent, [])

    def get_allowed_handoffs(self, agent_name: str) -> List[str]:
        """Get list of agents this agent can hand off to."""
        return self._flows.get(agent_name, [])

    def handoff(
        self,
        from_agent: Agent,
        to_agent_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HandoffResult:
        """
        Execute a handoff from one agent to another.

        Args:
            from_agent: The agent initiating the handoff
            to_agent_name: Name of the target agent
            message: Message to pass to target agent
            context: Optional additional context

        Returns:
            HandoffResult with response and metadata
        """
        start_time = time.time()

        if not self.can_handoff(from_agent.name, to_agent_name):
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=0,
                error=f"Handoff from {from_agent.name} to {to_agent_name} not allowed"
            )

        target = self._agent_map.get(to_agent_name)
        if not target:
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=0,
                error=f"Agent {to_agent_name} not found"
            )

        # Build handoff message with context
        full_message = f"[Handoff from {from_agent.name}]\n\n{message}"

        if self._shared_context:
            full_message = f"[Shared Project Context]\n{self._shared_context}\n\n{full_message}"

        if context:
            context_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
            full_message += f"\n\n[Additional Context]\n{context_str}"

        try:
            response = target.process(full_message)
            processing_time = time.time() - start_time

            result = HandoffResult(
                success=True,
                response=response,
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=processing_time
            )
            self._handoff_history.append(result)
            return result

        except Exception as e:
            return HandoffResult(
                success=False,
                response="",
                from_agent=from_agent.name,
                to_agent=to_agent_name,
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def process(
        self,
        user_input: str,
        use_tools: bool = True,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Any] = None,
        on_max_turns_reached: Optional[Callable[[], bool]] = None,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> AgencyResponse:
        """
        Process user input through the agency.

        Starts with entry_agent and handles any handoffs.

        Args:
            user_input: The user's request
            use_tools: Whether to enable tool usage
            tools: List of tool schemas (optional)
            tool_executor: Tool executor instance (optional)
            on_max_turns_reached: Optional callback that returns bool to continue after max_turns

        Returns:
            AgencyResponse with full processing details
        """
        start_time = time.time()
        root_user_request = user_input

        def emit(event: Dict[str, Any]) -> None:
            if event_callback:
                try:
                    event_callback(event)
                except Exception:
                    pass
        self._handoff_history = []
        agents_used = [self.entry_agent.name]
        parallel_results: List[ParallelResult] = []
        tool_list = tools or self.tools

        # Add shared context to initial message
        full_input = user_input
        if self._shared_context:
            full_input = f"[Project Context]\n{self._shared_context}\n\n[User Request]\n{user_input}"

        # Process with entry agent - use tools if enabled
        current_agent = self.entry_agent
        current_message = full_input
        response = ""
        handoff_count = 0

        # Match terminal_demo style: show "Starting with [Coder]" and then "[Coder] is working"
        emit({"type": "agent_start", "agent": current_agent.name})
        emit({"type": "agent_switch", "from_agent": None, "to_agent": current_agent.name})

        # Loop until no more handoffs or max reached
        continue_processing = True

        while continue_processing and handoff_count < self.max_handoffs:
            # Process with current agent
            handoff_data = None
            if self.use_thread_pool:
                response, _, _, _, handoff_data = self._run_agent_threadpool_call(
                    current_agent,
                    current_message,
                    emit,
                )
            else:
                if use_tools and tools is not None:
                    response = current_agent.process_with_tools(
                        current_message,
                        tools=tool_list,
                        tool_executor=tool_executor,
                        max_turns=self.max_turns,
                        on_max_turns_reached=on_max_turns_reached,
                        event_callback=emit,
                    )
                else:
                    response = current_agent.process(current_message)
                if tool_executor and hasattr(tool_executor, "_pending_handoff"):
                    handoff_data = tool_executor._pending_handoff
                    tool_executor._pending_handoff = None  # clear for next turn

            emit({
                "type": "agent_progress",
                "agent": current_agent.name,
                "event": "response_complete",
                "preview": str(response)[:200]
            })

            # If no handoff requested, we're done processing
            if not handoff_data:
                continue_processing = False
                break

            handoff_mode = handoff_data.get("mode", "single")

            if handoff_mode == "parallel":
                # Fan-out to multiple agents concurrently
                raw_targets = handoff_data.get("agent_names", []) or []
                aggregation_target = handoff_data.get("aggregation_target") or self.entry_agent.name
                handoff_message = handoff_data.get("message", "")
                handoff_context = handoff_data.get("context")

                # Validate targets
                allowed_targets = []
                for t in raw_targets:
                    if not self.can_handoff(current_agent.name, t):
                        emit({
                            "type": "warning",
                            "warning": f"Handoff from {current_agent.name} to {t} not allowed",
                            "from_agent": current_agent.name,
                            "to_agent": t,
                        })
                        continue
                    target_agent = self._agent_map.get(t)
                    if not target_agent:
                        emit({
                            "type": "warning",
                            "warning": f"Target agent {t} not found",
                            "from_agent": current_agent.name,
                            "to_agent": t,
                        })
                        continue
                    allowed_targets.append(target_agent)

                if not allowed_targets:
                    continue_processing = False
                    break

                # Emit parallel start event with clear console logging
                from rich.console import Console
                console = Console()
                console.print(f"\n[bold bright_cyan]╔══════════════════════════════════ PARALLEL EXECUTION START ══════════════════════════════════╗[/bold bright_cyan]")
                console.print(f"[bright_cyan]║[/bright_cyan] [bold]From Agent:[/bold] {current_agent.name}")
                console.print(f"[bright_cyan]║[/bright_cyan] [bold]Target Agents:[/bold] {', '.join([a.name for a in allowed_targets])}")
                console.print(f"[bright_cyan]║[/bright_cyan] [bold]Message:[/bold] {handoff_message[:80]}{'...' if len(handoff_message) > 80 else ''}")
                console.print(f"[bright_cyan]╚══════════════════════════════════════════════════════════════════════════════════════════════╝[/bright_cyan]\n")
                emit({"type": "parallel_start", "from_agent": current_agent.name, "targets": [a.name for a in allowed_targets]})

                def build_branch_message() -> str:
                    msg = f"[Handoff from {current_agent.name}]\n\n{handoff_message}"
                    if handoff_context:
                        msg += f"\n\n[Additional Context]\n{handoff_context}"
                    if self._shared_context:
                        msg = f"[Shared Context]\n{self._shared_context}\n\n{msg}"
                    return msg

                branch_message = build_branch_message()
                active_tools = tool_list
                branch_results: List[ParallelResult] = []

                if self.use_thread_pool:
                    branch_results, pending_handoffs = self._run_parallel_threadpool(
                        allowed_targets,
                        branch_message,
                        emit,
                    )
                    from rich.console import Console
                    console = Console()
                    for agent_name, pending in pending_handoffs:
                        console.print(f"[yellow]WARNING: {agent_name} attempted nested handoff (ignored in parallel mode)[/yellow]")
                        emit({
                            "type": "warning",
                            "warning": f"{agent_name} attempted nested handoff (ignored in parallel mode)",
                            "from_agent": agent_name,
                        })
                else:
                    def run_branch(agent: Agent, branch_executor: Any) -> ParallelResult:
                        from rich.console import Console
                        console = Console()
                        console.print(f"[bright_yellow]▶ Starting parallel branch: [bold]{agent.name}[/bold][/bright_yellow]")
                        emit({"type": "parallel_branch_start", "agent": agent.name})
                        start_branch = time.time()
                        success = True
                        error = None
                        try:
                            branch_response = agent.process_with_tools(
                                branch_message,
                                tools=active_tools,
                                tool_executor=branch_executor,
                                max_turns=self.max_turns,
                                on_max_turns_reached=on_max_turns_reached,
                                event_callback=emit,
                            )
                        except Exception as e:  # pragma: no cover - defensive
                            branch_response = str(e)
                            success = False
                            error = str(e)
                        processing_time = time.time() - start_branch
                        from rich.console import Console
                        console = Console()
                        status_icon = "✓" if success else "✗"
                        status_color = "green" if success else "red"
                        console.print(f"[{status_color}]{status_icon} Completed parallel branch: [bold]{agent.name}[/bold] ({processing_time:.2f}s)[/{status_color}]")
                        emit({
                            "type": "parallel_branch_end",
                            "agent": agent.name,
                            "success": success,
                            "duration": processing_time,
                        })
                        # Clear any nested handoff request from the branch; parallel branches don't cascade handoffs
                        if hasattr(branch_executor, "_pending_handoff"):
                            if branch_executor._pending_handoff:
                                console.print(f"[yellow]WARNING: {agent.name} attempted nested handoff (ignored in parallel mode)[/yellow]")
                            branch_executor._pending_handoff = None
                        return ParallelResult(
                            agent=agent.name,
                            response=branch_response,
                            processing_time=processing_time,
                            success=success,
                            error=error,
                        )

                    with futures.ThreadPoolExecutor(max_workers=len(allowed_targets)) as executor_pool:
                        future_map = {
                            executor_pool.submit(run_branch, agent, tool_executor.fork(name=f"{agent.name}-branch")): agent.name
                            for agent in allowed_targets
                        }
                        for future in futures.as_completed(future_map):
                            branch_results.append(future.result())

                parallel_results.extend(branch_results)

                # Print parallel execution summary
                from rich.console import Console
                from rich.table import Table
                console = Console()
                console.print(f"\n[bold bright_cyan]╔════════════════════════════════ PARALLEL EXECUTION COMPLETE ═════════════════════════════════╗[/bold bright_cyan]")
                
                summary_table = Table(show_header=True, header_style="bold bright_cyan", border_style="bright_cyan")
                summary_table.add_column("Agent", style="bold")
                summary_table.add_column("Status", justify="center")
                summary_table.add_column("Duration", justify="right")
                
                for r in branch_results:
                    status = "[green]✓ Success[/green]" if r.success else f"[red]✗ Error: {r.error}[/red]"
                    summary_table.add_row(r.agent, status, f"{r.processing_time:.2f}s")
                
                console.print(summary_table)
                console.print(f"[bright_cyan]╚══════════════════════════════════════════════════════════════════════════════════════════════╝[/bright_cyan]\n")

                emit({
                    "type": "parallel_end",
                    "from_agent": current_agent.name,
                    "targets": [a.name for a in allowed_targets],
                    "results": [
                        {"agent": r.agent, "success": r.success, "duration": r.processing_time}
                        for r in branch_results
                    ],
                })

                # Build aggregation step back to aggregator target (default Coder)
                aggregator_agent = self._agent_map.get(aggregation_target, self.entry_agent)
                if current_agent != aggregator_agent and not self.can_handoff(current_agent.name, aggregator_agent.name):
                    from rich.console import Console
                    console = Console()
                    console.print(f"[yellow]WARNING: Handoff from {current_agent.name} to {aggregator_agent.name} not allowed; staying with {current_agent.name}[/yellow]")
                    emit({
                        "type": "warning",
                        "warning": f"Handoff from {current_agent.name} to {aggregator_agent.name} not allowed; staying with {current_agent.name}",
                        "from_agent": current_agent.name,
                        "to_agent": aggregator_agent.name,
                    })
                    aggregator_agent = current_agent

                summary_lines = [
                    "[Parallel Results]",
                    f"- Original request: {root_user_request}",
                    f"- Handoff message: {handoff_message}",
                ]
                for r in branch_results:
                    status = "OK" if r.success else f"ERROR: {r.error}"
                    summary_lines.append(f"\nAgent: {r.agent} ({status}, {r.processing_time:.2f}s)\n{r.response}")

                aggregation_prompt = "\n".join(summary_lines)
                aggregation_prompt += (
                    "\n\nPlease merge these outputs, resolve conflicts, and decide the next best step. "
                    "If additional work is needed, continue with tool calls or handoffs."
                )

                from rich.console import Console
                console = Console()
                console.print(f"\n[bold bright_magenta]→ Aggregating results in: [bold]{aggregator_agent.name}[/bold][/bold bright_magenta]\n")
                
                emit({"type": "agent_switch", "from_agent": current_agent.name, "to_agent": aggregator_agent.name})
                current_agent = aggregator_agent
                current_message = aggregation_prompt
                agents_used.append(current_agent.name)
                handoff_count += 1
                continue_processing = True
                continue

            # --- Single handoff (existing path) ---
            handoff_target = handoff_data.get('agent_name')
            handoff_message = handoff_data.get('message', '')
            handoff_context = handoff_data.get('context')

            # Validate handoff is allowed
            if not self.can_handoff(current_agent.name, handoff_target):
                emit({
                    "type": "warning",
                    "warning": f"Handoff from {current_agent.name} to {handoff_target} not allowed",
                    "from_agent": current_agent.name,
                    "to_agent": handoff_target,
                })
                continue_processing = False
                break

            # Get target agent
            target_agent = self._agent_map.get(handoff_target)
            if not target_agent:
                emit({
                    "type": "warning",
                    "warning": f"Target agent {handoff_target} not found",
                    "from_agent": current_agent.name,
                    "to_agent": handoff_target,
                })
                continue_processing = False
                break

            # Execute handoff
            # Prepare message for target agent
            current_message = f"[Handoff from {current_agent.name}]\n\n{handoff_message}"
            if handoff_context:
                current_message += f"\n\n[Additional Context]\n{handoff_context}"
            if self._shared_context:
                current_message = f"[Shared Context]\n{self._shared_context}\n\n{current_message}"

            # Update current agent and continue loop to process with new agent
            emit({"type": "agent_switch", "from_agent": current_agent.name, "to_agent": target_agent.name})
            current_agent = target_agent
            agents_used.append(current_agent.name)
            handoff_count += 1
            # continue_processing stays True - loop will continue with new agent

        return AgencyResponse(
            response=response,
            agents_used=agents_used,
            handoffs=self._handoff_history,
            total_time=time.time() - start_time,
            final_agent=agents_used[-1],
            parallel_results=parallel_results if parallel_results else None,
        )

    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """Get a value from shared state."""
        return self._shared_state.get(key, default)

    def set_shared_state(self, key: str, value: Any) -> None:
        """Set a value in shared state."""
        self._shared_state[key] = value

    def clear_shared_state(self) -> None:
        """Clear all shared state."""
        self._shared_state = {}

    def terminal_demo(self, show_reasoning: bool = False):
        """
        Run interactive terminal demo.

        Args:
            show_reasoning: Whether to show agent reasoning
        """
        # Rich-based UI for a cleaner, TUI-like demo experience.
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.prompt import Prompt
        from rich.markdown import Markdown
        from rich.theme import Theme
        from rich import box

        theme = Theme({
            "banner": "bold bright_cyan",
            "agent_name": "bold bright_blue",
            "user": "bold blue",
            "tool": "bold yellow",
            "success": "bold green",
            "warning": "yellow",
            "error": "bold red",
            "dim": "dim white",
            "box_border": "bright_cyan",
        })
        console = Console(theme=theme)

        agents = self.list_agents()
        header = (
            f"[banner]{self.name}[/banner]\n"
            f"[dim]Multi-Agent Interactive Demo[/dim]\n\n"
            f"[dim]Agents:[/dim] [agent_name]{', '.join(agents)}[/agent_name]\n"
            f"[dim]Entry:[/dim] [agent_name]{self.entry_agent.name}[/agent_name]\n"
            f"[dim]Max handoffs:[/dim] {self.max_handoffs}    [dim]Max turns:[/dim] {self.max_turns}\n"
        )
        console.print()
        console.print(Panel(
            header,
            box=box.DOUBLE_EDGE,
            border_style="box_border",
            padding=(1, 2),
            width=80,
        ))

        commands_md = (
            "**Commands**\n"
            "- `/quit`, `/exit`: Exit\n"
            "- `/agents`: List agents\n"
            "- `/handoffs`: Show allowed handoffs\n"
            "- `/clear`: Clear conversation history\n"
            "- `/logs`: Show recent tool usage\n"
            "- `/stats`: Tool usage statistics\n"
            "- `/export`: Export tool logs to JSON\n"
        )
        console.print(Panel(Markdown(commands_md), border_style="dim", box=box.ROUNDED, width=80))
        console.print()

        while True:
            try:
                user_input = Prompt.ask("[user]You[/user]").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["/quit", "/exit"]:
                    console.print("[dim]Goodbye![/dim]")
                    break

                if user_input.lower() == "/agents":
                    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
                    table.add_column("Agents", style="agent_name")
                    for a in self.list_agents():
                        table.add_row(a)
                    console.print(Panel(table, title="[banner]Agents[/banner]", border_style="box_border"))
                    continue

                if user_input.lower() == "/handoffs":
                    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
                    table.add_column("From", style="agent_name", width=16)
                    table.add_column("Allowed handoffs", style="white")
                    for agent in self.agents:
                        targets = self.get_allowed_handoffs(agent.name)
                        table.add_row(agent.name, ", ".join(targets) if targets else "(none)")
                    console.print(Panel(table, title="[banner]Allowed Handoffs[/banner]", border_style="box_border"))
                    continue

                if user_input.lower() == "/clear":
                    for agent in self.agents:
                        agent.clear_history()
                    console.print("[success]Conversation history cleared.[/success]")
                    continue

                if user_input.lower() == "/logs":
                    tool_logger.print_recent_calls(limit=10)
                    continue

                if user_input.lower() == "/stats":
                    tool_logger.print_statistics()
                    continue

                if user_input.lower() == "/export":
                    filename = f"tool_logs_{int(time.time())}.json"
                    tool_logger.export_to_json(filename)
                    continue

                # Process the request
                result = self.process(
                    user_input,
                    use_tools=True,
                    tools=self.tools if self.tools else None,
                    tool_executor=self.tool_executor
                )

                footer = f"[dim]Time:[/dim] {result.total_time:.2f}s"
                if result.handoffs:
                    footer += f"    [dim]Handoffs:[/dim] {len(result.handoffs)}"

                console.print()
                console.print(Panel(
                    Markdown(result.response or "*No response generated*"),
                    title=f"[agent_name]{result.final_agent}[/agent_name]",
                    subtitle=footer,
                    border_style="agent_name",
                    box=box.ROUNDED,
                    padding=(1, 2),
                    width=80,
                ))
                console.print()

            except KeyboardInterrupt:
                console.print("\n[dim]Goodbye![/dim]")
                break
            except Exception as e:
                console.print(Panel(str(e), title="[error]Error[/error]", border_style="error", box=box.ROUNDED))
                console.print()

    def visualize(self) -> str:
        """
        Generate ASCII visualization of the agency structure.

        Returns:
            ASCII art representation of agents and flows
        """
        lines = [
            f"Agency: {self.name}",
            "=" * 40,
            "",
            "Agents:",
        ]

        for agent in self.agents:
            marker = ">" if agent == self.entry_agent else " "
            lines.append(f"  {marker} {agent.name}")

        lines.append("")
        lines.append("Communication Flows:")

        for source, targets in self._flows.items():
            for target in targets:
                lines.append(f"  {source} -> {target}")

        if not self._flows:
            lines.append("  (none defined)")

        return "\n".join(lines)
