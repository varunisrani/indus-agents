# Subagent Architecture Analysis: indus-agents vs Agency-Code

## Executive Summary

This document provides a detailed architectural comparison between indus-agents and Agency-Code (built on Agency-Swarm) to understand how to implement native subagent handling in indus-agents.

---

## 1. Framework Comparison Matrix

| Component | indus-agents | Agency-Code | Gap Level |
|-----------|--------------|-------------|-----------|
| **Agent Class** | Custom `Agent` with `AgentConfig` | Agency-Swarm `Agent` with `ModelSettings` | LOW |
| **Agency Orchestration** | Basic `Agency` class | Full Agency-Swarm integration | HIGH |
| **Communication Flows** | `(source, target)` tuples | `(source, target, SendMessageHandoff)` | HIGH |
| **Handoff Mechanism** | Function-based | Tool-based (LLM-driven) | HIGH |
| **Hooks System** | None | `AgentHooks` lifecycle | HIGH |
| **Model Detection** | None | `detect_model_type()` | MEDIUM |
| **Instruction Templates** | Basic renderer | Model-specific selection | MEDIUM |
| **Tool Registry** | Centralized | Distributed (class-based) | LOW |
| **Subagent Factory** | Basic pattern | Sophisticated factories | MEDIUM |
| **Shared Utilities** | None | `agent_utils.py`, `system_hooks.py` | HIGH |

---

## 2. Agent Architecture Comparison

### 2.1 indus-agents Agent Class

**Location**: `src/my_agent_framework/agent.py`

```python
class AgentConfig(BaseModel):
    model: str = Field(default="gpt-4o")
    max_tokens: int = Field(default=1024)
    temperature: float = Field(default=0.7)
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load from environment variables."""

class Agent:
    def __init__(
        self,
        name: str,
        role: str,
        config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None,
        context: Optional[Any] = None,
    ):
        self.name = name
        self.role = role
        self.config = config or AgentConfig.from_env()
        self.context = context
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def process(self, user_input: str) -> str:
        """Basic processing without tools."""

    def process_with_tools(
        self,
        user_input: str,
        tools: Optional[List[Dict]] = None,
        tool_executor: Optional[Any] = None,
        max_turns: int = 30
    ) -> str:
        """Processing with tool calling loop."""
```

**Strengths**:
- Pydantic-based validation
- Environment variable support
- Comprehensive retry logic
- Tool usage logging
- Conversation management

**Gaps**:
- No hooks parameter
- No parent_agent relationship
- No model-specific settings
- No reasoning effort control

### 2.2 Agency-Code Agent Pattern

**Location**: `Agency-Code/subagent_example/subagent_example.py`

```python
def create_subagent_example(
    model: str = "gpt-5",
    reasoning_effort: str = "low"
) -> Agent:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    instructions = render_instructions(current_dir + "/instructions.md", model)

    return Agent(
        name="SubagentExample",
        description="A template subagent...",
        instructions=instructions,
        tools=[Read, Bash, LS, Grep, Edit, Write, TodoWrite],
        model=get_model_instance(model),
        model_settings=create_model_settings(model, reasoning_effort, "detailed")
    )
```

**Strengths**:
- Factory function pattern
- Model-specific instruction selection
- Reasoning effort configuration
- Clean separation of concerns
- Reusable utilities

---

## 3. Agency/Orchestration Comparison

### 3.1 indus-agents Agency

**Location**: `src/my_agent_framework/agency.py`

```python
class HandoffType(Enum):
    MESSAGE = "message"
    FULL_CONTEXT = "full_context"

@dataclass
class HandoffResult:
    success: bool
    response: str
    from_agent: str
    to_agent: str
    processing_time: float
    error: Optional[str] = None

class Agency:
    def __init__(
        self,
        entry_agent: Agent,
        agents: Optional[List[Agent]] = None,
        communication_flows: Optional[List[Tuple[Agent, Agent]]] = None,
        shared_instructions: Optional[str] = None,
        name: str = "Agency",
        max_handoffs: int = 10,
    ):
        self.entry_agent = entry_agent
        self._agent_map: Dict[str, Agent] = {a.name: a for a in agents}
        self._flows: Dict[str, List[str]] = {}  # source -> [targets]

    def handoff(self, from_agent, to_agent_name, message, context) -> HandoffResult:
        """Execute handoff via direct agent.process() call."""

    def process(self, user_input: str) -> AgencyResponse:
        """Process through entry agent."""
```

**Characteristics**:
- Direct method-based handoffs
- Simple flow validation
- Handoff history tracking
- Shared context support

### 3.2 Agency-Code Agency

**Location**: `Agency-Code/agency.py`

```python
from agency_swarm import Agency
from agency_swarm.tools import SendMessageHandoff

agency = Agency(
    coder, planner,
    name="AgencyCode",
    communication_flows=[
        (coder, planner, SendMessageHandoff),  # Tool-based!
        (planner, coder, SendMessageHandoff),
    ],
    shared_instructions="./project-overview.md",
)
```

**Key Difference**:
- Tool-based handoffs allow LLM to decide when to delegate
- Explicit tool class in communication flows
- Automatic context injection

---

## 4. Tool System Comparison

### 4.1 indus-agents Tools

**Structure**:
```
tools/
├── __init__.py      # Centralized registry
├── base.py          # BaseTool with execute()
├── handoff.py       # Function-based handoff
└── dev/
    ├── bash.py
    ├── read.py
    ├── write.py
    ├── edit.py
    ├── glob.py
    ├── grep.py
    └── todo_write.py
```

**BaseTool Pattern**:
```python
class BaseTool(BaseModel, ABC):
    name: ClassVar[str] = "base_tool"
    description: ClassVar[str] = "Description"

    @abstractmethod
    def execute(self) -> str:
        """Execute the tool."""

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Generate OpenAI function schema."""
```

### 4.2 Agency-Code Tools

**Structure**:
```
tools/
├── __init__.py      # Exports all tools
├── bash.py
├── edit.py
├── git.py           # Missing in indus-agents
├── glob.py
├── grep.py
├── ls.py            # Missing in indus-agents
├── multi_edit.py    # Missing in indus-agents
├── notebook_edit.py # Missing in indus-agents
├── notebook_read.py # Missing in indus-agents
├── read.py
├── todo_write.py
└── write.py
```

**BaseTool Pattern**:
```python
from agency_swarm.tools import BaseTool

class Bash(BaseTool):
    """Docstring becomes description."""

    command: str = Field(..., description="...")
    timeout: int = Field(12000, description="...")

    def run(self):  # Note: run() not execute()
        """Execute the tool."""
```

---

## 5. Handoff Mechanism Deep Dive

### 5.1 indus-agents: Function-Based

```python
# tools/handoff.py
_current_agency: Optional["Agency"] = None

def handoff_to_agent(agent_name: str, message: str, context: Optional[str] = None) -> str:
    """Hand off to another agent."""
    if _current_agency is None:
        return "Error: No agency context"

    current = _current_agency.entry_agent  # PROBLEM: Always uses entry_agent!

    result = _current_agency.handoff(current, agent_name, message, context)
    return result.response if result.success else f"Error: {result.error}"
```

**Issues**:
1. Assumes entry_agent is current (breaks in multi-turn)
2. No call stack tracking
3. Global state management

### 5.2 Agency-Code: Tool-Based

```python
# Agency-Swarm's SendMessageHandoff
class SendMessageHandoff(BaseTool):
    """Send message to another agent."""

    to_agent: str = Field(..., description="Target agent name")
    message: str = Field(..., description="Message for target")

    def run(self):
        # Agency-Swarm handles:
        # 1. Getting current agent from context
        # 2. Validating communication flow
        # 3. Executing handoff with full context
        # 4. Returning response
        pass
```

**Advantages**:
1. LLM decides when to handoff
2. Context automatically managed
3. Clean tool-based interface
4. No global state issues

---

## 6. Hooks/Lifecycle System

### 6.1 indus-agents: None

Currently no lifecycle hooks. Processing is a single path:
```
user_input -> process_with_tools() -> tool loop -> response
```

### 6.2 Agency-Code: Full Lifecycle

```python
class AgentHooks(ABC):
    async def on_start(self, context, agent) -> None: pass
    async def on_end(self, context, agent, output) -> None: pass
    async def on_tool_start(self, context, agent, tool) -> None: pass
    async def on_tool_end(self, context, agent, tool, result) -> None: pass
    async def on_llm_start(self, context, agent, messages) -> None: pass
    async def on_llm_end(self, context, agent, response) -> None: pass
    async def on_handoff(self, context, agent, source) -> None: pass

class SystemReminderHook(AgentHooks):
    """Injects periodic reminders."""

    def __init__(self, tool_call_interval: int = 15):
        self.tool_call_count = 0
        self.tool_call_interval = tool_call_interval

    async def on_tool_end(self, context, agent, tool, result):
        self.tool_call_count += 1
        if self.tool_call_count >= self.tool_call_interval:
            self._inject_reminder(context)
```

---

## 7. Instruction Template System

### 7.1 indus-agents: Basic

**Location**: `src/my_agent_framework/templates/renderer.py`

```python
def render_instructions(template_path: str, agent_name: str = "Agent", ...) -> str:
    """Render with basic placeholders."""
    with open(template_path, 'r') as f:
        content = f.read()

    placeholders = {
        "{{agent_name}}": agent_name,
        "{{cwd}}": os.getcwd(),
        "{{today}}": datetime.now().strftime("%Y-%m-%d"),
    }
    # ... replacement
```

### 7.2 Agency-Code: Model-Aware

**Location**: `Agency-Code/shared/agent_utils.py`

```python
def select_instructions_file(base_dir: str, model: str) -> str:
    """Select model-specific instructions."""
    filename = (
        "instructions-gpt-5.md"
        if model.lower().startswith("gpt-5")
        else "instructions.md"
    )
    return os.path.join(base_dir, filename)

def render_instructions(template_path: str, model: str, ...) -> str:
    """Render with model awareness."""
    placeholders = {
        "{cwd}": os.getcwd(),
        "{is_git_repo}": os.path.isdir(".git"),
        "{platform}": platform.system(),
        "{os_version}": platform.release(),
        "{today}": datetime.now().strftime("%Y-%m-%d"),
        "{model}": model,
    }
```

**Key Differences**:
- Agency-Code uses single braces `{placeholder}`
- Model-specific file selection
- More placeholders (platform, git status, model)

---

## 8. Subagent Factory Pattern

### 8.1 indus-agents Example

**Location**: `src/test_agents/qa_tester_agent/qa_tester_agent.py`

```python
def create_qa_tester_agent(
    model: str = "gpt-5-mini",
    config: Optional[AgentConfig] = None,
    reasoning_effort: str = "medium"
) -> Agent:
    instructions = render_instructions(
        os.path.join(current_dir, "instructions.md"),
        model=model
    )

    agent_config = config or AgentConfig.from_env()
    agent_config.model = model

    return Agent(
        name="QaTester",
        role="A quality assurance testing agent",
        config=agent_config,
        system_prompt=instructions,
        tools=[Read, Write, Bash],
    )
```

### 8.2 Agency-Code Example

**Location**: `Agency-Code/subagent_example/subagent_example.py`

```python
def create_subagent_example(
    model: str = "gpt-5",
    reasoning_effort: str = "low"
) -> Agent:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    instructions = render_instructions(current_dir + "/instructions.md", model)

    return Agent(
        name="SubagentExample",
        description="A template subagent...",
        instructions=instructions,
        tools=[Read, Bash, LS, Grep, Edit, Write, TodoWrite],
        model=get_model_instance(model),
        model_settings=create_model_settings(model, reasoning_effort, "detailed")
    )
```

**Differences**:
- Agency-Code uses `model_settings` for reasoning
- Agency-Code uses `get_model_instance()` for multi-provider support
- Different parameter naming (`system_prompt` vs `instructions`)

---

## 9. Recommended Architecture for indus-agents

### 9.1 Enhanced Agent Class

```python
class Agent:
    def __init__(
        self,
        name: str,
        role: str,
        config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None,
        context: Optional[Any] = None,
        # NEW parameters
        hooks: Optional[AgentHooks] = None,
        parent_agent: Optional["Agent"] = None,
        model_settings: Optional[ModelSettings] = None,
    ):
        self.hooks = hooks
        self.parent_agent = parent_agent
        self.model_settings = model_settings
```

### 9.2 Enhanced Agency Class

```python
class Agency:
    def __init__(
        self,
        entry_agent: Agent,
        agents: Optional[List[Agent]] = None,
        communication_flows: Optional[List[Tuple[Agent, Agent, type]]] = None,  # With tool class
        # ...
    ):
        # Register SendMessageHandoff for each flow
        self._register_handoff_tools()

    def _register_handoff_tools(self):
        """Register handoff tools based on communication flows."""
        for source, target, tool_class in self.communication_flows:
            # Make tool available to source agent
```

### 9.3 SendMessageHandoff Tool

```python
class SendMessageHandoff(BaseTool):
    name: ClassVar[str] = "send_message_handoff"
    description: ClassVar[str] = "Hand off task to another agent"

    to_agent: str = Field(..., description="Target agent name")
    message: str = Field(..., description="Task/message for target")

    def execute(self) -> str:
        agency = get_current_agency()
        current_agent = get_current_agent()  # From call stack

        if not agency.can_handoff(current_agent.name, self.to_agent):
            return f"Error: Cannot handoff to {self.to_agent}"

        result = agency.handoff(current_agent, self.to_agent, self.message)
        return result.response
```

---

## 10. Key Insights

### What indus-agents Does Well
1. **Clean AgentConfig** - Pydantic-based with env support
2. **Comprehensive logging** - Tool-specific formatted output
3. **Retry logic** - Built-in failure recovery
4. **Centralized registry** - Easy tool management
5. **Conversation management** - History manipulation

### What Agency-Code Does Better
1. **Tool-based handoffs** - LLM-driven delegation
2. **Lifecycle hooks** - Extensible processing
3. **Model-specific handling** - Multi-provider support
4. **Instruction templates** - Dynamic context injection
5. **Factory pattern** - Reusable agent creation

### Integration Strategy

1. **Keep** indus-agents' AgentConfig and logging
2. **Add** shared utilities (agent_utils, system_hooks)
3. **Implement** SendMessageHandoff as a tool
4. **Enhance** Agency with tool-based communication flows
5. **Add** hooks to Agent processing
6. **Preserve** backward compatibility

---

## 11. File Structure After Implementation

```
src/my_agent_framework/
├── __init__.py
├── agent.py                    # Enhanced with hooks, parent
├── agency.py                   # Enhanced with tool-based flows
├── orchestrator.py
├── tool_usage_logger.py
├── cli.py
├── memory.py
├── shared/                     # NEW
│   ├── __init__.py
│   ├── agent_utils.py
│   ├── system_hooks.py
│   └── utils.py
├── tools/
│   ├── __init__.py             # Updated exports
│   ├── base.py                 # Enhanced with run() alias
│   ├── send_message_handoff.py # NEW
│   ├── handoff.py              # Legacy (deprecated)
│   └── dev/
│       ├── bash.py
│       ├── read.py
│       ├── write.py
│       ├── edit.py
│       ├── glob.py
│       ├── grep.py
│       ├── todo_write.py
│       ├── git.py              # NEW
│       └── ls.py               # NEW
└── templates/
    ├── __init__.py
    ├── renderer.py             # Enhanced
    ├── scaffolder.py           # Enhanced
    └── subagent_template/      # NEW
        ├── __init__.py.template
        ├── agent.py.template
        └── instructions.md.template
```

---

*Document Version: 1.0*
*Created: 2026-01-02*
*Analysis by: 5 Parallel Sub-agents*
