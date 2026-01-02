# Comprehensive Framework Comparison: indus-agents vs agency-swarm

## Executive Summary

This document provides an in-depth comparison between **indus-agents** (our custom framework) and **agency-swarm** (VRSEN's production-ready framework). The analysis covers architecture, tools, orchestration, memory management, and ecosystem features.

| Aspect | indus-agents | agency-swarm |
|--------|--------------|--------------|
| **Philosophy** | Simplicity & Learning | Enterprise Production |
| **Lines of Code** | ~2,500 | ~15,000+ |
| **Multi-Agent** | Limited (Orchestrator) | Full Support |
| **Production Ready** | No | Yes |
| **Test Coverage** | Basic (~9 files) | Comprehensive (130+ files, 92%) |

---

## 1. Agent Architecture Comparison

### indus-agents Agent Design

**Pattern**: Standalone, self-contained class with no inheritance

```python
class Agent:
    """AI Agent that interacts with OpenAI's API."""

    def __init__(self, name: str, role: str, config: AgentConfig = None):
        self.name = name
        self.role = role
        self.config = config or AgentConfig.from_env()
        self.client = OpenAI(api_key=api_key)
        self.messages: List[Dict[str, Any]] = []
```

**Characteristics**:
- Direct OpenAI SDK dependency only
- Simple message list for history
- Synchronous execution only
- ~500 lines of code
- Easy to understand and modify

### agency-swarm Agent Design

**Pattern**: Extended framework with sophisticated inheritance

```python
from agents import Agent as BaseAgent

class Agent(BaseAgent[MasterContext]):
    """Extends base agents.Agent with multi-agent collaboration."""

    files_folder: str | Path | None
    tools_folder: str | Path | None
    description: str | None
    file_manager: AgentFileManager | None
    _tool_concurrency_manager: ToolConcurrencyManager
```

**Characteristics**:
- Inherits from OpenAI Agents SDK
- Generic type parameterization with MasterContext
- Async/await execution model
- File management, tool discovery, guardrails
- ~5,000+ lines across modules

### Comparison Matrix

| Feature | indus-agents | agency-swarm |
|---------|--------------|--------------|
| Inheritance | None | agents.Agent[MasterContext] |
| Configuration | Pydantic BaseModel | Multi-layer kwargs |
| State Management | Simple message list | Runtime state + Context + Threads |
| Execution | Synchronous | Async with streaming |
| Tool Support | Basic registry | Auto-discovery, MCP, concurrency |
| File Management | None | Full system with vector stores |
| API Surface | 8 methods | 40+ methods |
| Complexity | 2/10 | 9/10 |

---

## 2. Tool Systems Comparison

### indus-agents Tool System

**Pattern**: Decorator-based registry with automatic schema generation

```python
from tools import registry

@registry.register
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression, {"__builtins__": {}}, {}))
```

**Features**:
- Single global registry
- Automatic OpenAI schema generation from type hints
- Simple execution via `registry.execute(name, **kwargs)`
- Built-in tools: calculator, time/date, text manipulation

**Limitations**:
- No async support
- No Pydantic validation
- No context injection
- Function-based only

### agency-swarm Tool System

**Pattern**: Multiple sophisticated approaches

**1. BaseTool (Class-based with Pydantic)**:
```python
class AddTool(BaseTool):
    """Add two numbers with validation."""
    a: int = Field(..., ge=0, description="First number")
    b: int = Field(..., ge=0, description="Second number")

    @field_validator("a", "b")
    def validate_range(cls, v):
        if v > 100:
            raise ValueError("Value must be <= 100")
        return v

    def run(self) -> str:
        return str(self.a + self.b)
```

**2. @function_tool decorator**:
```python
@function_tool
def add_numbers(args: AddArgs) -> str:
    """Add two numbers."""
    return str(args.a + args.b)
```

**3. FunctionTool (Dynamic)**:
```python
tool = FunctionTool(
    name="send_message",
    params_json_schema={...},
    on_invoke_tool=async_handler
)
```

**Features**:
- Full Pydantic validation
- Field and model validators
- Async/sync execution
- Context access via `self.context`
- OpenAPI schema import
- MCP server integration
- Tool concurrency management

### Tool Comparison Matrix

| Feature | indus-agents | agency-swarm |
|---------|--------------|--------------|
| Definition Pattern | Decorator only | 4 patterns (BaseTool, function_tool, FunctionTool, OpenAPI) |
| Validation | Type hints only | Full Pydantic |
| Async Support | No | Yes |
| Context Access | No | Yes (self.context) |
| Concurrency Control | No | Yes (one_call_at_a_time) |
| Schema Generation | Automatic (basic) | Pydantic (advanced) |
| Built-in Tools | 9 basic utilities | 15+ including shell, file, MCP |

---

## 3. Multi-Agent Orchestration

### indus-agents: Centralized Hub-and-Spoke

**Architecture**: Single orchestrator routes queries to specialized agents

```python
class MultiAgentOrchestrator:
    agents: Dict[AgentType, Agent]  # GENERAL, MATH, TIME_DATE
    routing_keywords: Dict[AgentType, Dict[str, float]]

    def process(self, query: str) -> OrchestratorResponse:
        routing_decision = self.route_query(query)  # Keyword scoring
        selected_agent = self.agents[routing_decision.agent_type]
        return selected_agent.process_with_tools(query)
```

**Flow**:
```
User → Orchestrator → [Keyword Routing] → Single Agent → Response
```

**Features**:
- Deterministic keyword-based routing
- Confidence scores and reasoning
- Predefined agent types (enum-based)
- No agent-to-agent communication

### agency-swarm: Decentralized Communication Graph

**Architecture**: Agents form communication flows and message each other

```python
agency = Agency(
    ceo_agent,  # Entry point
    communication_flows=[
        (ceo_agent, developer_agent),   # CEO can message Developer
        (developer_agent, qa_agent),    # Developer can message QA
    ]
)
```

**Flow**:
```
User → Entry Agent → SendMessage(Sub-Agent) → Sub-Agent → ... → Response
```

**Features**:
- LLM-driven routing decisions
- Multi-hop agent chains
- Parallel sub-agent execution
- Bidirectional communication flows
- Thread isolation per agent pair

### Orchestration Comparison

| Aspect | indus-agents | agency-swarm |
|--------|--------------|--------------|
| Pattern | Hub-and-spoke | Directed graph |
| Routing | Keyword scoring | LLM-driven |
| Agent Communication | None | SendMessage tool |
| Multi-hop | No | Yes |
| Parallel Execution | No | Yes |
| Transparency | High (explicit scores) | Medium (LLM reasoning) |
| Flexibility | Low (predefined types) | High (any agent configuration) |

---

## 4. Memory and Persistence

### indus-agents Memory System

**Class**: `ConversationMemory` with circular buffer

```python
memory = ConversationMemory(max_messages=1000)
memory.add_message("user", "Hello!")
stats = memory.get_statistics()  # tokens, cost, counts
memory.save_to_file("conversation.json")
```

**Features**:
- Rich Message objects with timestamps and metadata
- Token estimation (4 chars/token heuristic)
- Cost estimation (hardcoded pricing)
- Built-in JSON/text export
- Context window management
- Text search and filtering

**Limitations**:
- Single conversation per instance
- File-based persistence only
- Inaccurate token counting
- Outdated pricing data

### agency-swarm Memory System

**Classes**: `MessageStore` + `ThreadManager` with callbacks

```python
manager = ThreadManager(
    load_threads_callback=lambda: load_from_db(),
    save_threads_callback=lambda msgs: save_to_db(msgs)
)
```

**Features**:
- Flat storage with agent/callerAgent metadata
- Thread isolation per agent pair
- Shared user thread across entry agents
- Callback-based persistence (any backend)
- Automatic save on message add
- Accurate token counting from API responses
- Comprehensive pricing database (100s of models)

### Memory Comparison

| Feature | indus-agents | agency-swarm |
|---------|--------------|--------------|
| Architecture | Circular buffer | Flat list + metadata |
| Multi-Agent | No | Yes (thread isolation) |
| Persistence | Built-in file only | Callbacks (flexible) |
| Auto-Save | No | Yes |
| Token Counting | Heuristic (~4 chars) | Actual API response |
| Cost Tracking | Hardcoded (4 models) | Real-time (100s of models) |
| Context Window | Built-in management | SDK-level |

---

## 5. Features and Ecosystem

### Feature Comparison Matrix

| Feature | indus-agents | agency-swarm |
|---------|--------------|--------------|
| **CLI** | 6 basic commands | 3 advanced + demos |
| **Streaming** | No | Full SSE support |
| **Visualization** | No | Interactive HTML |
| **Hooks/Callbacks** | No | Comprehensive |
| **MCP Support** | No | Local + Hosted |
| **FastAPI** | No | Built-in integration |
| **Observability** | No | 3 platforms (Langfuse, AgentOps, OpenAI) |
| **Multi-Model** | No | Yes (LiteLLM) |
| **Guardrails** | No | Input/Output validation |
| **File Handling** | No | Attachments + Vector stores |
| **Examples** | 2 files | 27 files |
| **Tests** | 9 files | 130+ files (92% coverage) |

### CLI Comparison

**indus-agents**:
- `run` - Execute single query
- `interactive` - Chat session
- `list-tools` - Show tools
- `test-connection` - API check

**agency-swarm**:
- `create-agent-template` - Scaffold agents
- `migrate-agent` - Convert from Assistants API
- `import-tool` - Add built-in tools
- `terminal_demo()` - Interactive terminal
- `copilot_demo()` - Web UI demo

### Integration Options

| Integration | indus-agents | agency-swarm |
|-------------|--------------|--------------|
| OpenAI | Direct SDK | Agents SDK |
| Anthropic | No | Via LiteLLM |
| Google Gemini | No | Via LiteLLM |
| Azure OpenAI | No | Via LiteLLM |
| FastAPI | No | Built-in |
| Langfuse | No | Yes |
| AgentOps | No | Yes |

---

## 6. Code Quality and Testing

### indus-agents

```
tests/
├── test_agent.py
├── test_cli.py
├── test_config.py
├── test_integration.py
├── test_memory.py
├── test_orchestrator.py
└── test_tools.py
```

- **Test Files**: 9
- **Coverage**: Unknown
- **Stack**: pytest, pytest-asyncio, pytest-mock

### agency-swarm

```
tests/
├── integration/
│   ├── agency/ - Multi-agency, handoffs
│   ├── communication/ - Streaming, send_message
│   ├── fastapi/ - API endpoints
│   ├── guardrails/ - Validation
│   ├── mcp/ - MCP integration
│   ├── persistence/ - Thread isolation
│   └── tools/ - Tool execution
├── test_agency_modules/
└── test_agent_modules/
```

- **Test Files**: 130+
- **Coverage**: 92% (documented)
- **Stack**: pytest, mypy, comprehensive integration tests

---

## 7. When to Use Each Framework

### Choose indus-agents if you:

- Are learning agent concepts
- Need a simple chatbot prototype
- Want to understand agent internals
- Prefer minimal dependencies
- Have single-agent use cases
- Want full control over implementation
- Need synchronous execution only

### Choose agency-swarm if you:

- Need production-ready solution
- Require multi-agent orchestration
- Want streaming support
- Need FastAPI integration
- Require MCP support
- Want built-in visualization
- Need observability integrations
- Are building enterprise applications
- Require comprehensive testing
- Need migration from Assistants API

---

## 8. Conclusion

**indus-agents** is a **minimalist, educational framework** that prioritizes:
- Simplicity over features
- Transparency over abstraction
- Learning over production
- Single-agent focus

**agency-swarm** is an **enterprise-grade framework** that prioritizes:
- Features over simplicity
- Production readiness
- Multi-agent collaboration
- Comprehensive ecosystem

### Overall Scores

| Criteria | indus-agents | agency-swarm |
|----------|--------------|--------------|
| Simplicity | 9/10 | 4/10 |
| Learning Curve | 9/10 (easy) | 5/10 (moderate) |
| Features | 3/10 | 9/10 |
| Production Ready | 3/10 | 9/10 |
| Multi-Agent | 4/10 | 9/10 |
| Testing | 4/10 | 9/10 |
| Documentation | 5/10 | 8/10 |
| **Overall** | **5.3/10** | **7.6/10** |

The 10x difference in complexity reflects fundamentally different target audiences and use cases. Neither is objectively "better" - they serve different purposes.

---

## Appendix: File References

### indus-agents
- `agent.py` - Agent class implementation
- `tools.py` - Tool registry and built-in tools
- `orchestrator.py` - Multi-agent orchestrator
- `memory.py` - Conversation memory management
- `cli.py` - Command-line interface

### agency-swarm
- `src/agency_swarm/agent/core.py` - Agent class
- `src/agency_swarm/agency/core.py` - Agency orchestration
- `src/agency_swarm/tools/` - Tool system
- `src/agency_swarm/utils/thread.py` - Thread management
- `examples/` - 27 example files
