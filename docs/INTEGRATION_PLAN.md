# Integration Plan: Adding Agency Swarm Features to indus-agents

## Overview

This document outlines the comprehensive plan to enhance indus-agents with Agency Swarm-like capabilities, enabling it to generate agent code, manage tasks, and provide production-ready multi-agent orchestration similar to Agency-Code.

---

## Goals

1. **Enable Code Generation**: Build agents that can generate other agents (like Agency-Code)
2. **Add File Operations**: Full filesystem manipulation capabilities
3. **Multi-LLM Support**: Work with OpenAI, Anthropic, and other providers
4. **Inter-Agent Communication**: Agents can delegate tasks to each other
5. **Production Ready**: Hooks, testing, and robust error handling
6. **Task Management**: Built-in todo/task tracking for complex workflows

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Core infrastructure for async operations and file handling

| Task | Priority | Effort | Details |
|------|----------|--------|---------|
| Async Agent Support | CRITICAL | High | Add async process() and process_with_tools() |
| Async Tool Registry | CRITICAL | Medium | Enable async tool execution |
| Bash Tool | CRITICAL | Medium | Shell command execution with timeout |
| Read Tool | CRITICAL | Medium | File reading with line selection |
| Write Tool | CRITICAL | Medium | File creation/overwriting |
| Edit Tool | CRITICAL | High | String replacement with validation |

**Deliverables**:
- `src/my_agent_framework/tools/bash.py`
- `src/my_agent_framework/tools/read.py`
- `src/my_agent_framework/tools/write.py`
- `src/my_agent_framework/tools/edit.py`
- Updated `agent.py` with async methods

---

### Phase 2: Enhanced Tools (Weeks 3-4)
**Goal**: Complete tool ecosystem for developer workflows

| Task | Priority | Effort | Details |
|------|----------|--------|---------|
| MultiEdit Tool | HIGH | Medium | Atomic multi-file editing |
| Glob Tool | HIGH | Medium | Pattern-based file discovery |
| Grep Tool | HIGH | Medium | Content search with ripgrep |
| Git Tool | HIGH | High | Version control operations |
| LS Tool | MEDIUM | Low | Directory listing |
| TodoWrite Tool | MEDIUM | Medium | Task management |

**Deliverables**:
- Complete `tools/` package with 10+ tools
- Tool base class with common patterns
- Tool documentation

---

### Phase 3: Agent System (Weeks 5-6)
**Goal**: Inter-agent communication and multi-model support

| Task | Priority | Effort | Details |
|------|----------|--------|---------|
| LLM Abstraction | CRITICAL | High | Support multiple providers |
| LiteLLM Integration | HIGH | Medium | Unified LLM interface |
| Agent Factory Pattern | HIGH | Medium | create_*_agent() functions |
| SendMessageHandoff | HIGH | High | Agent-to-agent communication |
| Instruction Files | MEDIUM | Low | Markdown-based instructions |
| Model Detection | MEDIUM | Low | Auto-detect provider capabilities |

**Deliverables**:
- `src/my_agent_framework/llm.py` - LLM abstraction layer
- Updated agent factory functions
- Handoff mechanism

---

### Phase 4: Advanced Features (Weeks 7-8)
**Goal**: Production-ready features and code generation

| Task | Priority | Effort | Details |
|------|----------|--------|---------|
| AgentHooks System | HIGH | Medium | Pre/post execution hooks |
| System Reminder Hook | MEDIUM | Low | Periodic instruction reminders |
| Message Filter Hook | MEDIUM | Low | Message preprocessing |
| Notebook Support | MEDIUM | Medium | Jupyter notebook tools |
| Web Search Tool | MEDIUM | Medium | Web search integration |
| Streaming Responses | MEDIUM | High | Real-time output |

**Deliverables**:
- `src/my_agent_framework/hooks.py`
- `tools/notebook_read.py`
- `tools/notebook_edit.py`
- `tools/web_search.py`

---

### Phase 5: Code Generation (Weeks 9-10)
**Goal**: Build agencies that create agencies (Genesis-like capability)

| Task | Priority | Effort | Details |
|------|----------|--------|---------|
| Agent Creator Agent | HIGH | High | Generates agent code |
| Tool Creator Agent | HIGH | Medium | Generates custom tools |
| Agency Factory | MEDIUM | High | Creates complete agencies |
| Template System | MEDIUM | Medium | Agent/tool templates |
| Testing Generator | LOW | Medium | Auto-generate tests |

**Deliverables**:
- `src/my_agent_framework/genesis/` - Code generation system
- Agent templates
- Documentation

---

## Architecture Design

### New Package Structure
```
src/my_agent_framework/
├── __init__.py
├── agent.py              # Enhanced with async
├── orchestrator.py       # Enhanced with handoffs
├── tools.py              # Legacy registry (deprecated)
├── memory.py
├── cli.py
├── llm.py                # NEW: LLM abstraction
├── hooks.py              # NEW: Hook system
├── tools/                # NEW: Tool package
│   ├── __init__.py
│   ├── base.py           # BaseTool class
│   ├── bash.py
│   ├── read.py
│   ├── write.py
│   ├── edit.py
│   ├── multi_edit.py
│   ├── glob.py
│   ├── grep.py
│   ├── git.py
│   ├── ls.py
│   ├── todo_write.py
│   ├── notebook_read.py
│   ├── notebook_edit.py
│   └── web_search.py
├── agents/               # NEW: Pre-built agents
│   ├── __init__.py
│   ├── developer_agent.py
│   ├── planner_agent.py
│   └── instructions/
│       ├── developer.md
│       └── planner.md
└── genesis/              # NEW: Code generation
    ├── __init__.py
    ├── agent_creator.py
    └── templates/
```

---

## Key Technical Decisions

### 1. Async-First Design
```python
# Current
def process(self, user_input: str) -> str:
    ...

# New
async def process(self, user_input: str) -> str:
    ...

# Backward compatibility
def process_sync(self, user_input: str) -> str:
    return asyncio.run(self.process(user_input))
```

### 2. Tool Base Class
```python
from pydantic import BaseModel, Field
from abc import abstractmethod

class BaseTool(BaseModel):
    """Base class for all tools"""

    @abstractmethod
    async def run(self) -> str:
        """Execute the tool"""
        pass

    def run_sync(self) -> str:
        """Synchronous execution"""
        return asyncio.run(self.run())
```

### 3. LLM Abstraction
```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list, tools: list = None) -> str:
        pass

class OpenAIProvider(LLMProvider):
    async def complete(self, messages, tools=None):
        ...

class AnthropicProvider(LLMProvider):
    async def complete(self, messages, tools=None):
        ...
```

### 4. Handoff Mechanism
```python
class SendMessageHandoff:
    """Tool for inter-agent communication"""
    target_agent: str
    message: str
    context: dict = {}

    async def run(self, agency):
        target = agency.get_agent(self.target_agent)
        return await target.process(self.message, context=self.context)
```

---

## Migration Strategy

### For Existing Users

1. **Tool Registry Compatibility**: Keep `@registry.register` decorator working
2. **Sync Methods Available**: Provide `*_sync()` versions of async methods
3. **Gradual Adoption**: New features are opt-in
4. **Documentation**: Clear migration guide

### Breaking Changes
- Tool execution will prefer async (sync wrappers provided)
- New `tools/` package replaces inline tool definitions
- Agent instantiation via factory functions (old way still works)

---

## Success Metrics

1. **Feature Parity**: 90% of Agency-Code features implemented
2. **Performance**: <100ms overhead for tool execution
3. **Test Coverage**: >80% code coverage
4. **Documentation**: All features documented with examples
5. **User Adoption**: Smooth migration for existing users

---

## Dependencies

### New Dependencies
```
litellm>=1.0.0          # Multi-LLM support
dulwich>=0.21.0         # Git operations (pure Python)
aiofiles>=23.0.0        # Async file operations
pytest-asyncio>=0.23.0  # Async testing
```

### Optional Dependencies
```
tiktoken>=0.5.0         # Accurate token counting
rich>=13.0.0            # Enhanced CLI output
```

---

## Next Steps

1. Review and approve this plan
2. Start Phase 1 implementation
3. Set up CI/CD for new features
4. Create feature branch per phase
5. Regular progress reviews

See individual phase documents for detailed implementation guides:
- `PHASE1_FOUNDATION.md`
- `PHASE2_TOOLS.md`
- `PHASE3_AGENTS.md`
- `PHASE4_FEATURES.md`
- `PHASE5_GENESIS.md`
