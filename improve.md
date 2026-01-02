# indus-agents Framework Enhancement Recommendations

## Executive Summary

Based on the comprehensive analysis comparing indus-agents with agency-swarm, this document outlines strategic improvements to enhance indus-agents into a more powerful, production-ready framework while maintaining its core philosophy of simplicity.

---

## Priority Matrix

| Priority | Enhancement | Impact | Effort |
|----------|------------|--------|--------|
| P0 | Async/Streaming Support | High | Medium |
| P0 | Multi-Agent Communication | High | High |
| P1 | Enhanced Tool System | High | Medium |
| P1 | Improved Persistence | High | Low |
| P2 | MCP Integration | Medium | Medium |
| P2 | Observability | Medium | Low |
| P3 | FastAPI Integration | Medium | Medium |
| P3 | Visualization | Low | Medium |

---

## P0: Critical Improvements

### 1. Async/Streaming Support

**Current State**: Synchronous execution only, no streaming

**Problem**:
- Users cannot see responses as they generate
- Blocking I/O limits scalability
- No real-time feedback for long-running tasks

**Recommended Implementation**:

```python
# agent.py - Add async methods

import asyncio
from openai import AsyncOpenAI

class Agent:
    def __init__(self, ...):
        self.async_client = AsyncOpenAI(api_key=api_key)

    async def process_async(self, user_input: str) -> str:
        """Async version of process method."""
        self.messages.append({"role": "user", "content": user_input})

        response = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.messages
            ],
            **self._get_completion_params()
        )

        assistant_message = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_message})
        return assistant_message

    async def process_stream(self, user_input: str):
        """Streaming response generator."""
        self.messages.append({"role": "user", "content": user_input})

        stream = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.messages
            ],
            stream=True,
            **self._get_completion_params()
        )

        full_response = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        self.messages.append({"role": "assistant", "content": full_response})
```

**CLI Integration**:

```python
# cli.py - Add streaming command

@app.command()
def stream(
    message: str,
    model: str = "gpt-4o"
):
    """Stream a response in real-time."""
    agent = Agent("Assistant", "General assistant")

    async def run_stream():
        async for chunk in agent.process_stream(message):
            print(chunk, end="", flush=True)
        print()  # Newline at end

    asyncio.run(run_stream())
```

**Effort**: 2-3 days
**Impact**: Enables real-time responses, better UX

---

### 2. Multi-Agent Communication

**Current State**: Orchestrator selects ONE agent per query, no inter-agent communication

**Problem**:
- Complex tasks cannot be delegated between agents
- No collaboration between specialized agents
- Limited to simple routing patterns

**Recommended Implementation**:

#### Step 1: Add Communication Flows

```python
# communication.py - New file

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable

@dataclass
class AgentFlow:
    """Defines allowed communication between agents."""
    sender: str
    receiver: str
    tool_class: Optional[type] = None

class CommunicationManager:
    """Manages inter-agent communication."""

    def __init__(self):
        self.flows: Dict[str, List[str]] = {}  # sender -> [receivers]
        self.agents: Dict[str, 'Agent'] = {}

    def register_agent(self, agent: 'Agent'):
        """Register an agent with the manager."""
        self.agents[agent.name] = agent
        if agent.name not in self.flows:
            self.flows[agent.name] = []

    def add_flow(self, sender: str, receiver: str):
        """Add a communication flow."""
        if sender not in self.flows:
            self.flows[sender] = []
        if receiver not in self.flows[sender]:
            self.flows[sender].append(receiver)

    def can_communicate(self, sender: str, receiver: str) -> bool:
        """Check if sender can communicate with receiver."""
        return receiver in self.flows.get(sender, [])

    def get_available_recipients(self, sender: str) -> List[str]:
        """Get list of agents the sender can communicate with."""
        return self.flows.get(sender, [])
```

#### Step 2: Add SendMessage Tool

```python
# tools.py - Add SendMessage tool

class SendMessageTool:
    """Tool for agent-to-agent communication."""

    def __init__(self, sender_agent: 'Agent', comm_manager: 'CommunicationManager'):
        self.sender = sender_agent
        self.comm_manager = comm_manager

    def get_schema(self) -> Dict:
        """Generate OpenAI function schema."""
        recipients = self.comm_manager.get_available_recipients(self.sender.name)

        return {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": "Send a message to another agent for collaboration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "enum": recipients,
                            "description": "Name of the agent to message"
                        },
                        "message": {
                            "type": "string",
                            "description": "The message/task to send"
                        }
                    },
                    "required": ["recipient", "message"]
                }
            }
        }

    async def execute(self, recipient: str, message: str) -> str:
        """Execute the send_message tool."""
        if not self.comm_manager.can_communicate(self.sender.name, recipient):
            return f"Error: Cannot communicate with {recipient}"

        target_agent = self.comm_manager.agents.get(recipient)
        if not target_agent:
            return f"Error: Agent {recipient} not found"

        # Call the recipient agent
        response = await target_agent.process_async(
            f"[Message from {self.sender.name}]: {message}"
        )
        return response
```

#### Step 3: Create Agency Class

```python
# agency.py - New file

from typing import List, Tuple, Optional

class Agency:
    """Multi-agent orchestration with communication flows."""

    def __init__(
        self,
        *entry_point_agents: 'Agent',
        communication_flows: List[Tuple['Agent', 'Agent']] = None
    ):
        self.comm_manager = CommunicationManager()
        self.entry_points = list(entry_point_agents)

        # Register all agents
        all_agents = set(entry_point_agents)
        if communication_flows:
            for sender, receiver in communication_flows:
                all_agents.add(sender)
                all_agents.add(receiver)
                self.comm_manager.add_flow(sender.name, receiver.name)

        for agent in all_agents:
            self.comm_manager.register_agent(agent)
            # Add send_message tool to agents with outgoing flows
            if self.comm_manager.get_available_recipients(agent.name):
                send_tool = SendMessageTool(agent, self.comm_manager)
                agent.add_tool(send_tool)

    async def get_response(
        self,
        message: str,
        recipient_agent: Optional['Agent'] = None
    ) -> str:
        """Get response from the agency."""
        target = recipient_agent or self.entry_points[0]
        return await target.process_async(message)
```

**Usage Example**:

```python
# Create specialized agents
ceo = Agent("CEO", "Coordinate project tasks")
developer = Agent("Developer", "Write code")
qa = Agent("QA", "Test code")

# Create agency with communication flows
agency = Agency(
    ceo,  # Entry point
    communication_flows=[
        (ceo, developer),      # CEO can message Developer
        (developer, qa),       # Developer can message QA
    ]
)

# Process request - CEO can delegate to Developer, who can delegate to QA
response = await agency.get_response(
    "Build and test a login feature"
)
```

**Effort**: 5-7 days
**Impact**: Enables complex multi-agent workflows

---

## P1: High Priority Improvements

### 3. Enhanced Tool System

**Current State**: Function-only tools with basic type hint schema generation

**Recommended Enhancements**:

#### A. Add Pydantic-Based Tools

```python
# tools.py - Add BaseTool class

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Any

class BaseTool(BaseModel, ABC):
    """Base class for Pydantic-based tools."""

    class Config:
        arbitrary_types_allowed = True

    class ToolConfig:
        strict: bool = False
        async_execution: bool = False

    @abstractmethod
    def run(self) -> str:
        """Execute the tool."""
        pass

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Generate OpenAI function schema from Pydantic model."""
        schema = cls.model_json_schema()

        # Extract parameters
        parameters = {
            k: v for k, v in schema.items()
            if k not in ("title", "description")
        }
        parameters["required"] = [
            k for k, v in parameters.get("properties", {}).items()
            if "default" not in v
        ]

        return {
            "type": "function",
            "function": {
                "name": cls.__name__,
                "description": cls.__doc__ or f"Execute {cls.__name__}",
                "parameters": parameters
            }
        }
```

**Example Usage**:

```python
from pydantic import Field, field_validator

class DivideNumbers(BaseTool):
    """Divide two numbers safely."""

    numerator: float = Field(..., description="The numerator")
    denominator: float = Field(..., description="The denominator (non-zero)")

    @field_validator('denominator')
    @classmethod
    def check_nonzero(cls, v):
        if v == 0:
            raise ValueError("Denominator cannot be zero")
        return v

    def run(self) -> str:
        return str(self.numerator / self.denominator)
```

#### B. Add Async Tool Support

```python
class AsyncBaseTool(BaseTool):
    """Base class for async tools."""

    @abstractmethod
    async def run(self) -> str:
        """Execute the tool asynchronously."""
        pass
```

#### C. Add Context Injection

```python
class ToolContext:
    """Context available to tools during execution."""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

class BaseTool(BaseModel, ABC):
    _context: ToolContext = None

    @property
    def context(self) -> ToolContext:
        return self._context
```

**Effort**: 3-4 days
**Impact**: Better validation, async support, shared state

---

### 4. Improved Persistence System

**Current State**: File-based persistence only, no callback system

**Recommended Implementation**:

```python
# persistence.py - New file

from typing import Callable, List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Type aliases
LoadCallback = Callable[[], List[Dict[str, Any]]]
SaveCallback = Callable[[List[Dict[str, Any]]], None]

class PersistenceBackend(ABC):
    """Abstract base for persistence backends."""

    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def save(self, messages: List[Dict[str, Any]]) -> None:
        pass

class FilePersistence(PersistenceBackend):
    """File-based persistence."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Dict[str, Any]]:
        import json
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save(self, messages: List[Dict[str, Any]]) -> None:
        import json
        with open(self.file_path, 'w') as f:
            json.dump(messages, f, indent=2)

class CallbackPersistence(PersistenceBackend):
    """Callback-based persistence for custom backends."""

    def __init__(
        self,
        load_callback: LoadCallback,
        save_callback: SaveCallback
    ):
        self._load = load_callback
        self._save = save_callback

    def load(self) -> List[Dict[str, Any]]:
        return self._load()

    def save(self, messages: List[Dict[str, Any]]) -> None:
        self._save(messages)

class ThreadManager:
    """Manages conversation threads with persistence."""

    def __init__(
        self,
        persistence: Optional[PersistenceBackend] = None,
        auto_save: bool = True
    ):
        self.persistence = persistence
        self.auto_save = auto_save
        self._messages: List[Dict[str, Any]] = []

        if persistence:
            self._messages = persistence.load()

    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message and optionally auto-save."""
        self._messages.append(message)
        if self.auto_save and self.persistence:
            self.persistence.save(self._messages)

    def get_messages(
        self,
        agent: Optional[str] = None,
        caller_agent: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get messages filtered by agent pair."""
        if agent is None and caller_agent is None:
            return self._messages.copy()

        return [
            m for m in self._messages
            if m.get("agent") == agent and m.get("callerAgent") == caller_agent
        ]
```

**Usage Examples**:

```python
# File persistence
manager = ThreadManager(
    persistence=FilePersistence("./conversations.json")
)

# Database persistence
def load_from_db():
    return db.query("SELECT * FROM messages")

def save_to_db(messages):
    db.execute("UPDATE messages SET data = ?", json.dumps(messages))

manager = ThreadManager(
    persistence=CallbackPersistence(load_from_db, save_to_db)
)
```

**Effort**: 2-3 days
**Impact**: Flexible persistence, database support

---

## P2: Medium Priority Improvements

### 5. Accurate Token Counting and Cost Tracking

**Current State**: Heuristic estimation (4 chars/token), hardcoded pricing

**Recommended Implementation**:

```python
# usage.py - New file

import tiktoken
from dataclasses import dataclass
from typing import Optional

# Pricing data (update regularly)
MODEL_PRICING = {
    "gpt-4o": {"input": 0.0000025, "output": 0.00001},
    "gpt-4o-mini": {"input": 0.00000015, "output": 0.0000006},
    "gpt-4-turbo": {"input": 0.00001, "output": 0.00003},
    "gpt-3.5-turbo": {"input": 0.0000005, "output": 0.0000015},
    "o1-preview": {"input": 0.000015, "output": 0.00006},
    "o1-mini": {"input": 0.000003, "output": 0.000012},
}

@dataclass
class UsageStats:
    """Token usage and cost statistics."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0

class TokenCounter:
    """Accurate token counting using tiktoken."""

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def count_messages(self, messages: list) -> int:
        """Count tokens in message list."""
        total = 0
        for msg in messages:
            total += 4  # Message overhead
            total += self.count_tokens(msg.get("content", ""))
            total += self.count_tokens(msg.get("role", ""))
        total += 2  # Completion overhead
        return total

class CostCalculator:
    """Calculate costs from token usage."""

    def calculate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> UsageStats:
        """Calculate usage stats with costs."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o"])

        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]

        return UsageStats(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost
        )
```

**Effort**: 1-2 days
**Impact**: Accurate cost tracking for production use

---

### 6. MCP (Model Context Protocol) Integration

**Recommended Implementation**:

```python
# mcp.py - New file

from typing import List, Optional
import subprocess
import json

class MCPServer:
    """Base class for MCP servers."""

    def __init__(self, name: str):
        self.name = name
        self._tools: List[dict] = []

    async def get_tools(self) -> List[dict]:
        """Get available tools from the server."""
        return self._tools

class MCPServerStdio(MCPServer):
    """MCP server via stdio communication."""

    def __init__(
        self,
        name: str,
        command: str,
        args: List[str] = None
    ):
        super().__init__(name)
        self.command = command
        self.args = args or []
        self._process = None

    async def start(self):
        """Start the MCP server process."""
        self._process = subprocess.Popen(
            [self.command] + self.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    async def stop(self):
        """Stop the MCP server process."""
        if self._process:
            self._process.terminate()
            self._process = None

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Call a tool on the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
            "id": 1
        }

        self._process.stdin.write(json.dumps(request).encode() + b'\n')
        self._process.stdin.flush()

        response = self._process.stdout.readline()
        return json.loads(response)

class MCPManager:
    """Manages multiple MCP servers."""

    def __init__(self):
        self.servers: dict[str, MCPServer] = {}

    def add_server(self, server: MCPServer):
        """Add an MCP server."""
        self.servers[server.name] = server

    async def get_all_tools(self) -> List[dict]:
        """Get tools from all servers."""
        tools = []
        for server in self.servers.values():
            tools.extend(await server.get_tools())
        return tools
```

**Effort**: 3-4 days
**Impact**: Enables MCP tool ecosystem integration

---

### 7. Observability Integration

**Recommended Implementation**:

```python
# observability.py - New file

from typing import Optional, Any, Dict
from contextlib import contextmanager
import time
import logging

logger = logging.getLogger(__name__)

class ObservabilityProvider:
    """Base class for observability providers."""

    def start_trace(self, name: str, metadata: Dict = None):
        pass

    def end_trace(self, trace_id: Any, status: str = "success"):
        pass

    def log_event(self, name: str, data: Dict):
        pass

class ConsoleObservability(ObservabilityProvider):
    """Simple console-based observability."""

    def start_trace(self, name: str, metadata: Dict = None):
        trace_id = time.time()
        logger.info(f"[TRACE START] {name} | {metadata}")
        return trace_id

    def end_trace(self, trace_id: Any, status: str = "success"):
        duration = time.time() - trace_id
        logger.info(f"[TRACE END] duration={duration:.2f}s status={status}")

    def log_event(self, name: str, data: Dict):
        logger.info(f"[EVENT] {name} | {data}")

class LangfuseObservability(ObservabilityProvider):
    """Langfuse integration."""

    def __init__(self, public_key: str, secret_key: str):
        from langfuse import Langfuse
        self.langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key
        )

    def start_trace(self, name: str, metadata: Dict = None):
        return self.langfuse.trace(name=name, metadata=metadata)

    def end_trace(self, trace_id: Any, status: str = "success"):
        trace_id.update(status=status)

# Global observability manager
_provider: ObservabilityProvider = ConsoleObservability()

def set_provider(provider: ObservabilityProvider):
    global _provider
    _provider = provider

@contextmanager
def trace(name: str, metadata: Dict = None):
    """Context manager for tracing."""
    trace_id = _provider.start_trace(name, metadata)
    try:
        yield trace_id
        _provider.end_trace(trace_id, "success")
    except Exception as e:
        _provider.end_trace(trace_id, f"error: {e}")
        raise
```

**Usage**:

```python
from observability import trace, set_provider, LangfuseObservability

# Optional: Set up Langfuse
set_provider(LangfuseObservability(
    public_key="pk-xxx",
    secret_key="sk-xxx"
))

# Use tracing
with trace("agent_request", {"model": "gpt-4o"}):
    response = agent.process("Hello!")
```

**Effort**: 2-3 days
**Impact**: Production monitoring and debugging

---

## P3: Lower Priority Improvements

### 8. FastAPI Integration

```python
# api.py - New file

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

app = FastAPI(title="indus-agents API")

class MessageRequest(BaseModel):
    message: str
    agent: str = "default"

class MessageResponse(BaseModel):
    response: str
    agent: str
    tokens_used: int

# Store agents
agents = {}

def register_agent(name: str, agent: 'Agent'):
    agents[name] = agent

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    agent = agents.get(request.agent)
    if not agent:
        raise HTTPException(404, f"Agent {request.agent} not found")

    response = await agent.process_async(request.message)

    return MessageResponse(
        response=response,
        agent=request.agent,
        tokens_used=agent.last_token_count
    )

@app.post("/chat/stream")
async def chat_stream(request: MessageRequest):
    agent = agents.get(request.agent)
    if not agent:
        raise HTTPException(404, f"Agent {request.agent} not found")

    async def generate():
        async for chunk in agent.process_stream(request.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

def run_api(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)
```

**Effort**: 2-3 days
**Impact**: HTTP API for integrations

---

### 9. Visualization

```python
# visualization.py - New file

from typing import Dict, List

def generate_agency_diagram(agency: 'Agency') -> str:
    """Generate Mermaid diagram of agency structure."""
    lines = ["graph TD"]

    # Add nodes
    for agent_name in agency.comm_manager.agents:
        label = agent_name
        if agent_name in [a.name for a in agency.entry_points]:
            lines.append(f'    {agent_name}["{label}"]:::entrypoint')
        else:
            lines.append(f'    {agent_name}["{label}"]')

    # Add edges
    for sender, receivers in agency.comm_manager.flows.items():
        for receiver in receivers:
            lines.append(f'    {sender} --> {receiver}')

    # Add styling
    lines.append('    classDef entrypoint fill:#f9f,stroke:#333,stroke-width:2px')

    return '\n'.join(lines)

def visualize_to_html(agency: 'Agency', output_file: str = "agency.html"):
    """Generate interactive HTML visualization."""
    mermaid_code = generate_agency_diagram(agency)

    html = f'''
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <h1>Agency Structure</h1>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
</body>
</html>
'''

    with open(output_file, 'w') as f:
        f.write(html)

    return output_file
```

**Effort**: 1-2 days
**Impact**: Better understanding of agency structure

---

## Implementation Roadmap

### Phase 1: Foundation (2-3 weeks)
- [ ] Async/streaming support
- [ ] Basic multi-agent communication
- [ ] Enhanced tool system with Pydantic

### Phase 2: Production Features (2-3 weeks)
- [ ] Callback-based persistence
- [ ] Accurate token counting
- [ ] Observability integration

### Phase 3: Ecosystem (2-3 weeks)
- [ ] MCP integration
- [ ] FastAPI endpoints
- [ ] Visualization

### Phase 4: Polish (1-2 weeks)
- [ ] Documentation updates
- [ ] Example applications
- [ ] Test coverage improvement

---

## Quick Wins (Can implement immediately)

1. **Add tiktoken for accurate token counting** (1 day)
2. **Update pricing data** (0.5 day)
3. **Add callback-based persistence** (1 day)
4. **Add basic observability logging** (0.5 day)
5. **Create agent template generator CLI command** (1 day)

---

## Conclusion

These enhancements would transform indus-agents from an educational framework into a production-capable system while maintaining its core philosophy of simplicity. The key priorities are:

1. **Async/Streaming** - Essential for modern AI applications
2. **Multi-Agent Communication** - Core differentiator for complex workflows
3. **Enhanced Tools** - Better validation and async support
4. **Flexible Persistence** - Production database support

By implementing these improvements incrementally, indus-agents can bridge the gap with agency-swarm while remaining more accessible and easier to understand.

---

## References

- agency-swarm source: `/home/user/indus-agents/agency-swarm/`
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
- tiktoken: https://github.com/openai/tiktoken
- Langfuse: https://langfuse.com
- MCP Protocol: https://modelcontextprotocol.io
