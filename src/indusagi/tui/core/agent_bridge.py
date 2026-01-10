"""
Agent Bridge for Indus CLI TUI.

Connects the TUI to IndusAGI's Agency system, supporting:
- Multi-agent architecture (Coder + Planner)
- Tool execution (Bash, Read, Edit, Write, Glob, Grep, TodoWrite)
- Agent handoffs
- Multiple providers (GLM, OpenAI, Anthropic, etc.)
"""

from __future__ import annotations

import os
import asyncio
import threading
import queue
import json
import time
from typing import Optional, Dict, Any, AsyncIterator, List, Callable
from dataclasses import dataclass
from enum import Enum

LOG_PATH = r"c:\Users\Varun israni\indus-agents\.cursor\debug.log"


def _safe_debug_log(payload: dict) -> None:
    """Write a single NDJSON line to the debug log, creating the directory if needed."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as _dbg_file:
            _dbg_file.write(json.dumps(payload) + "\n")
    except Exception:
        pass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use existing env vars

# Import IndusAGI components
from indusagi import Agent, AgentConfig, Agency
from indusagi.tools import Bash, Read, Edit, Write, Glob, Grep, TodoWrite
from indusagi.tools import handoff_to_agent, set_current_agency, registry
from indusagi.memory import ConversationMemory
from indusagi.presets.improved_anthropic_agency import (
    ImprovedAgencyOptions,
    create_improved_agency,
)


class StreamEventType(str, Enum):
    """Types of streaming events."""
    TOKEN = "token"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    AGENT_HANDOFF = "agent_handoff"
    DONE = "done"
    ERROR = "error"


@dataclass
class StreamEvent:
    """A streaming event from the agent."""
    type: StreamEventType
    content: Optional[str] = None
    name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    success: bool = True
    finish_reason: Optional[str] = None
    error: Optional[str] = None


class AgentBridge:
    """
    Bridge between TUI and IndusAGI Agency.

    Creates a multi-agent system with:
    - Coder: Entry agent for code implementation
    - Planner: Strategic planning agent
    - Tools: Bash, Read, Edit, Write, Glob, Grep, TodoWrite
    """

    # Provider configurations
    PROVIDER_CONFIG = {
        "GLM (Z.AI)": {
            "provider": "anthropic",  # GLM uses Anthropic-compatible API via Z.AI
            "api_key_env": "GLM_API_KEY",
            "api_base_env": "GLM_API_BASE",
            "default_base": "https://api.z.ai/api/anthropic",  # Z.AI's Anthropic-compatible endpoint
        },
        "OpenAI": {
            "provider": "openai",
            "api_key_env": "OPENAI_API_KEY",
            "api_base_env": "OPENAI_API_BASE",
            "default_base": "https://api.openai.com/v1",
        },
        "Anthropic": {
            "provider": "anthropic",
            "api_key_env": "ANTHROPIC_API_KEY",
            "api_base_env": "ANTHROPIC_BASE_URL",  # Match what agent.py expects
            "default_base": "https://api.anthropic.com",
        },
        "Groq": {
            "provider": "openai",  # Groq uses OpenAI-compatible API
            "api_key_env": "GROQ_API_KEY",
            "api_base_env": "GROQ_API_BASE",
            "default_base": "https://api.groq.com/openai/v1",
        },
        "Ollama": {
            "provider": "openai",  # Ollama uses OpenAI-compatible API
            "api_key_env": "",
            "api_base_env": "OLLAMA_HOST",
            "default_base": "http://localhost:11434",
        },
    }

    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        agent: Optional[str] = None,
        system_prompt: Optional[str] = None,
        tools_enabled: bool = True,
        use_agency: bool = True,
    ):
        """
        Initialize the agent bridge.

        Args:
            model: Model to use (e.g., "glm-4.7", "gpt-4o")
            provider: Provider name (e.g., "GLM (Z.AI)", "OpenAI")
            agent: Agent name/role
            system_prompt: Custom system prompt
            tools_enabled: Whether to enable tool calling
            use_agency: Whether to use multi-agent Agency
        """
        self.model = model or "glm-4.7"
        self.provider_name = provider or "GLM (Z.AI)"
        self.agent_name = agent or "Coder"
        self.tools_enabled = tools_enabled
        self.use_agency = use_agency

        # Register tools
        self._register_tools()

        # Set up provider configuration
        self._setup_provider()

        # Create agent or agency
        if use_agency:
            self.agency = self._create_agency()
            self.agent = self.agency.entry_agent
        else:
            self.agent = self._create_single_agent()
            self.agency = None

        # Memory
        self.memory = ConversationMemory()

        # Callbacks
        self._on_tool_start: Optional[Callable] = None
        self._on_tool_end: Optional[Callable] = None
        self._on_handoff: Optional[Callable] = None

    def _register_tools(self) -> None:
        """Register available tools."""
        for tool_class in [Bash, Read, Edit, Write, Glob, Grep, TodoWrite]:
            try:
                registry.register(tool_class)
            except Exception:
                pass  # Tool might already be registered

    def _setup_provider(self) -> None:
        """Set up provider environment variables."""
        config = self.PROVIDER_CONFIG.get(self.provider_name, self.PROVIDER_CONFIG["GLM (Z.AI)"])

        # For GLM via Z.AI, set ANTHROPIC env vars from GLM env vars
        if self.provider_name == "GLM (Z.AI)":
            glm_key = os.environ.get("GLM_API_KEY", "")
            glm_base = os.environ.get("GLM_API_BASE", config["default_base"])
            if glm_key:
                os.environ["ANTHROPIC_API_KEY"] = glm_key
            if glm_base:
                os.environ["ANTHROPIC_BASE_URL"] = glm_base  # Match what agent.py expects

    def _get_provider_type(self) -> str:
        """Get the provider type for AgentConfig."""
        config = self.PROVIDER_CONFIG.get(self.provider_name, {})
        return config.get("provider", "anthropic")

    def _create_single_agent(self) -> Agent:
        """Create a single agent."""
        config = AgentConfig(
            model=self.model,
            provider=self._get_provider_type(),
            temperature=0.7,
            max_tokens=8000,
        )

        agent = Agent(
            name=self.agent_name,
            role="Interactive AI assistant for the Indus CLI",
            config=config,
        )
        agent.context = registry.context

        return agent

    def _create_agency(self) -> Agency:
        """Create multi-agent agency like the example (shared preset)."""
        provider_type = self._get_provider_type()

        # Prefer repo prompt files when running from source checkout (matches example scripts).
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
        prompt_dir = os.path.join(project_root, "example_agency_improved_anthropic_prompts")

        coder_prompt_file = os.path.join(prompt_dir, "coder_instructions.md")
        planner_prompt_file = os.path.join(prompt_dir, "planner_instructions.md")

        opts = ImprovedAgencyOptions(
            model=self.model,
            provider=provider_type,
            max_handoffs=100,
            max_turns=1000,
            name="DevAgency_TUI",
            coder_prompt_file=coder_prompt_file if os.path.exists(coder_prompt_file) else None,
            planner_prompt_file=planner_prompt_file if os.path.exists(planner_prompt_file) else None,
        )
        return create_improved_agency(opts)

    def _get_coder_prompt(self) -> str:
        """Get system prompt for Coder agent - loaded from markdown file."""
        # Try to load from markdown file like the example
        prompt_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "example_agency_improved_anthropic_prompts", "coder_instructions.md"),
            os.path.join(os.path.dirname(__file__), "prompts", "coder_instructions.md"),
        ]

        for path in prompt_paths:
            try:
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        return f.read()
            except Exception:
                pass

        # Fallback to embedded prompt
        return """You are a Coder Agent - an interactive CLI tool that helps users with software engineering tasks.

# Tone and Style
- Be concise, direct, and to the point
- Your output will be displayed on a command line interface
- Use Github-flavored markdown for formatting

# Task Management with TodoWrite

CRITICAL: YOU MUST WORK ON TASKS ONE BY ONE

- BEFORE starting ANY complex task (3+ steps), use todo_write to create a task list
- Break down the user's request into specific, actionable todos
- WORKFLOW FOR EACH TASK:
  1. Mark ONLY ONE task as "in_progress"
  2. Execute that SINGLE task using appropriate tool
  3. Mark that task as "completed"
  4. Move to next task

# Planning Mode and Handoffs - WHEN TO USE PLANNER

You must handoff to Planner for complex tasks including:
- Multi-component system architecture (3+ interconnected systems)
- Large-scale refactoring across multiple files/modules
- User explicitly requests planning (e.g., "create plan.md", "plan this project")

When NOT to handoff (handle yourself):
- Simple file creation (HTML, CSS, JS files)
- Basic CRUD operations
- Single file modifications
- Straightforward bug fixes

# Implementation Rules

CRITICAL - FOLDER CREATION:
- Create folders: bash(command="mkdir foldername")
- Create files: write(file_path="foldername/filename.ext", content="...")
- Always Read files before editing them
- Use Edit for modifying existing files
- Use Bash to run tests and build commands

READING PLAN.MD:
When Planner hands back to you:
1. FIRST: Use Read tool to read plan.md
2. Parse the folder structure and file list
3. Use todo_write to create tasks from plan
4. Execute step by step

Available tools:
- todo_write: Manage task list (USE FIRST for complex tasks!)
- Bash: Execute shell commands (mkdir, tests, git)
- Read: Read file contents (REQUIRED before edit)
- Edit: Modify existing files
- Write: Create new files
- Glob: Find files by pattern
- Grep: Search file contents
- handoff_to_agent: Transfer to Planner for complex planning

DO NOT ASK FOR PERMISSION - JUST EXECUTE TASKS DIRECTLY!
Be precise, systematic, and always verify your changes."""

    def _get_planner_prompt(self) -> str:
        """Get system prompt for Planner agent - loaded from markdown file."""
        # Try to load from markdown file like the example
        prompt_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "example_agency_improved_anthropic_prompts", "planner_instructions.md"),
            os.path.join(os.path.dirname(__file__), "prompts", "planner_instructions.md"),
        ]

        for path in prompt_paths:
            try:
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        return f.read()
            except Exception:
                pass

        # Fallback to embedded prompt
        return """# Role and Objective

You are a strategic planning and task breakdown specialist for software development projects. Your mission is to create comprehensive plan.md files that the Coder will execute.

# YOUR WORKFLOW (Follow this EXACT process):

1. Analyze the request - Understand what needs to be built
2. Make smart defaults - Don't ask questions, choose modern best practices
3. Write plan.md file - Use Write tool to create comprehensive plan.md (ONE tool call)
4. Handoff to Coder - Use handoff_to_agent to send to Coder with message "Plan complete. Please implement according to plan.md"

CRITICAL: You do NOT use todo_write! That's for Coder. You use Write tool to create plan.md directly!

# Instructions

DEFAULT: DO NOT ASK QUESTIONS - Make sensible default decisions and start creating plan.md immediately
Make smart defaults: Choose modern, professional defaults for all decisions

## Creating plan.md Files

DO NOT USE todo_write - That's for Coder only! You use Write tool directly!

When requested to create a plan:
1. Immediately use Write tool to create the plan.md file (NO todo_write!)
2. Include in plan.md:
   - Project overview and objectives
   - Folder structure (e.g., "project_name/" as root folder)
   - File breakdown with descriptions
   - Implementation steps in order
   - Testing and validation approach
3. Format: Use clear markdown with sections and bullet points
4. One Write call: Create the entire plan.md in a single Write tool call

## Handoff to Coder

When planning is complete:
- Use handoff_to_agent tool to transfer to Coder with message: "Plan complete. Please implement according to plan.md"

Available tools (USE THESE ONLY):
- Write: Create plan.md files - USE THIS to create plan.md!
- Read: Read existing files for context
- Glob: Find files by pattern
- Grep: Search file contents
- handoff_to_agent: Transfer to Coder for implementation

DO NOT USE: todo_write (that's for Coder only, not for you!)"""

    def set_model(self, model: str, provider: Optional[str] = None) -> None:
        """Change the model and optionally provider."""
        self.model = model
        if provider:
            self.provider_name = provider
            self._setup_provider()

        # Recreate agency/agent
        if self.use_agency:
            self.agency = self._create_agency()
            self.agent = self.agency.entry_agent
        else:
            self.agent = self._create_single_agent()

    def clear_history(self) -> None:
        """Clear conversation history."""
        if self.agent:
            self.agent.clear_history()
        self.memory.clear()

    def on_tool_start(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Set callback for tool start."""
        self._on_tool_start = callback

    def on_tool_end(self, callback: Callable[[str, str, bool], None]) -> None:
        """Set callback for tool end."""
        self._on_tool_end = callback

    def on_handoff(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for agent handoff."""
        self._on_handoff = callback

    async def stream_response(self, message: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream a response from the agent/agency.

        Args:
            message: User message to process

        Yields:
            Stream events
        """
        try:
            # Add user message to memory
            self.memory.add_message("user", message)

            # Process with agency or single agent
            if self.agency:
                async for event in self._process_with_agency(message):
                    yield event
            else:
                async for event in self._process_with_agent(message):
                    yield event

        except Exception as e:
            error_msg = str(e)[:200]
            # Escape markup characters
            safe_error = error_msg.replace("[", "\\[").replace("]", "\\]")
            yield {"type": "error", "error": safe_error}
            yield {
                "type": "token",
                "content": f"Error: {safe_error}\n\nPlease configure your API key in Settings (Ctrl+P -> settings).",
            }
            yield {"type": "done", "finish_reason": "error"}

    async def _process_with_agency(self, message: str) -> AsyncIterator[Dict[str, Any]]:
        """Process message with multi-agent agency with real-time log streaming."""
        # Queue for thread communication
        result_queue: queue.Queue = queue.Queue()
        stop_event = threading.Event()
        first_stream_event_logged = False

        #region agent log
        _safe_debug_log({
            "sessionId": "debug-session",
            "runId": "post-fix",
            "hypothesisId": "H0",
            "location": "agent_bridge._process_with_agency",
            "message": "entry",
            "data": {"message_len": len(message)},
            "timestamp": int(time.time() * 1000)
        })
        #endregion agent log

        def run_agency_in_thread():
            """Run agency in background thread and send events to queue."""
            try:
                # Process message with streaming callback
                result = self.agency.process(
                    message,
                    use_tools=True,
                    tools=self.agency.tools,
                    tool_executor=self.agency.tool_executor,
                    event_callback=lambda ev: result_queue.put(ev)
                )
                #region agent log
                _safe_debug_log({
                    "sessionId": "debug-session",
                    "runId": "post-fix",
                    "hypothesisId": "H2",
                    "location": "agent_bridge.run_agency_in_thread",
                    "message": "agency_process_completed",
                    "data": {
                        "agents_used": getattr(result, "agents_used", None),
                        "handoff_count": len(getattr(result, "handoffs", []) or []),
                        "response_length": len(str(getattr(result, "response", "")) or "")
                    },
                    "timestamp": int(time.time() * 1000)
                })
                #endregion agent log

                # Extract response
                if hasattr(result, 'response'):
                    response = result.response
                else:
                    response = str(result)
                response = str(response) if response else "No response generated."

                # Format response (match example output style)
                if hasattr(result, 'final_agent'):
                    agent_name = result.final_agent
                    formatted_response = f"\n[{agent_name}]\n\n{response}"
                else:
                    formatted_response = response

                if hasattr(result, 'handoffs') and result.handoffs:
                    handoff_info = f"\n\n---\n*Handoffs: {len(result.handoffs)} | Time: {result.total_time:.2f}s*"
                    formatted_response += handoff_info

                # Add to memory (must be done in main thread for thread safety)
                result_queue.put({"type": "memory_add", "role": "assistant", "content": formatted_response})

                # Send result
                result_queue.put({"type": "token", "content": formatted_response})
                result_queue.put({"type": "done", "finish_reason": "stop"})

            except Exception as e:
                error_msg = str(e)[:200]
                safe_error = error_msg.replace("[", "\\[").replace("]", "\\]")
                result_queue.put({"type": "error", "error": safe_error})
                result_queue.put({
                    "type": "token",
                    "content": f"Error: {safe_error}\n\nCheck your API key and try again.",
                })
                result_queue.put({"type": "done", "finish_reason": "error"})
            finally:
                result_queue.put(None)  # Sentinel value

        # Start thread
        thread = threading.Thread(target=run_agency_in_thread, daemon=True)
        thread.start()

        # Yield events as they arrive
        try:
            while True:
                try:
                    # Use asyncio.sleep to allow other coroutines to run
                    event = result_queue.get(timeout=0.1)
                    if event is None:  # Sentinel value - processing complete
                        break

                    # Handle memory add event
                    if event.get("type") == "memory_add":
                        self.memory.add_message(event["role"], event["content"])
                    else:
                        if not first_stream_event_logged:
                            #region agent log
                            _safe_debug_log({
                                "sessionId": "debug-session",
                                "runId": "post-fix",
                                "hypothesisId": "H3",
                                "location": "agent_bridge._process_with_agency",
                                "message": "queue_event_forwarded",
                                "data": {"event_type": event.get("type")},
                                "timestamp": int(time.time() * 1000)
                            })
                            #endregion agent log
                            first_stream_event_logged = True
                        yield event

                except queue.Empty:
                    # No event yet, yield control back to event loop
                    await asyncio.sleep(0.05)
                    continue
        except Exception as e:
            error_msg = str(e)[:200]
            safe_error = error_msg.replace("[", "\\[").replace("]", "\\]")
            yield {"type": "error", "error": safe_error}
            yield {
                "type": "token",
                "content": f"Error: {safe_error}\n\nCheck your API key and try again.",
            }
            yield {"type": "done", "finish_reason": "error"}

    async def _process_with_agent(self, message: str) -> AsyncIterator[Dict[str, Any]]:
        """Process message with single agent."""
        try:
            # Get tools if enabled
            tools = registry.list_tools() if self.tools_enabled else None

            # Process with tools - run in thread to avoid blocking TUI
            if self.tools_enabled and tools:
                response = await asyncio.to_thread(
                    self.agent.process_with_tools,
                    message,
                    tools=tools,
                    tool_executor=registry.execute,
                )
            else:
                response = await asyncio.to_thread(self.agent.process, message)

            # Add response to memory
            self.memory.add_message("assistant", response)

            # Yield response
            yield {"type": "token", "content": response}
            yield {"type": "done", "finish_reason": "stop"}

        except Exception as e:
            error_msg = str(e)[:200]
            safe_error = error_msg.replace("[", "\\[").replace("]", "\\]")
            yield {"type": "error", "error": safe_error}
            yield {
                "type": "token",
                "content": f"Error: {safe_error}\n\nCheck your API key and try again.",
            }
            yield {"type": "done", "finish_reason": "error"}

    async def process(self, message: str) -> str:
        """Process a message and return the full response."""
        full_response = ""

        async for event in self.stream_response(message):
            if event["type"] == "token":
                full_response += event.get("content", "")
            elif event["type"] == "error":
                raise Exception(event.get("error", "Unknown error"))

        return full_response

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models by provider."""
        return {
            "GLM (Z.AI)": ["glm-4.7", "glm-4-plus", "glm-4", "glm-4-flash"],
            "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            "Anthropic": ["claude-3-5-sonnet-latest", "claude-3-opus-latest"],
            "Groq": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
            "Ollama": ["llama3.2", "mixtral", "codellama"],
        }

    def get_current_agent(self) -> str:
        """Get current agent name."""
        return self.agent.name if self.agent else "None"

    def get_agency_info(self) -> Dict[str, Any]:
        """Get agency information."""
        if self.agency:
            return {
                "name": self.agency.name,
                "entry_agent": self.agency.entry_agent.name,
                "agents": [a.name for a in self.agency.agents],
                "model": self.model,
                "provider": self.provider_name,
            }
        return {
            "name": "Single Agent",
            "entry_agent": self.agent.name if self.agent else "None",
            "agents": [self.agent.name] if self.agent else [],
            "model": self.model,
            "provider": self.provider_name,
        }
