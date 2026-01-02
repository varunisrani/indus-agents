# Phase 3: Agent System - Multi-LLM Support & Inter-Agent Communication

## Overview

This phase transforms indus-agents from an OpenAI-only system to a multi-provider framework with full inter-agent communication capabilities similar to Agency Swarm.

---

## Objectives

1. Create LLM abstraction layer supporting multiple providers
2. Integrate LiteLLM for unified API
3. Implement agent factory pattern
4. Add SendMessageHandoff for agent-to-agent communication
5. Support markdown-based instruction files

---

## Task Breakdown

### 3.1 LLM Abstraction Layer

**File**: `src/my_agent_framework/llm.py`

```python
"""
LLM Provider Abstraction Layer

Supports OpenAI, Anthropic, and other providers via LiteLLM.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
import os

class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Tuple[str, Optional[List[Dict]]]:
        """
        Complete a chat conversation.

        Returns:
            Tuple of (response_content, tool_calls)
            tool_calls is None if no tools were called
        """
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if provider supports tool/function calling"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        **kwargs
    ):
        from openai import AsyncOpenAI

        self.model = model
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.kwargs = kwargs

    async def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Tuple[str, Optional[List[Dict]]]:
        merged_kwargs = {**self.kwargs, **kwargs}

        request_params = {
            "model": self.model,
            "messages": messages,
            **merged_kwargs
        }

        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"

        response = await self.client.chat.completions.create(**request_params)
        message = response.choices[0].message

        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
                for tc in message.tool_calls
            ]

        return message.content or "", tool_calls

    def supports_tools(self) -> bool:
        return True


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        **kwargs
    ):
        from anthropic import AsyncAnthropic

        self.model = model
        self.client = AsyncAnthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.kwargs = kwargs

    async def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Tuple[str, Optional[List[Dict]]]:
        merged_kwargs = {**self.kwargs, **kwargs}

        # Convert OpenAI format to Anthropic format
        anthropic_messages = []
        system_content = ""

        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n"
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        request_params = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": merged_kwargs.get("max_tokens", 4096),
        }

        if system_content:
            request_params["system"] = system_content.strip()

        if tools:
            # Convert OpenAI tool format to Anthropic
            request_params["tools"] = self._convert_tools(tools)

        response = await self.client.messages.create(**request_params)

        content = ""
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input
                })

        return content, tool_calls

    def _convert_tools(self, openai_tools: List[Dict]) -> List[Dict]:
        """Convert OpenAI tool format to Anthropic format"""
        anthropic_tools = []
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool["function"]
                anthropic_tools.append({
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {})
                })
        return anthropic_tools

    def supports_tools(self) -> bool:
        return True


class LiteLLMProvider(LLMProvider):
    """Generic provider using LiteLLM for any supported model"""

    def __init__(self, model: str, **kwargs):
        import litellm
        self.model = model
        self.kwargs = kwargs
        litellm.drop_params = True  # Ignore unsupported params

    async def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Tuple[str, Optional[List[Dict]]]:
        import litellm

        merged_kwargs = {**self.kwargs, **kwargs}

        request_params = {
            "model": self.model,
            "messages": messages,
            **merged_kwargs
        }

        if tools:
            request_params["tools"] = tools

        response = await litellm.acompletion(**request_params)
        message = response.choices[0].message

        tool_calls = None
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
                for tc in message.tool_calls
            ]

        return message.content or "", tool_calls

    def supports_tools(self) -> bool:
        # Most modern models support tools
        return True


def get_provider(model: str, **kwargs) -> LLMProvider:
    """
    Factory function to get appropriate provider for a model.

    Args:
        model: Model identifier (e.g., "gpt-4o", "claude-3-5-sonnet", "anthropic/claude-3")

    Returns:
        LLMProvider instance
    """
    model_lower = model.lower()

    # Direct OpenAI models
    if model_lower.startswith("gpt-") or model_lower.startswith("o1"):
        return OpenAIProvider(model=model, **kwargs)

    # Direct Anthropic models
    if model_lower.startswith("claude"):
        return AnthropicProvider(model=model, **kwargs)

    # LiteLLM format (provider/model)
    if "/" in model:
        provider, _ = model.split("/", 1)
        if provider == "anthropic":
            return LiteLLMProvider(model=model, **kwargs)
        elif provider == "openai":
            return LiteLLMProvider(model=model, **kwargs)
        else:
            return LiteLLMProvider(model=model, **kwargs)

    # Default to LiteLLM for unknown models
    return LiteLLMProvider(model=model, **kwargs)


def detect_model_type(model: str) -> Tuple[bool, bool, bool]:
    """
    Detect the type of model.

    Returns:
        Tuple of (is_openai, is_anthropic, is_other)
    """
    model_lower = model.lower()

    is_openai = model_lower.startswith("gpt-") or model_lower.startswith("o1") or "openai" in model_lower
    is_anthropic = "claude" in model_lower or "anthropic" in model_lower
    is_other = not is_openai and not is_anthropic

    return is_openai, is_anthropic, is_other
```

---

### 3.2 Agent Factory Pattern

**File**: `src/my_agent_framework/agents/__init__.py`

```python
"""
Pre-built Agent Definitions

Factory functions for creating specialized agents.
"""

from .developer_agent import create_developer_agent
from .planner_agent import create_planner_agent

__all__ = [
    "create_developer_agent",
    "create_planner_agent",
]
```

**File**: `src/my_agent_framework/agents/developer_agent.py`

```python
"""
Developer Agent - Code implementation specialist
"""

import os
from typing import Optional
from ..agent import Agent, AgentConfig
from ..llm import get_provider, detect_model_type
from ..tools import (
    Bash, Read, Write, Edit, MultiEdit,
    Glob, Grep, Git, LS, TodoWrite
)


def load_instructions(base_dir: str, model: str) -> str:
    """Load appropriate instruction file based on model"""
    # Check for model-specific instructions
    is_openai, is_anthropic, _ = detect_model_type(model)

    if is_openai and model.startswith("gpt-5"):
        filename = "developer-gpt5.md"
    elif is_anthropic:
        filename = "developer-claude.md"
    else:
        filename = "developer.md"

    filepath = os.path.join(base_dir, "instructions", filename)

    # Fallback to default
    if not os.path.exists(filepath):
        filepath = os.path.join(base_dir, "instructions", "developer.md")

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()

    # Default embedded instructions
    return """You are a skilled software developer agent.

Your role is to help with coding tasks including:
- Writing and editing code
- Running commands and tests
- Searching and navigating codebases
- Version control operations

Use the available tools to complete tasks efficiently.
Always read files before editing them.
Prefer editing existing code over creating new files.
"""


def create_developer_agent(
    model: str = "gpt-4o",
    name: str = "Developer",
    reasoning_effort: str = "medium",
    **kwargs
) -> Agent:
    """
    Create a developer agent specialized for code implementation.

    Args:
        model: LLM model to use
        name: Agent name
        reasoning_effort: Reasoning effort level (low, medium, high)
        **kwargs: Additional agent configuration

    Returns:
        Configured Agent instance
    """
    # Get instructions
    base_dir = os.path.dirname(__file__)
    instructions = load_instructions(base_dir, model)

    # Create config
    config = AgentConfig(
        model=model,
        temperature=0.3,  # More deterministic for code
        max_tokens=4096,
        **kwargs
    )

    # Create agent
    agent = Agent(
        name=name,
        role="Software Developer",
        config=config,
        system_prompt=instructions
    )

    # Attach tools
    agent.tools = [
        Bash, Read, Write, Edit, MultiEdit,
        Glob, Grep, Git, LS, TodoWrite
    ]

    return agent
```

**File**: `src/my_agent_framework/agents/planner_agent.py`

```python
"""
Planner Agent - Strategic planning and task breakdown
"""

import os
from typing import Optional
from ..agent import Agent, AgentConfig
from ..llm import detect_model_type


def load_instructions(base_dir: str, model: str) -> str:
    """Load planner instructions"""
    filepath = os.path.join(base_dir, "instructions", "planner.md")

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()

    return """You are a strategic planning agent.

Your role is to:
- Break down complex tasks into actionable steps
- Identify dependencies between tasks
- Create implementation roadmaps
- Clarify requirements before implementation

You do NOT execute code directly. Instead, you provide detailed plans
for the Developer agent to implement.

When planning:
1. Understand the full scope of the request
2. Identify all components that need to be created or modified
3. Determine the correct order of operations
4. Anticipate potential issues and edge cases
5. Provide clear, actionable steps
"""


def create_planner_agent(
    model: str = "gpt-4o",
    name: str = "Planner",
    reasoning_effort: str = "high",
    **kwargs
) -> Agent:
    """
    Create a planner agent specialized for strategic planning.

    Args:
        model: LLM model to use
        name: Agent name
        reasoning_effort: Reasoning effort level
        **kwargs: Additional configuration

    Returns:
        Configured Agent instance
    """
    base_dir = os.path.dirname(__file__)
    instructions = load_instructions(base_dir, model)

    config = AgentConfig(
        model=model,
        temperature=0.5,  # Balanced for planning
        max_tokens=4096,
        **kwargs
    )

    agent = Agent(
        name=name,
        role="Strategic Planner",
        config=config,
        system_prompt=instructions
    )

    # Planner typically doesn't need execution tools
    agent.tools = []

    return agent
```

---

### 3.3 Inter-Agent Communication (Handoffs)

**File**: `src/my_agent_framework/handoff.py`

```python
"""
Inter-Agent Communication System

Enables agents to hand off tasks to other agents.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from pydantic import Field
from .tools.base import BaseTool

if TYPE_CHECKING:
    from .orchestrator import Agency


class SendMessageHandoff(BaseTool):
    """Hand off a task to another agent.

    Use this when you need another agent's expertise.
    The target agent will receive your message and context,
    and their response will be returned to you.
    """

    target_agent: str = Field(
        ...,
        description="Name of the agent to hand off to"
    )
    message: str = Field(
        ...,
        description="Message/task for the target agent"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context to pass to the agent"
    )

    # Set by agency at runtime
    _agency: Optional["Agency"] = None

    async def run(self) -> str:
        """Execute the handoff"""
        if self._agency is None:
            return "Error: Handoff not configured. Agency not set."

        # Get target agent
        target = self._agency.get_agent(self.target_agent)
        if target is None:
            available = list(self._agency.agents.keys())
            return f"Error: Agent '{self.target_agent}' not found. Available: {available}"

        # Build context message
        context_str = ""
        if self.context:
            context_str = f"\n\nContext: {self.context}"

        full_message = f"[Handoff from {self._agency.current_agent}]{context_str}\n\n{self.message}"

        try:
            # Process with target agent
            response = await target.process(full_message)
            return f"[Response from {self.target_agent}]\n\n{response}"
        except Exception as e:
            return f"Error during handoff: {str(e)}"


class HandoffConfig:
    """Configuration for agent handoffs"""

    def __init__(self):
        self.allowed_handoffs: Dict[str, list] = {}  # agent -> list of targets

    def allow(self, from_agent: str, to_agent: str):
        """Allow handoff from one agent to another"""
        if from_agent not in self.allowed_handoffs:
            self.allowed_handoffs[from_agent] = []
        if to_agent not in self.allowed_handoffs[from_agent]:
            self.allowed_handoffs[from_agent].append(to_agent)

    def is_allowed(self, from_agent: str, to_agent: str) -> bool:
        """Check if handoff is allowed"""
        allowed = self.allowed_handoffs.get(from_agent, [])
        return to_agent in allowed or "*" in allowed

    def allow_all(self, from_agent: str):
        """Allow agent to hand off to any other agent"""
        self.allowed_handoffs[from_agent] = ["*"]
```

---

### 3.4 Enhanced Agency/Orchestrator

**File**: `src/my_agent_framework/agency.py`

```python
"""
Agency - Multi-Agent Orchestration with Handoffs

Replaces/enhances the basic MultiAgentOrchestrator with
full inter-agent communication support.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from .agent import Agent
from .handoff import SendMessageHandoff, HandoffConfig


@dataclass
class AgencyResponse:
    """Response from agency processing"""
    response: str
    agents_used: List[str]
    handoff_chain: List[Tuple[str, str]]  # (from, to) pairs
    processing_time: float
    error: Optional[str] = None


class Agency:
    """
    Multi-agent orchestration system with inter-agent communication.

    Similar to Agency Swarm's Agency class, this manages multiple agents
    and enables them to communicate via handoffs.
    """

    def __init__(
        self,
        *agents: Agent,
        name: str = "IndusAgency",
        communication_flows: Optional[List[Tuple[Agent, Agent]]] = None,
        shared_instructions: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize agency with agents and communication flows.

        Args:
            *agents: Agent instances (first is entry point)
            name: Agency name
            communication_flows: List of (from_agent, to_agent) tuples
            shared_instructions: Instructions shared by all agents
            verbose: Enable verbose logging
        """
        self.name = name
        self.verbose = verbose
        self.shared_instructions = shared_instructions

        # Store agents by name
        self.agents: Dict[str, Agent] = {}
        self.entry_agent: Optional[Agent] = None

        for i, agent in enumerate(agents):
            self.agents[agent.name] = agent
            if i == 0:
                self.entry_agent = agent

            # Add shared instructions if provided
            if shared_instructions:
                agent.system_prompt = f"{shared_instructions}\n\n{agent.system_prompt}"

        # Configure handoffs
        self.handoff_config = HandoffConfig()
        if communication_flows:
            for from_agent, to_agent in communication_flows:
                self.handoff_config.allow(from_agent.name, to_agent.name)

        # Track current processing state
        self.current_agent: Optional[str] = None
        self.handoff_chain: List[Tuple[str, str]] = []

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        return self.agents.get(name)

    def add_agent(self, agent: Agent, can_handoff_to: List[str] = None):
        """Add an agent to the agency"""
        self.agents[agent.name] = agent
        if can_handoff_to:
            for target in can_handoff_to:
                self.handoff_config.allow(agent.name, target)

    def _inject_handoff_tool(self, agent: Agent):
        """Inject handoff tool configured for this agency"""
        # Create handoff tool with agency reference
        handoff = SendMessageHandoff(
            target_agent="",  # Set at call time
            message=""
        )
        handoff._agency = self

        # Add to agent tools if not present
        if not hasattr(agent, 'tools'):
            agent.tools = []
        if SendMessageHandoff not in agent.tools:
            agent.tools.append(SendMessageHandoff)

    async def process(self, message: str, agent_name: Optional[str] = None) -> AgencyResponse:
        """
        Process a message through the agency.

        Args:
            message: User message to process
            agent_name: Specific agent to use (default: entry agent)

        Returns:
            AgencyResponse with result and metadata
        """
        import time
        start_time = time.time()

        agents_used = []
        self.handoff_chain = []

        # Select agent
        if agent_name:
            agent = self.get_agent(agent_name)
            if not agent:
                return AgencyResponse(
                    response=f"Agent '{agent_name}' not found",
                    agents_used=[],
                    handoff_chain=[],
                    processing_time=time.time() - start_time,
                    error=f"Agent not found: {agent_name}"
                )
        else:
            agent = self.entry_agent

        if not agent:
            return AgencyResponse(
                response="No entry agent configured",
                agents_used=[],
                handoff_chain=[],
                processing_time=time.time() - start_time,
                error="No entry agent"
            )

        try:
            self.current_agent = agent.name
            agents_used.append(agent.name)

            if self.verbose:
                print(f"[{self.name}] Processing with agent: {agent.name}")

            # Inject handoff capability
            self._inject_handoff_tool(agent)

            # Process message
            if hasattr(agent, 'tools') and agent.tools:
                response = await agent.process_with_tools(message)
            else:
                response = await agent.process(message)

            return AgencyResponse(
                response=response,
                agents_used=agents_used,
                handoff_chain=self.handoff_chain,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            return AgencyResponse(
                response=f"Error: {str(e)}",
                agents_used=agents_used,
                handoff_chain=self.handoff_chain,
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def process_sync(self, message: str, agent_name: Optional[str] = None) -> AgencyResponse:
        """Synchronous wrapper for process"""
        return asyncio.run(self.process(message, agent_name))

    def demo_terminal(self):
        """Interactive terminal demo mode"""
        from rich.console import Console
        from rich.panel import Panel
        from rich.markdown import Markdown

        console = Console()
        console.print(Panel(f"[bold blue]{self.name}[/bold blue] - Interactive Mode"))
        console.print(f"Available agents: {list(self.agents.keys())}")
        console.print("Type 'exit' to quit, '@agent_name message' to use specific agent\n")

        while True:
            try:
                user_input = console.input("[bold green]You:[/bold green] ")
            except EOFError:
                break

            if user_input.lower() in ['exit', 'quit', '/quit']:
                break

            # Parse agent targeting
            agent_name = None
            message = user_input
            if user_input.startswith("@"):
                parts = user_input[1:].split(" ", 1)
                if len(parts) == 2:
                    agent_name, message = parts

            # Process
            response = self.process_sync(message, agent_name)

            # Display
            console.print(f"\n[bold magenta]Agent:[/bold magenta] {response.agents_used}")
            console.print(Markdown(response.response))
            console.print(f"[dim]Time: {response.processing_time:.2f}s[/dim]\n")


# Convenience function
def create_agency(
    *agents: Agent,
    name: str = "IndusAgency",
    bidirectional: bool = True,
    **kwargs
) -> Agency:
    """
    Create an agency with common defaults.

    Args:
        *agents: Agents (first is entry point)
        name: Agency name
        bidirectional: Enable bidirectional handoffs between all agents
        **kwargs: Additional Agency arguments

    Returns:
        Configured Agency instance
    """
    communication_flows = []

    if bidirectional:
        # Allow all agents to communicate with each other
        agent_list = list(agents)
        for i, from_agent in enumerate(agent_list):
            for j, to_agent in enumerate(agent_list):
                if i != j:
                    communication_flows.append((from_agent, to_agent))

    return Agency(
        *agents,
        name=name,
        communication_flows=communication_flows,
        **kwargs
    )
```

---

### 3.5 Instruction File Templates

**File**: `src/my_agent_framework/agents/instructions/developer.md`

```markdown
# Developer Agent Instructions

You are a skilled software developer agent specializing in code implementation.

## Core Responsibilities
- Write clean, efficient, maintainable code
- Edit existing code to add features or fix bugs
- Run tests and commands to verify changes
- Navigate and search codebases effectively
- Use version control appropriately

## Working Principles

### Before Coding
1. ALWAYS read files before editing them
2. Understand existing patterns and conventions
3. Check for similar code that can be reused or extended

### While Coding
- Prefer editing existing files over creating new ones
- Follow the existing code style and conventions
- Write minimal, focused changes
- Avoid over-engineering or premature optimization

### Code Quality
- NO comments unless specifically requested
- Keep functions small and focused
- Use meaningful variable and function names
- Handle errors appropriately

## Tool Usage

### File Operations
- Use `Read` before any `Edit` or `Write`
- Use `Edit` for targeted changes with exact string matching
- Use `MultiEdit` for related changes across the same file
- Use `Glob` to find files by pattern
- Use `Grep` to search file contents

### Commands
- Use `Bash` for running tests, builds, and installations
- Always check command output for errors
- Use `Git` for version control operations

### Task Management
- Use `TodoWrite` to track multi-step tasks
- Mark tasks in_progress when starting
- Mark tasks completed immediately when done

## Handoff Guidelines

Hand off to the Planner agent when:
- Task requires architectural decisions
- Multiple possible approaches exist
- Scope is unclear or needs refinement
- Task has many interconnected components

Do NOT hand off for:
- Simple, well-defined coding tasks
- Bug fixes with clear causes
- Small feature additions
```

**File**: `src/my_agent_framework/agents/instructions/planner.md`

```markdown
# Planner Agent Instructions

You are a strategic planning agent specializing in software architecture and task breakdown.

## Core Responsibilities
- Analyze complex requirements
- Break tasks into actionable steps
- Identify dependencies and risks
- Create clear implementation roadmaps
- Provide guidance without executing code

## Planning Process

### 1. Understanding
- Clarify ambiguous requirements
- Identify the scope and constraints
- Note any technical considerations

### 2. Analysis
- Break down into components
- Identify dependencies between components
- Consider edge cases and potential issues

### 3. Planning
- Create ordered list of implementation steps
- Note which steps can be parallelized
- Identify critical path items
- Specify expected outcomes for each step

### 4. Communication
- Provide clear, actionable plans
- Include rationale for key decisions
- Highlight potential risks or concerns

## Output Format

When providing a plan:

```
## Task: [Brief description]

### Analysis
[Key observations and considerations]

### Implementation Steps
1. [Step 1] - [Expected outcome]
2. [Step 2] - [Expected outcome]
...

### Dependencies
- Step X requires Step Y to complete first
- [Other dependencies]

### Risks
- [Potential issue 1] - [Mitigation]
- [Potential issue 2] - [Mitigation]
```

## When NOT to Plan

Skip extensive planning for:
- Single-step tasks
- Well-defined, simple changes
- Bug fixes with obvious solutions

For these, provide brief guidance and hand off to Developer.

## Handoff Guidelines

Always hand off to Developer after planning, with:
- Clear step-by-step instructions
- Expected outcomes for each step
- Any specific constraints or requirements
```

---

## Testing Requirements

- Test each LLM provider
- Test handoff between agents
- Test agency configuration
- Test instruction loading
- Integration tests for full workflows

---

## Acceptance Criteria

- [ ] OpenAI provider works with tools
- [ ] Anthropic provider works with tools
- [ ] LiteLLM provider works as fallback
- [ ] Agent factory creates configured agents
- [ ] Handoff transfers context correctly
- [ ] Bidirectional communication works
- [ ] Instruction files load correctly
- [ ] Agency demo mode works

---

## Next Phase

After completing Phase 3, proceed to [Phase 4: Advanced Features](PHASE4_FEATURES.md) for hooks, streaming, and code generation capabilities.
