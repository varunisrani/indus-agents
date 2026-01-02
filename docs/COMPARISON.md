# Comprehensive Comparison: indus-agents vs Agency-Code/Agency-Swarm

## Executive Summary

**indus-agents** is a lightweight, specialized multi-agent system focused on query routing and tool management, while **Agency-Code/Agency-Swarm** is a comprehensive, production-grade framework built on Agency Swarm that replicates Claude Code functionality with advanced agent orchestration capabilities.

---

## Feature Comparison Table

| Feature | indus-agents | Agency-Code/Agency-Swarm |
|---------|--------------|--------------------------|
| **Core Framework** | Custom (Standalone) | Agency Swarm (Third-party) |
| **Agent Types** | 3 (General, Math, Time/Date) | 2+ (Developer, Planner, Extensible) |
| **Agent Count** | Fixed 3 | Configurable, unlimited subagents |
| **Tool Count** | 8 built-in | 14 built-in (code-focused) |
| **Routing Strategy** | Keyword-based regex patterns | Direct agent configuration |
| **Async Support** | Partial | Full async support |
| **LLM Support** | OpenAI only | Multiple (OpenAI, Anthropic, LiteLLM) |
| **Agent Communication** | Implicit (via tool results) | Explicit (SendMessageHandoff) |
| **File Operations** | Not included | Read, Edit, Write, MultiEdit, Git |
| **Web Search** | Not included | WebSearchTool, ClaudeWebSearch |
| **Notebook Support** | Not included | NotebookRead, NotebookEdit |
| **Hooks/Middleware** | Not present | System hooks (reminders, filters) |
| **Testing Framework** | Basic | Pytest + async support |
| **Production-Ready** | Emerging | Yes (Claude Code foundation) |

---

## Architecture Comparison

### indus-agents Architecture
```
indus-agents/
├── Agent (Core LLM interface)
│   ├── AgentConfig
│   ├── process() [basic]
│   ├── process_with_tools() [advanced]
│   └── Message history management
│
├── MultiAgentOrchestrator (Query Router)
│   ├── Keyword-based routing
│   ├── Confidence scoring
│   └── OrchestratorResponse dataclass
│
└── ToolRegistry (Tool Management)
    ├── Decorator-based registration
    ├── OpenAI schema generation
    └── 8 built-in tools
```

### Agency-Code Architecture
```
Agency-Code/
├── Agency (Orchestrator)
│   ├── Multiple agents (Planner, Developer, Subagents)
│   ├── Communication flows (SendMessageHandoff)
│   └── Shared instructions
│
├── AgencyCodeAgent (Developer)
│   ├── 14 specialized tools
│   ├── File operations (Bash, Read, Edit, Write, Git)
│   └── Model configuration + reasoning_effort
│
├── PlannerAgent (Strategist)
│   ├── Task breakdown
│   └── Strategic planning
│
└── Tool System (Agency Swarm)
    ├── 14 discrete tool classes
    └── Provider-specific adaptations
```

---

## Key Differences

### 1. Tool System
| Aspect | indus-agents | Agency-Code |
|--------|--------------|-------------|
| Pattern | Function with @register | Class inheriting BaseTool |
| Registration | Global registry | Per-agent tool assignment |
| Schema | Auto-generated | Pydantic Field definitions |
| Execution | Synchronous | Async-capable |

### 2. Agent Communication
| Aspect | indus-agents | Agency-Code |
|--------|--------------|-------------|
| Method | Implicit via tool results | Explicit SendMessageHandoff |
| Direction | Orchestrator → Agent only | Bidirectional between agents |
| State | Per-agent message history | Shared agency context |

### 3. LLM Support
| Aspect | indus-agents | Agency-Code |
|--------|--------------|-------------|
| Providers | OpenAI only | OpenAI, Anthropic, Grok, etc. |
| Configuration | AgentConfig class | Factory functions + LiteLLM |
| Features | Basic | Reasoning effort, model detection |

---

## What indus-agents Does Well

1. **Simplicity**: Self-contained in 3-4 files
2. **Clear Routing**: Transparent keyword-based decisions
3. **Type Safety**: Pydantic models throughout
4. **Auto Schema**: Tool schema auto-generation from type hints
5. **Confidence Scoring**: Each routing decision has a score
6. **Metadata Rich**: Complete OrchestratorResponse with timing

---

## Gaps to Fill in indus-agents

### Critical (Must Have)
- [ ] File operations (Bash, Read, Edit, Write)
- [ ] Git integration
- [ ] Async/await support
- [ ] Multiple LLM support

### High Priority
- [ ] Inter-agent communication (handoffs)
- [ ] Search tools (Glob, Grep)
- [ ] Web search capability
- [ ] Hooks/middleware system

### Medium Priority
- [ ] Notebook support
- [ ] Todo/task management
- [ ] Streaming responses
- [ ] Enhanced testing

### Low Priority
- [ ] CLI interface improvements
- [ ] Agent templates
- [ ] Pre-commit hooks

---

## Recommendation

**Use indus-agents for**: Learning, prototyping, simple routing systems

**Use Agency-Code for**: Production systems, multi-agent coordination, developer workflows

**To make indus-agents production-ready**: Follow the integration plan in `INTEGRATION_PLAN.md`
