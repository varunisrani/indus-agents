# Subagent Integration Roadmap for indus-agents

## Overview

This roadmap outlines the step-by-step implementation plan for adding native subagent handling to indus-agents, following patterns from Agency-Swarm and Agency-Code.

---

## Phase 1: Foundation (Days 1-2)

### Step 1.1: Create Shared Utilities Module

**Priority**: CRITICAL
**Effort**: 3 hours
**Dependencies**: None

**Files to Create**:
```
src/my_agent_framework/shared/
├── __init__.py
├── agent_utils.py
├── system_hooks.py
└── utils.py
```

**Tasks**:
- [ ] Create `shared/` directory
- [ ] Implement `detect_model_type(model)` function
- [ ] Implement `select_instructions_file(base_dir, model)` function
- [ ] Implement `render_instructions(template_path, model)` function
- [ ] Implement `create_model_settings(model, reasoning_effort)` function
- [ ] Implement `get_model_instance(model)` function
- [ ] Create `ModelSettings` dataclass
- [ ] Add exports to `__init__.py`

**Validation**:
```python
from my_agent_framework.shared import detect_model_type, render_instructions
assert detect_model_type("gpt-4o") == (True, False, False)
assert detect_model_type("claude-opus") == (False, True, False)
```

---

### Step 1.2: Create Hooks System

**Priority**: CRITICAL
**Effort**: 5 hours
**Dependencies**: Step 1.1

**Tasks**:
- [ ] Create `AgentHooks` abstract base class
- [ ] Implement lifecycle methods (on_start, on_end, on_tool_start, etc.)
- [ ] Create `SystemReminderHook` implementation
- [ ] Add `create_system_reminder_hook()` factory
- [ ] Add to `shared/__init__.py` exports

**Validation**:
```python
from my_agent_framework.shared import AgentHooks, SystemReminderHook
hook = SystemReminderHook(tool_call_interval=10)
assert hook.tool_call_count == 0
```

---

### Step 1.3: Create SendMessageHandoff Tool

**Priority**: CRITICAL
**Effort**: 4 hours
**Dependencies**: Step 1.1

**File**: `src/my_agent_framework/tools/send_message_handoff.py`

**Tasks**:
- [ ] Create `SendMessageHandoff` tool class
- [ ] Implement call stack tracking (`push_agent`, `pop_agent`, `get_current_agent`)
- [ ] Implement agency context management
- [ ] Add flow validation
- [ ] Update `tools/__init__.py` exports

**Validation**:
```python
from my_agent_framework.tools import SendMessageHandoff
tool = SendMessageHandoff(to_agent="PlannerAgent", message="Create plan")
schema = tool.get_schema()
assert schema["function"]["name"] == "send_message_handoff"
```

---

## Phase 2: Agent Enhancement (Day 3)

### Step 2.1: Add Hooks to Agent Class

**Priority**: HIGH
**Effort**: 5 hours
**Dependencies**: Steps 1.1, 1.2

**File**: `src/my_agent_framework/agent.py`

**Tasks**:
- [ ] Add `hooks` parameter to `Agent.__init__`
- [ ] Add `parent_agent` parameter
- [ ] Add `model_settings` parameter
- [ ] Call `hooks.on_start()` at processing start
- [ ] Call `hooks.on_tool_start()` before each tool
- [ ] Call `hooks.on_tool_end()` after each tool
- [ ] Call `hooks.on_end()` at processing end
- [ ] Handle async hooks properly

**Code Changes**:
```python
def __init__(
    self,
    name: str,
    role: str,
    config: Optional[AgentConfig] = None,
    system_prompt: Optional[str] = None,
    context: Optional[Any] = None,
    hooks: Optional[AgentHooks] = None,       # NEW
    parent_agent: Optional["Agent"] = None,   # NEW
    model_settings: Optional[ModelSettings] = None,  # NEW
):
    self.hooks = hooks
    self.parent_agent = parent_agent
    self.model_settings = model_settings
```

---

### Step 2.2: Create Development Tools

**Priority**: HIGH
**Effort**: 8 hours
**Dependencies**: None (can parallel with Step 2.1)

**Files**:
- `src/my_agent_framework/tools/dev/git.py`
- `src/my_agent_framework/tools/dev/ls.py`

**Tasks**:
- [ ] Implement `Git` tool (status, add, commit, push, pull, diff, log, branch)
- [ ] Implement `LS` tool (directory listing with options)
- [ ] Add validation and error handling
- [ ] Update `tools/dev/__init__.py`
- [ ] Update `tools/__init__.py`

---

## Phase 3: Agency Enhancement (Days 4-5)

### Step 3.1: Enhance Agency Class

**Priority**: HIGH
**Effort**: 8 hours
**Dependencies**: Steps 1.1, 1.3

**File**: `src/my_agent_framework/agency.py`

**Tasks**:
- [ ] Update communication_flows to include tool class: `(source, target, ToolClass)`
- [ ] Implement `_register_handoff_tools()` method
- [ ] Add call stack management for handoffs
- [ ] Set agency context for SendMessageHandoff
- [ ] Track handoff history with more detail
- [ ] Add subagent management methods

**Code Changes**:
```python
class Agency:
    def __init__(
        self,
        entry_agent: Agent,
        agents: Optional[List[Agent]] = None,
        communication_flows: Optional[List[Tuple[Agent, Agent, type]]] = None,  # Enhanced
        ...
    ):
        set_current_agency(self)
        self._register_handoff_tools()

    def _register_handoff_tools(self):
        """Register handoff tools for each communication flow."""
        for flow in self.communication_flows or []:
            if len(flow) >= 3:
                source, target, tool_class = flow
                # Register tool_class for source agent
```

---

### Step 3.2: Enhance Handoff Processing

**Priority**: HIGH
**Effort**: 4 hours
**Dependencies**: Step 3.1

**Tasks**:
- [ ] Integrate call stack with handoff execution
- [ ] Update `handoff()` to use call stack
- [ ] Add context preservation across handoffs
- [ ] Implement subagent result aggregation
- [ ] Add handoff timeout handling

---

## Phase 4: Templates & Scaffolding (Day 6)

### Step 4.1: Enhance Template Renderer

**Priority**: MEDIUM
**Effort**: 3 hours
**Dependencies**: Step 1.1

**File**: `src/my_agent_framework/templates/renderer.py`

**Tasks**:
- [ ] Add model-specific file selection
- [ ] Add more placeholders (`{platform}`, `{os_version}`, `{is_git_repo}`)
- [ ] Support extra_context parameter
- [ ] Keep backward compatibility with existing format

---

### Step 4.2: Create Subagent Template

**Priority**: MEDIUM
**Effort**: 4 hours
**Dependencies**: Steps 1.1, 1.2

**Files**:
```
src/my_agent_framework/templates/subagent_template/
├── __init__.py.template
├── agent.py.template
├── instructions.md.template
└── instructions-gpt-5.md.template
```

**Tasks**:
- [ ] Create factory function template
- [ ] Create default instructions template
- [ ] Create GPT-5 specific instructions template
- [ ] Add model-aware placeholders

---

### Step 4.3: Enhance Scaffolder

**Priority**: MEDIUM
**Effort**: 3 hours
**Dependencies**: Step 4.2

**File**: `src/my_agent_framework/templates/scaffolder.py`

**Tasks**:
- [ ] Add subagent generation mode
- [ ] Support model-specific instructions generation
- [ ] Add hooks integration in generated agents
- [ ] Generate proper factory functions

---

## Phase 5: CLI & Integration (Day 7)

### Step 5.1: Add Agency CLI Commands

**Priority**: MEDIUM
**Effort**: 5 hours
**Dependencies**: Step 3.1

**File**: `src/my_agent_framework/cli.py` (or new `cli_agency.py`)

**Tasks**:
- [ ] Add `--agency` flag for agency operations
- [ ] Add `create-subagent` command
- [ ] Add `list-agents` command
- [ ] Add `show-flows` command
- [ ] Add `agency demo` mode

---

### Step 5.2: Update Package Exports

**Priority**: LOW
**Effort**: 2 hours
**Dependencies**: All previous steps

**File**: `src/my_agent_framework/__init__.py`

**Tasks**:
- [ ] Export shared utilities
- [ ] Export new tools
- [ ] Export SendMessageHandoff
- [ ] Update `__all__` list

---

## Phase 6: Testing (Days 8-9)

### Step 6.1: Unit Tests

**Priority**: HIGH
**Effort**: 8 hours
**Dependencies**: All implementation steps

**Tasks**:
- [ ] Test `agent_utils.py` functions
- [ ] Test `system_hooks.py` classes
- [ ] Test `SendMessageHandoff` tool
- [ ] Test `Git` and `LS` tools
- [ ] Test enhanced `Agent` class
- [ ] Test enhanced `Agency` class
- [ ] Test template rendering

---

### Step 6.2: Integration Tests

**Priority**: HIGH
**Effort**: 6 hours
**Dependencies**: Step 6.1

**Tasks**:
- [ ] Test multi-agent handoff flows
- [ ] Test subagent creation and usage
- [ ] Test hooks lifecycle
- [ ] Test communication flow validation
- [ ] Test context preservation across handoffs

---

## Phase 7: Documentation (Day 10)

### Step 7.1: Update Documentation

**Priority**: MEDIUM
**Effort**: 4 hours
**Dependencies**: All implementation

**Tasks**:
- [ ] Document new shared utilities
- [ ] Document SendMessageHandoff usage
- [ ] Document hooks system
- [ ] Create subagent creation guide
- [ ] Update README with new features

---

### Step 7.2: Create Examples

**Priority**: MEDIUM
**Effort**: 4 hours
**Dependencies**: Step 7.1

**Tasks**:
- [ ] Create example subagent (ResearchAgent)
- [ ] Create example agency with multiple agents
- [ ] Create example with hooks
- [ ] Document example usage

---

## Implementation Checklist

### Shared Utilities
- [ ] `shared/__init__.py`
- [ ] `shared/agent_utils.py`
  - [ ] `detect_model_type()`
  - [ ] `select_instructions_file()`
  - [ ] `render_instructions()`
  - [ ] `create_model_settings()`
  - [ ] `get_model_instance()`
  - [ ] `ModelSettings` dataclass
- [ ] `shared/system_hooks.py`
  - [ ] `AgentHooks` base class
  - [ ] `SystemReminderHook`
  - [ ] `create_system_reminder_hook()`
- [ ] `shared/utils.py`

### Tools
- [ ] `tools/send_message_handoff.py`
  - [ ] `SendMessageHandoff` class
  - [ ] Call stack management
  - [ ] Agency context management
- [ ] `tools/dev/git.py`
- [ ] `tools/dev/ls.py`
- [ ] Update `tools/__init__.py`

### Agent Enhancement
- [ ] Add `hooks` parameter
- [ ] Add `parent_agent` parameter
- [ ] Add `model_settings` parameter
- [ ] Hook integration in `process_with_tools()`

### Agency Enhancement
- [ ] Update `communication_flows` type
- [ ] Implement `_register_handoff_tools()`
- [ ] Call stack integration
- [ ] Subagent management

### Templates
- [ ] Enhanced `renderer.py`
- [ ] Subagent templates
- [ ] Enhanced `scaffolder.py`

### Testing
- [ ] Unit tests for all components
- [ ] Integration tests for flows
- [ ] CLI command tests

### Documentation
- [ ] API documentation
- [ ] Usage examples
- [ ] Migration guide

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Unit test coverage | > 85% |
| Integration tests passing | 100% |
| Handoff latency | < 100ms |
| Backward compatibility | 100% |
| Documentation complete | Yes |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing API | All new params optional with defaults |
| Async hook complexity | Start sync, add async later |
| Performance issues | Profile critical paths |
| Model compatibility | Test with multiple providers |

---

## Quick Start After Implementation

### Creating a Subagent

```python
from my_agent_framework.agent import Agent, AgentConfig
from my_agent_framework.shared import (
    render_instructions,
    create_model_settings,
    create_system_reminder_hook,
)

def create_research_agent(model: str = "gpt-4o") -> Agent:
    instructions = render_instructions("./instructions.md", model)
    settings = create_model_settings(model, reasoning_effort="medium")
    hooks = create_system_reminder_hook()

    return Agent(
        name="ResearchAgent",
        role="Research and information gathering",
        config=AgentConfig(model=model),
        system_prompt=instructions,
        model_settings=settings,
        hooks=hooks,
    )
```

### Creating Agency with Subagents

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
    ],
    shared_instructions="./project.md",
)

response = agency.process("Build a data pipeline")
```

---

## Timeline Summary

| Phase | Days | Hours | Priority |
|-------|------|-------|----------|
| 1. Foundation | 1-2 | 12 | CRITICAL |
| 2. Agent Enhancement | 3 | 13 | HIGH |
| 3. Agency Enhancement | 4-5 | 12 | HIGH |
| 4. Templates & Scaffolding | 6 | 10 | MEDIUM |
| 5. CLI & Integration | 7 | 7 | MEDIUM |
| 6. Testing | 8-9 | 14 | HIGH |
| 7. Documentation | 10 | 8 | MEDIUM |
| **TOTAL** | **10** | **76** | - |

---

*Document Version: 1.0*
*Created: 2026-01-02*
*Analysis by: 5 Parallel Sub-agents*
