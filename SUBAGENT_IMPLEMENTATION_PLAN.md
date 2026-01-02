# Subagent Implementation Plan for indus-agents

## Executive Summary

This document outlines the comprehensive plan for adding native subagent creation and handling to the indus-agents framework, following patterns from Agency-Swarm and Agency-Code.

**Goal**: Enable indus-agents to create, manage, and orchestrate subagents natively with full support for:
- Factory-based subagent creation
- SendMessageHandoff-style communication
- Lifecycle hooks
- Model-specific configurations
- Hierarchical agent relationships

**Estimated Effort**: ~59 hours over 10 working days
**Complexity**: MEDIUM

---

## 1. Current State Analysis

### indus-agents Strengths
| Feature | Status | Location |
|---------|--------|----------|
| Agent Class | ✅ Complete | `src/my_agent_framework/agent.py` |
| AgentConfig | ✅ Complete | `src/my_agent_framework/agent.py` |
| Agency Class | ✅ Basic | `src/my_agent_framework/agency.py` |
| Tool Registry | ✅ Complete | `src/my_agent_framework/tools/__init__.py` |
| Development Tools | ✅ Partial | `src/my_agent_framework/tools/dev/` |
| Template Renderer | ✅ Basic | `src/my_agent_framework/templates/renderer.py` |
| Handoff Tool | ⚠️ Basic | `src/my_agent_framework/tools/handoff.py` |

### Missing Components for Subagent Support
| Component | Priority | Gap |
|-----------|----------|-----|
| SendMessageHandoff Tool | CRITICAL | No tool-based handoff |
| Agent Hooks System | CRITICAL | No lifecycle hooks |
| Shared Utilities (agent_utils) | CRITICAL | No model detection/settings |
| Git Tool | HIGH | Missing version control |
| LS Tool | HIGH | Missing directory listing |
| Enhanced Agency | HIGH | Limited orchestration |

---

## 2. Required New Files

### Phase 1: Shared Utilities (Critical Foundation)

#### 2.1 `src/my_agent_framework/shared/__init__.py`
```python
"""Shared utilities for indus-agents framework."""
from .agent_utils import (
    detect_model_type,
    select_instructions_file,
    render_instructions,
    create_model_settings,
    get_model_instance,
)
from .system_hooks import AgentHooks, SystemReminderHook, create_system_reminder_hook
from .utils import silence_warnings_and_logs

__all__ = [
    "detect_model_type",
    "select_instructions_file",
    "render_instructions",
    "create_model_settings",
    "get_model_instance",
    "AgentHooks",
    "SystemReminderHook",
    "create_system_reminder_hook",
    "silence_warnings_and_logs",
]
```

#### 2.2 `src/my_agent_framework/shared/agent_utils.py`
```python
"""Agent creation utilities - model detection, instruction rendering, settings."""

import os
import platform
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class ModelSettings:
    """Extended model configuration for different providers."""
    reasoning_effort: Optional[str] = None
    reasoning_summary: Optional[str] = "auto"
    max_tokens: int = 32000
    truncation: str = "auto"
    extra_body: Optional[Dict[str, Any]] = None

def detect_model_type(model: str) -> Tuple[bool, bool, bool]:
    """Detect model provider type."""
    is_openai = "gpt" in model.lower()
    is_claude = "claude" in model.lower()
    is_grok = "grok" in model.lower()
    return is_openai, is_claude, is_grok

def select_instructions_file(base_dir: str, model: str) -> str:
    """Select model-specific instructions file."""
    if model.lower().startswith("gpt-5"):
        filename = "instructions-gpt-5.md"
    elif "claude" in model.lower():
        filename = "instructions-claude.md"
    else:
        filename = "instructions.md"

    path = os.path.join(base_dir, filename)
    if os.path.exists(path):
        return path
    return os.path.join(base_dir, "instructions.md")

def render_instructions(
    template_path: str,
    model: str = "gpt-4o",
    extra_context: Optional[Dict[str, Any]] = None
) -> str:
    """Render instructions with placeholders replaced."""
    with open(template_path, "r") as f:
        content = f.read()

    placeholders = {
        "{cwd}": os.getcwd(),
        "{is_git_repo}": str(os.path.isdir(".git")),
        "{platform}": platform.system(),
        "{os_version}": platform.release(),
        "{today}": datetime.now().strftime("%Y-%m-%d"),
        "{model}": model,
    }

    if extra_context:
        for key, value in extra_context.items():
            placeholders[f"{{{key}}}"] = str(value)

    for key, value in placeholders.items():
        content = content.replace(key, value)

    return content

def create_model_settings(
    model: str,
    reasoning_effort: str = "medium",
    reasoning_summary: str = "auto",
    max_tokens: int = 32000
) -> ModelSettings:
    """Create model-specific settings."""
    is_openai, is_claude, is_grok = detect_model_type(model)

    return ModelSettings(
        reasoning_effort=reasoning_effort if (is_openai or is_claude) else None,
        reasoning_summary=reasoning_summary,
        max_tokens=max_tokens,
        truncation="auto",
        extra_body=(
            {"search_parameters": {"mode": "on", "returnCitations": True}}
            if is_grok else None
        ),
    )

def get_model_instance(model: str):
    """Get appropriate model instance based on provider."""
    is_openai, _, _ = detect_model_type(model)
    if is_openai:
        return model
    # For non-OpenAI models, would use LiteLLM wrapper
    return model
```

#### 2.3 `src/my_agent_framework/shared/system_hooks.py`
```python
"""Lifecycle hooks for agent execution."""

from abc import ABC
from typing import Any, Optional, List, Dict

class AgentHooks(ABC):
    """Base class for agent lifecycle hooks."""

    async def on_start(self, context: Any, agent: Any) -> None:
        """Called when agent starts processing."""
        pass

    async def on_end(self, context: Any, agent: Any, output: str) -> None:
        """Called when agent finishes processing."""
        pass

    async def on_tool_start(self, context: Any, agent: Any, tool: Any) -> None:
        """Called before tool execution."""
        pass

    async def on_tool_end(self, context: Any, agent: Any, tool: Any, result: str) -> None:
        """Called after tool execution."""
        pass

    async def on_llm_start(self, context: Any, agent: Any, messages: List[Dict]) -> None:
        """Called before LLM inference."""
        pass

    async def on_llm_end(self, context: Any, agent: Any, response: Any) -> None:
        """Called after LLM response."""
        pass

    async def on_handoff(self, context: Any, agent: Any, source_agent: str) -> None:
        """Called when agent receives a handoff."""
        pass

class SystemReminderHook(AgentHooks):
    """Injects periodic reminders about critical instructions."""

    def __init__(self, tool_call_interval: int = 15):
        self.tool_call_count = 0
        self.tool_call_interval = tool_call_interval
        self.pending_reminder = None

    async def on_tool_end(self, context, agent, tool, result):
        self.tool_call_count += 1
        if self.tool_call_count >= self.tool_call_interval:
            self._inject_reminder()
            self.tool_call_count = 0

    def _inject_reminder(self):
        self.pending_reminder = """<system-reminder>
- Read file before Edit (safety requirement)
- Use TodoWrite for task tracking
- Mark todos as in_progress before execution
</system-reminder>"""

def create_system_reminder_hook(interval: int = 15) -> SystemReminderHook:
    """Factory for creating system reminder hooks."""
    return SystemReminderHook(tool_call_interval=interval)
```

### Phase 2: Enhanced Tools

#### 2.4 `src/my_agent_framework/tools/dev/git.py`
```python
"""Git operations tool for version control."""

from typing import Optional, ClassVar
from pydantic import Field
from ..base import BaseTool
import subprocess

class Git(BaseTool):
    name: ClassVar[str] = "git"
    description: ClassVar[str] = """Execute git commands for version control.
    Supports: status, add, commit, push, pull, branch, checkout, diff, log, clone."""

    command: str = Field(..., description="Git subcommand (status, add, commit, etc.)")
    args: Optional[str] = Field(None, description="Additional arguments")
    message: Optional[str] = Field(None, description="Commit message (for commit)")

    def execute(self) -> str:
        cmd = ["git", self.command]
        if self.args:
            cmd.extend(self.args.split())
        if self.command == "commit" and self.message:
            cmd.extend(["-m", self.message])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout or result.stderr
            return f"Exit code: {result.returncode}\n{output}"
        except Exception as e:
            return f"Error: {str(e)}"
```

#### 2.5 `src/my_agent_framework/tools/dev/ls.py`
```python
"""Directory listing tool."""

from typing import Optional, ClassVar
from pydantic import Field
from ..base import BaseTool
import os

class LS(BaseTool):
    name: ClassVar[str] = "ls"
    description: ClassVar[str] = """List directory contents with details."""

    path: str = Field(".", description="Directory path to list")
    all_files: bool = Field(False, description="Include hidden files")
    long_format: bool = Field(True, description="Use long listing format")

    def execute(self) -> str:
        try:
            entries = os.listdir(self.path)
            if not self.all_files:
                entries = [e for e in entries if not e.startswith('.')]
            entries.sort()

            if self.long_format:
                lines = []
                for entry in entries:
                    full_path = os.path.join(self.path, entry)
                    stat = os.stat(full_path)
                    is_dir = "d" if os.path.isdir(full_path) else "-"
                    size = stat.st_size
                    lines.append(f"{is_dir} {size:>10} {entry}")
                return "\n".join(lines)
            else:
                return "\n".join(entries)
        except Exception as e:
            return f"Error: {str(e)}"
```

### Phase 3: SendMessageHandoff Tool

#### 2.6 `src/my_agent_framework/tools/send_message_handoff.py`
```python
"""SendMessageHandoff tool for inter-agent communication."""

from typing import Optional, ClassVar, Dict, Any, TYPE_CHECKING
from pydantic import Field
from .base import BaseTool

if TYPE_CHECKING:
    from ..agency import Agency

_current_agency: Optional["Agency"] = None
_agent_call_stack: list = []

def set_current_agency(agency: "Agency") -> None:
    global _current_agency
    _current_agency = agency

def push_agent(agent_name: str) -> None:
    _agent_call_stack.append(agent_name)

def pop_agent() -> Optional[str]:
    return _agent_call_stack.pop() if _agent_call_stack else None

def get_current_agent() -> Optional[str]:
    return _agent_call_stack[-1] if _agent_call_stack else None

class SendMessageHandoff(BaseTool):
    name: ClassVar[str] = "send_message_handoff"
    description: ClassVar[str] = """Hand off a task to another agent in the agency.
    Use when you need specialized expertise or want to delegate a subtask."""

    to_agent: str = Field(..., description="Name of agent to hand off to")
    message: str = Field(..., description="Task or message for the target agent")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context")

    def execute(self) -> str:
        global _current_agency

        if _current_agency is None:
            return "Error: No agency context available"

        current_agent_name = get_current_agent()
        if not current_agent_name:
            current_agent_name = _current_agency.entry_agent.name

        current_agent = _current_agency.get_agent(current_agent_name)
        if not current_agent:
            return f"Error: Current agent '{current_agent_name}' not found"

        if not _current_agency.can_handoff(current_agent_name, self.to_agent):
            allowed = _current_agency.get_allowed_handoffs(current_agent_name)
            return f"Error: Cannot hand off to {self.to_agent}. Allowed: {allowed}"

        result = _current_agency.handoff(
            from_agent=current_agent,
            to_agent_name=self.to_agent,
            message=self.message,
            context=self.context_data
        )

        if result.success:
            return result.response
        else:
            return f"Handoff failed: {result.error}"
```

### Phase 4: Subagent Factory Template

#### 2.7 `src/my_agent_framework/templates/subagent_template/subagent_factory.py.template`
```python
"""
{agent_name} Agent Factory

Auto-generated subagent template for indus-agents framework.
"""

import os
from typing import Optional, List
from my_agent_framework.agent import Agent, AgentConfig
from my_agent_framework.shared.agent_utils import (
    render_instructions,
    select_instructions_file,
    create_model_settings,
    get_model_instance,
)
from my_agent_framework.shared.system_hooks import create_system_reminder_hook
from my_agent_framework.tools.dev import Read, Write, Bash, Grep, Glob, Edit, TodoWrite

current_dir = os.path.dirname(os.path.abspath(__file__))

def create_{snake_name}_agent(
    model: str = "gpt-4o",
    reasoning_effort: str = "medium",
    config: Optional[AgentConfig] = None,
) -> Agent:
    """Factory that returns a fresh {class_name} instance."""

    instructions_file = select_instructions_file(current_dir, model)
    instructions = render_instructions(instructions_file, model)

    agent_config = config or AgentConfig.from_env()
    agent_config.model = model

    model_settings = create_model_settings(model, reasoning_effort)
    hooks = create_system_reminder_hook()

    return Agent(
        name="{class_name}",
        role="{description}",
        config=agent_config,
        system_prompt=instructions,
        context={
            "model_settings": model_settings,
            "hooks": hooks,
        }
    )
```

---

## 3. Modifications to Existing Files

### 3.1 `src/my_agent_framework/agent.py`
**Add hook integration:**
```python
class Agent:
    def __init__(
        self,
        name: str,
        role: str,
        config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None,
        context: Optional[Any] = None,
        hooks: Optional[AgentHooks] = None,  # NEW
        parent_agent: Optional["Agent"] = None,  # NEW
    ) -> None:
        self.hooks = hooks
        self.parent_agent = parent_agent
        # ... existing code

    def process_with_tools(self, user_input: str, ...) -> str:
        # NEW: Call hooks
        if self.hooks:
            asyncio.run(self.hooks.on_start(self.context, self))

        # ... existing processing

        for tool_call in response_message.tool_calls:
            if self.hooks:
                asyncio.run(self.hooks.on_tool_start(self.context, self, tool_call))

            result = tool_executor.execute(tool_name, **tool_args)

            if self.hooks:
                asyncio.run(self.hooks.on_tool_end(self.context, self, tool_call, result))

        # ... rest of processing

        if self.hooks:
            asyncio.run(self.hooks.on_end(self.context, self, response))

        return response
```

### 3.2 `src/my_agent_framework/agency.py`
**Add SendMessageHandoff support:**
```python
from my_agent_framework.tools.send_message_handoff import (
    SendMessageHandoff,
    set_current_agency,
    push_agent,
    pop_agent,
)

class Agency:
    def __init__(
        self,
        entry_agent: Agent,
        agents: Optional[List[Agent]] = None,
        communication_flows: Optional[List[Tuple[Agent, Agent, type]]] = None,  # ENHANCED
        # ... existing params
    ):
        # ... existing code

        # Set agency context for handoff tool
        set_current_agency(self)

        # Register SendMessageHandoff for each agent in flows
        self._register_handoff_tools()

    def _register_handoff_tools(self):
        """Register handoff tools based on communication flows."""
        for flow in self.communication_flows or []:
            if len(flow) >= 3:
                source, target, tool_class = flow
                # Tool class is registered for source agent
```

### 3.3 `src/my_agent_framework/tools/__init__.py`
**Add new tool exports:**
```python
from .dev.git import Git
from .dev.ls import LS
from .send_message_handoff import SendMessageHandoff

__all__ = [
    # Existing
    "Bash", "Read", "Write", "Edit", "Glob", "Grep", "TodoWrite",
    # New
    "Git", "LS", "SendMessageHandoff",
]
```

---

## 4. Implementation Timeline

### Week 1: Foundation (Days 1-3)

| Day | Task | Hours | Deliverable |
|-----|------|-------|-------------|
| 1 | Create shared/agent_utils.py | 3 | Model detection, instruction rendering |
| 1 | Create shared/system_hooks.py | 4 | AgentHooks, SystemReminderHook |
| 2 | Create shared/utils.py | 2 | Helper utilities |
| 2 | Create SendMessageHandoff tool | 4 | Tool-based handoff |
| 3 | Update agent.py with hooks | 5 | Lifecycle integration |
| 3 | Create Git, LS tools | 4 | Development tools |

### Week 2: Integration (Days 4-7)

| Day | Task | Hours | Deliverable |
|-----|------|-------|-------------|
| 4 | Enhance agency.py | 6 | Full orchestration |
| 4 | Update tools/__init__.py | 2 | Export new tools |
| 5 | Create subagent template | 4 | Factory pattern |
| 5 | Enhance scaffolder.py | 3 | Template generation |
| 6 | Create CLI commands | 5 | Agency management |
| 7 | Integration testing | 6 | End-to-end tests |

### Week 3: Polish (Days 8-10)

| Day | Task | Hours | Deliverable |
|-----|------|-------|-------------|
| 8 | Unit tests | 6 | Test coverage |
| 9 | Documentation | 4 | Usage guides |
| 9 | Example agents | 4 | Sample subagents |
| 10 | Performance testing | 4 | Optimization |
| 10 | Final review | 3 | Quality check |

---

## 5. Success Criteria

### Functional Requirements
- [ ] Subagents can be created using factory functions
- [ ] SendMessageHandoff enables tool-based handoffs
- [ ] Lifecycle hooks fire at correct times
- [ ] Model-specific instructions work correctly
- [ ] Communication flows enforce handoff permissions
- [ ] Subagent context preserved across handoffs

### Technical Requirements
- [ ] No breaking changes to existing API
- [ ] All new parameters have sensible defaults
- [ ] Unit test coverage > 85%
- [ ] Handoff overhead < 100ms
- [ ] Documentation complete

### Integration Requirements
- [ ] Works with existing AgentConfig
- [ ] Works with existing tool registry
- [ ] Works with existing Agency class
- [ ] CLI commands functional

---

## 6. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing API | HIGH | All new params optional |
| Complex async hooks | MEDIUM | Start sync, add async later |
| Performance degradation | MEDIUM | Profile and optimize |
| Model compatibility | LOW | Extensive testing |

---

## 7. Example Usage After Implementation

### Creating a Subagent
```python
from my_agent_framework.shared.agent_utils import (
    render_instructions,
    create_model_settings,
)
from my_agent_framework.shared.system_hooks import create_system_reminder_hook
from my_agent_framework.agent import Agent, AgentConfig

def create_research_agent(model: str = "gpt-4o") -> Agent:
    instructions = render_instructions("./instructions.md", model)
    return Agent(
        name="ResearchAgent",
        role="Research and information gathering specialist",
        config=AgentConfig(model=model),
        system_prompt=instructions,
        hooks=create_system_reminder_hook(),
    )
```

### Creating an Agency with Subagents
```python
from my_agent_framework.agency import Agency
from my_agent_framework.tools import SendMessageHandoff

planner = create_planner_agent()
coder = create_coder_agent()
researcher = create_research_agent()

agency = Agency(
    entry_agent=coder,
    agents=[coder, planner, researcher],
    communication_flows=[
        (coder, planner, SendMessageHandoff),
        (planner, coder, SendMessageHandoff),
        (coder, researcher, SendMessageHandoff),
        (researcher, coder, SendMessageHandoff),
    ],
    shared_instructions="./project-overview.md",
)

# Run
response = agency.process("Build a REST API with documentation")
```

---

## 8. Next Steps

1. **Immediate**: Create `shared/` directory and implement agent_utils.py
2. **Short-term**: Implement SendMessageHandoff tool
3. **Medium-term**: Enhance Agency class with full orchestration
4. **Long-term**: Add CLI commands and comprehensive testing

---

*Document Version: 1.0*
*Created: 2026-01-02*
*Author: Claude Analysis*
