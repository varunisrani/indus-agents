# Agency Swarm Framework - Comprehensive Research Report

## Executive Summary

Agency Swarm is a production-ready, open-source framework (MIT license) for building multi-agent applications. Created by Arsenii Shatokhin (VRSEN), it leverages and extends the OpenAI Agents SDK, providing specialized features for creating, orchestrating, and managing collaborative swarms of AI agents. The framework is designed around real-world organizational structures, making it intuitive for both developers and users.

**Current Version**: v1.0 - Complete rewrite on OpenAI Agents SDK and Responses API
- Native async support
- Production-grade persistence
- Orchestrator-workers pattern
- Off legacy Assistants API

---

## 1. Core Concepts of Agency Swarm

### Philosophy
Agency Swarm simplifies AI automation by thinking in terms of real-world organizational structures. Instead of abstract workflows, you define agents with roles (CEO, Developer, Virtual Assistant) that mirror actual job functions.

### Key Principles

1. **Orchestrator-Workers Pattern**: A hierarchical yet flexible structure where agents can communicate based on defined flows
2. **Full Prompt Control**: Unlike other frameworks, Agency Swarm doesn't hard-code any prompts, parameters, or agents
3. **Production-First Design**: Built for reliability and real-world deployment scenarios
4. **Uniform Communication Flows**: Non-hierarchical, non-sequential - define any communication pattern you need
5. **Tool-Centric Architecture**: Agents are defined by their instructions and tools

### Framework Architecture

```
Agency (Orchestrator)
├── Agent 1 (e.g., CEO)
│   ├── Instructions
│   ├── Tools
│   └── Files
├── Agent 2 (e.g., Developer)
│   ├── Instructions
│   ├── Tools
│   └── Files
└── Communication Flows
    ├── Agent 1 → Agent 2
    └── Agent 2 → Agent 3
```

### Supported Models

**OpenAI (native)**:
- GPT-5 family
- GPT-4o
- Other OpenAI models

**Via LiteLLM (router)**:
- Anthropic (Claude)
- Google (Gemini)
- Grok (xAI)
- Azure OpenAI
- OpenRouter (gateway)

---

## 2. Agent Definition (Agent Class)

### Agent Class Parameters

```python
from agency_swarm import Agent, ModelSettings

agent = Agent(
    name="AgentName",                      # Required: Agent's name
    description="Agent description",       # Description for inter-agent communication
    instructions="path/to/instructions.md", # Instructions or file path
    model="gpt-5.2",                       # OpenAI model to use
    model_settings=ModelSettings(...),     # Model configuration from agents SDK
    tools=[tool1, tool2],                  # List of tools available to the agent
    files_folder="./files",                # Path for file management and vector stores
    tools_folder="./tools",                # Path to directory containing tool definitions
    schemas_folder="./schemas",            # Path for OpenAPI schemas
    output_type=MyOutputType,              # Type of agent's final output
    send_message_tool_class=CustomSendMessage, # Custom SendMessage tool class
    input_guardrails=[validator1],         # Input validation guardrails
    output_guardrails=[validator2],        # Output validation guardrails
    hooks=RunHooks(),                      # Custom execution hooks
)
```

### Agent Directory Structure

When creating agents, the recommended folder structure is:

```
AgentName/
├── AgentName.py          # Main agent class file
├── instructions.md       # Agent instructions (or .txt)
├── files/                # Files to upload to OpenAI
├── schemas/              # OpenAPI schemas to convert into tools
└── tools/                # Custom tools for this agent
    ├── __init__.py
    ├── tool1.py
    └── tool2.py
```

### Creating Agents with CLI

```bash
# Create agent template
agency-swarm create-agent-template \
    --name "AgentName" \
    --description "Agent Description" \
    --path "/path/to/directory"
```

### Agent Configuration Example

```python
from agency_swarm import Agent

ceo = Agent(
    name="CEO",
    description="Responsible for client communication, task planning and management.",
    instructions="./ceo_instructions.md",
    files_folder="./files",
    tools=[TaskPlanner, ClientCommunicator],
    model="gpt-5.2",
)

developer = Agent(
    name="Developer",
    description="Responsible for software development and coding tasks.",
    instructions="./dev_instructions.md",
    tools=[CodeWriter, CodeReviewer, GitTool],
    model="gpt-4o",
)
```

---

## 3. Agency Creation (Agency Class)

### Agency Class Overview

The Agency class orchestrates a collection of Agent instances based on a defined structure. It provides enhanced thread management, persistence hooks, and improved communication patterns between agents.

### Basic Agency Setup (Latest Syntax)

```python
from agency_swarm import Agency

agency = Agency(
    ceo,              # Entry point 1 - can interact with users
    developer,        # Entry point 2 - can interact with users
    communication_flows=[
        (ceo, developer),          # CEO can initiate with Developer
        (ceo, virtual_assistant),  # CEO can initiate with VA
        (developer, virtual_assistant), # Developer can initiate with VA
    ],
    shared_instructions='agency_manifesto.md',  # Shared instructions for all agents
)
```

### Alternative Syntax (Legacy)

```python
agency = Agency([
    ceo, developer,      # Top-level: can talk to users
    [ceo, developer],    # CEO can initiate with Developer
    [ceo, va],           # CEO can initiate with VA
    [developer, va]      # Developer can initiate with VA
])
```

### Communication Flow Operators

The `>` operator (or tuple syntax) defines allowed initiations:
- Left can initiate a chat with right
- Communication is directional
- Can be customized for any pattern

### Agency Configuration Options

```python
agency = Agency(
    # Entry point agents (can interact with users)
    ceo, developer,

    # Communication flows
    communication_flows=[
        (ceo, developer),
        (developer, qa_agent),
    ],

    # Optional configurations
    shared_instructions='manifesto.md',           # Shared across all agents
    send_message_tool_class=SendMessageQuick,    # Custom SendMessage class
    async_mode='threading',                       # Async execution mode

    # State management callbacks
    threads_callbacks={
        'load': load_threads_callback,
        'save': save_threads_callback
    },
    settings_callbacks={
        'load': load_settings_callback,
        'save': save_settings_callback
    }
)
```

### Running the Agency

```python
# Async mode (recommended)
response = await agency.get_response(
    message="Create a new feature for user authentication",
    thread_id="user_123_session_1",
    hooks_override=custom_hooks
)

# Sync mode (wrapper)
response = agency.get_completion_sync(
    message="Create a new feature",
    thread_id="user_123"
)

# Streaming mode
stream = agency.get_completion_stream(
    message="Analyze the codebase",
    event_handler=CustomEventHandler()
)

# Demo mode (for testing)
agency.demo_gradio()  # Launch Gradio interface
```

---

## 4. Tool Creation with BaseTool

### Method 1: @function_tool Decorator (Recommended)

```python
from agency_swarm import function_tool

@function_tool
def my_custom_tool(
    query: str,
    limit: int = 10
) -> str:
    """
    A brief description of what the custom tool does.

    Args:
        query: The search query to execute
        limit: Maximum number of results to return

    Returns:
        JSON string of search results
    """
    # Tool implementation
    results = perform_search(query, limit)
    return json.dumps(results)
```

### Method 2: Extending BaseTool (Compatible)

```python
from agency_swarm.tools import BaseTool
from pydantic import Field

class MyCustomTool(BaseTool):
    """
    A brief description of what the custom tool does.
    This docstring is used by the agent to determine when to use this tool.
    """
    query: str = Field(
        ...,
        description="The search query to execute"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return"
    )

    async def run(self):
        """
        The main functionality of the tool.
        This method should utilize the fields defined above.
        """
        results = await perform_search(self.query, self.limit)
        return json.dumps(results)
```

### BaseTool Advanced Features

#### Shared State

```python
class QueryDatabase(BaseTool):
    """Query database and store results in shared state."""

    query: str = Field(..., description="SQL query to execute")

    async def run(self):
        context = execute_query(self.query)
        # Store in shared state for other tools/agents
        self._shared_state.set('db_context', context)
        return f"Query executed. Results stored in shared state."

class AnalyzeData(BaseTool):
    """Analyze data from shared state."""

    async def run(self):
        # Retrieve from shared state
        context = self._shared_state.get('db_context')
        analysis = perform_analysis(context)
        return analysis
```

**Important Note**: Shared state is only available when tools are deployed together with agents. For separate API deployments, implement custom state management.

#### One Call at a Time

```python
class CriticalTool(BaseTool):
    """Ensures only one instance runs at a time."""

    one_call_at_a_time = True  # Class variable

    async def run(self):
        # Critical operation that shouldn't run concurrently
        pass
```

#### Accessing Caller Agent

```python
class ContextAwareTool(BaseTool):
    """Tool that knows which agent called it."""

    async def run(self):
        agent_name = self.caller_agent.name
        return f"Called by {agent_name}"
```

### Tool Factory Methods

#### From LangChain Tools

```python
from langchain.agents import load_tools
from agency_swarm.tools import ToolFactory

langchain_tools = load_tools(["arxiv", "human"])
tools = ToolFactory.from_langchain_tools(langchain_tools)
```

#### From OpenAPI Schema

```python
from agency_swarm.tools import ToolFactory
import requests

# From local file
with open("schemas/api_schema.json") as f:
    tools = ToolFactory.from_openapi_schema(f.read())

# From URL
schema = requests.get("https://api.example.com/openapi.json").json()
tools = ToolFactory.from_openapi_schema(schema)
```

### Tool Testing

Each tool file should include test cases:

```python
if __name__ == "__main__":
    # Test the tool
    tool = MyCustomTool(query="test", limit=5)
    result = asyncio.run(tool.run())
    print(result)
```

---

## 5. Agent Communication Patterns

### Default SendMessage Tool

The default SendMessage tool facilitates "direct, synchronous communication between specialized agents within your agency. When you send a message using this tool, you receive a response exclusively from the designated recipient agent."

### Communication Flow Definition

```python
agency = Agency(
    ceo,  # Entry point
    communication_flows=[
        (ceo, developer),     # CEO → Developer
        (ceo, va),            # CEO → Virtual Assistant
        (developer, va),      # Developer → VA
        (va, researcher),     # VA → Researcher
    ]
)
```

### Custom Communication Tools

#### Extending SendMessageBase

```python
from agency_swarm.tools.send_message import SendMessageBase

class SendMessageQuick(SendMessageBase):
    """Quick communication without full context."""

    message: str = Field(..., description="Quick message to send")

    async def run(self):
        # Custom communication logic
        response = await self._get_completion(
            message=self.message,
            agent=self.recipient_agent
        )
        return response
```

#### API-Based Communication

```python
import requests
from agency_swarm.tools.send_message import SendMessage

class SendMessageAPI(SendMessage):
    """Send messages via API for distributed deployment."""

    def run(self):
        response = requests.post(
            "https://your-api-endpoint.com/send-message",
            json={
                "message": self.message,
                "recipient": self.recipient,
                "sender": self.caller_agent.name
            }
        )
        return response.json()["message"]
```

### Pre-made SendMessage Classes

```python
from agency_swarm.tools.send_message import SendMessageQuick

agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
    send_message_tool_class=SendMessageQuick  # Apply to all communications
)
```

### Async Communication Modes

```python
agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
    async_mode='threading'  # Async communication between agents
)
```

Useful when you don't want to wait for a response from an agent that takes long to process.

### Communication Best Practices

1. **Design Clear Flows**: Define directional flows that mirror real-world communication patterns
2. **Minimize Cross-Talk**: Avoid creating overly connected graphs (mesh topology) unless necessary
3. **Use Hierarchy When Appropriate**: CEO → Manager → Worker patterns often work well
4. **Enable Bidirectional When Needed**: Create both (A, B) and (B, A) for two-way communication
5. **Consider Async for I/O**: Use async mode for agents with heavy I/O operations

---

## 6. Instructions System

### What are Instructions?

Instructions are the static prompts that define an agent's:
- Purpose and goals
- Behavior and personality
- Decision-making criteria
- What to consider when performing tasks

### Full Prompt Control

Agency Swarm provides "Full Control Over Prompts/Instructions: Maintain complete control over each agent's guiding prompts (instructions) for precise behavior customization."

Unlike other frameworks, Agency Swarm doesn't hard-code prompts or inject hidden system messages.

### Defining Instructions

#### Method 1: Inline String

```python
ceo = Agent(
    name="CEO",
    instructions="""
    You are the CEO of a software development agency.

    Your responsibilities:
    1. Communicate with clients to understand their needs
    2. Break down projects into manageable tasks
    3. Delegate work to the Developer and Virtual Assistant
    4. Ensure quality and timely delivery

    When a client requests a feature:
    - Ask clarifying questions
    - Create a project plan
    - Assign tasks to appropriate agents
    - Monitor progress and quality

    Always maintain professional communication and focus on delivering value.
    """
)
```

#### Method 2: File Path (Recommended)

```python
ceo = Agent(
    name="CEO",
    instructions="./ceo_instructions.md",  # or .txt
)
```

**ceo_instructions.md:**
```markdown
# CEO Agent Instructions

## Role
You are the CEO of a software development agency.

## Responsibilities
1. Client communication and relationship management
2. Project planning and task breakdown
3. Team coordination and delegation
4. Quality assurance and delivery

## Communication Style
- Professional and friendly
- Clear and concise
- Solution-oriented

## Decision Making
When receiving a client request:
1. Gather all necessary information
2. Assess technical feasibility
3. Create implementation plan
4. Delegate to appropriate team members

## Tools Available
- TaskPlanner: Break down projects into tasks
- SendMessage: Communicate with Developer and VA
- ClientCommunicator: Send updates to clients
```

### Shared Instructions

```python
agency = Agency(
    ceo, developer, va,
    communication_flows=[...],
    shared_instructions='agency_manifesto.md'  # Applies to ALL agents
)
```

**agency_manifesto.md:**
```markdown
# Agency Manifesto

## Our Mission
Deliver high-quality software solutions that exceed client expectations.

## Core Values
- Excellence in execution
- Clear communication
- Continuous improvement
- Client-first mentality

## Communication Guidelines
- Always confirm understanding before proceeding
- Provide regular status updates
- Escalate blockers immediately
- Document decisions and rationale
```

### Instructions in OpenAI Swarm Pattern

In the OpenAI Swarm pattern (which Agency Swarm builds upon):
- Agent instructions are directly converted into the system prompt
- Only the active agent's instructions are present at any given time
- Instructions can be a string or a function returning a string

### Dynamic Instructions (Advanced)

```python
def get_instructions(context_variables):
    user_tier = context_variables.get('user_tier', 'free')

    base = "You are a helpful assistant."

    if user_tier == 'premium':
        base += "\n\nProvide detailed, comprehensive responses with examples."
    else:
        base += "\n\nProvide concise, helpful responses."

    return base

agent = Agent(
    name="Assistant",
    instructions=get_instructions  # Function, not string
)
```

### Input/Output Validation

```python
from agency_swarm.validators import Validator

class SafetyValidator(Validator):
    """Ensure responses don't contain harmful content."""

    def validate(self, value):
        if contains_harmful_content(value):
            raise ValueError("Response contains prohibited content")
        return value

agent = Agent(
    name="Assistant",
    instructions="./instructions.md",
    input_guardrails=[InputSanitizer()],
    output_guardrails=[SafetyValidator(), QualityChecker()]
)
```

---

## 7. Thread and Message Management

### Async-First Architecture (v1.0)

Agency Swarm v1.0 introduced:
- Native async support
- Main methods expose async entry points (e.g., `await agency.get_response()`)
- Synchronous wrappers remain available
- Production-grade persistence
- Off the legacy Assistants API

### Thread Management Features

The Agency class provides:
- Enhanced thread management
- Persistence hooks
- Improved communication patterns between agents
- Automatic state management

### Thread Persistence

#### Callbacks for Loading/Saving Threads

```python
def load_threads_callback():
    """Load threads from database."""
    with open('threads.json', 'r') as f:
        return json.load(f)

def save_threads_callback(threads):
    """Save threads to database."""
    with open('threads.json', 'w') as f:
        json.dump(threads, f)

agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
    threads_callbacks={
        'load': load_threads_callback,
        'save': save_threads_callback
    }
)
```

#### Settings Persistence

```python
def load_settings_callback():
    """Load agent settings from database."""
    return db.get('agent_settings')

def save_settings_callback(settings):
    """Save agent settings to database."""
    db.set('agent_settings', settings)

agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
    settings_callbacks={
        'load': load_settings_callback,
        'save': save_settings_callback
    }
)
```

Settings is a list of dictionaries containing states of all agents. If any change is detected after initialization, settings will be updated and saved.

### Multi-User Thread Management

For applications with multiple users:

```python
# Store thread IDs per user
def get_or_create_thread(user_id):
    thread_id = db.get_thread_id(user_id)
    if not thread_id:
        thread_id = generate_thread_id()
        db.save_thread_id(user_id, thread_id)
    return thread_id

# Use thread_id in interactions
response = await agency.get_response(
    message="Help me with task X",
    thread_id=get_or_create_thread(user_id)
)
```

### State Management

Agency Swarm conveniently manages the state of your agents and threads, simplifying the assistant creation and management process on OpenAI's Assistants API.

Key features:
- Offloads conversation state management to OpenAI
- Maintains ongoing conversations without manual history management
- Handles message storage and truncation within token limits
- Efficient and seamless context handling

### Async Mode for Tools

```python
agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
    async_mode='tools_threading'  # Tools execute concurrently
)
```

With `tools_threading` mode:
- All tools execute concurrently in separate threads
- Significantly speeds up I/O bound tasks
- Useful for parallel API calls, database queries, etc.

### Known Issues and Workarounds

#### FastAPI Event Loop Conflict

When using Agency Swarm in FastAPI:

```python
# Problem: RuntimeError: This event loop is already running
# Solution: Use native async methods

@app.post("/chat")
async def chat(request: ChatRequest):
    # Don't use sync wrapper in async context
    # response = agency.get_completion_sync(...)  # ❌

    # Use async method directly
    response = await agency.get_response(  # ✅
        message=request.message,
        thread_id=request.thread_id
    )
    return response
```

### Message History Management

Agency Swarm automatically handles:
- Message history per thread
- Context window management
- Message truncation when limits are reached
- Conversation continuity across sessions

---

## 8. Key Features That Make Agency Swarm Powerful

### 1. Production-Ready Architecture

- **Built on OpenAI Agents SDK**: Leverages stable, production-grade foundation
- **Async-Native**: Designed for concurrent operations and scalability
- **Persistence**: Built-in state and thread management
- **Error Handling**: Robust error handling and recovery mechanisms

### 2. Full Developer Control

- **No Hidden Prompts**: Complete transparency and control over all prompts
- **No Hard-coded Agents**: Define everything from scratch
- **Customizable Communication**: Extend and modify communication patterns
- **Flexible Tool System**: Multiple ways to create and integrate tools

### 3. Uniform Communication Flows

Unlike other frameworks:
- Not hierarchical by default
- Not sequential by requirement
- Define any communication pattern
- Bidirectional, mesh, or custom topologies

### 4. Tool Ecosystem

```python
# Multiple tool creation methods
tools = [
    # 1. Custom tools with @function_tool
    my_function_tool,

    # 2. Extended BaseTool classes
    MyCustomTool(),

    # 3. LangChain tools
    *ToolFactory.from_langchain_tools(langchain_tools),

    # 4. OpenAPI schemas
    *ToolFactory.from_openapi_schema(api_schema),
]
```

### 5. Model Flexibility

```python
# OpenAI native
agent1 = Agent(name="A1", model="gpt-5.2")
agent2 = Agent(name="A2", model="gpt-4o")

# LiteLLM for other providers
agent3 = Agent(name="A3", model="claude-3-5-sonnet-20240620")
agent4 = Agent(name="A4", model="gemini-pro")
```

### 6. Event Hooks System

```python
from agency_swarm import RunHooks

class CustomHooks(RunHooks):
    def on_agent_start(self, ctx, agent):
        print(f"Agent {agent.name} starting")
        log_to_analytics("agent_start", agent.name)

    def on_agent_end(self, ctx, agent, output):
        print(f"Agent {agent.name} completed")
        log_to_analytics("agent_end", agent.name, output)

    def on_handoff(self, ctx, from_agent, to_agent):
        print(f"Handoff: {from_agent.name} → {to_agent.name}")

    def on_tool_start(self, ctx, agent, tool):
        print(f"{agent.name} using {tool.__class__.__name__}")

    def on_tool_end(self, ctx, agent, tool, result):
        print(f"Tool {tool.__class__.__name__} returned: {result}")

agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
)

response = await agency.get_response(
    message="Build feature X",
    hooks_override=CustomHooks()
)
```

### 7. Streaming Support

```python
from agency_swarm import AgencyEventHandler

class CustomEventHandler(AgencyEventHandler):
    def on_message_delta(self, delta):
        """Stream message chunks."""
        print(delta.content, end='', flush=True)

    def on_tool_call_created(self, tool_call):
        """Tool execution started."""
        print(f"\nUsing tool: {tool_call.type}")

    def on_tool_call_done(self, tool_call):
        """Tool execution completed."""
        print(f"\nTool {tool_call.type} completed")

stream = agency.get_completion_stream(
    message="Analyze the codebase",
    event_handler=CustomEventHandler()
)
```

The `AgencyEventHandler` has 2 additional properties over standard event handlers:
- `agent_name`: Name of the agent currently responding
- `recipient_agent_name`: Name of the recipient agent

### 8. Input/Output Validation

```python
from agency_swarm.validators import Validator

class InputSanitizer(Validator):
    """Remove sensitive data from inputs."""

    def validate(self, value):
        # Remove PII, credentials, etc.
        sanitized = remove_sensitive_data(value)
        return sanitized

class OutputQualityChecker(Validator):
    """Ensure output meets quality standards."""

    def validate(self, value):
        if not meets_quality_standards(value):
            raise ValueError("Output quality insufficient")
        return value

agent = Agent(
    name="SecureAgent",
    instructions="./instructions.md",
    input_guardrails=[InputSanitizer()],
    output_guardrails=[OutputQualityChecker()]
)
```

### 9. Shared State Management

```python
# Tool 1: Store data
class DataCollector(BaseTool):
    async def run(self):
        data = collect_data()
        self._shared_state.set('collected_data', data)
        return "Data collected"

# Tool 2: Use stored data
class DataAnalyzer(BaseTool):
    async def run(self):
        data = self._shared_state.get('collected_data')
        analysis = analyze(data)
        return analysis
```

### 10. Multiple Deployment Options

- **Monolithic**: All agents and tools together
- **Microservices**: Each agent as separate service
- **Hybrid**: Critical agents together, others separate
- **API-Based Tools**: Tools as separate endpoints

---

## 9. Code Generation Capabilities (Genesis)

### What is Genesis?

Genesis is Agency Swarm's AI-powered agency creation system. It's a meta-agency that creates other agencies for you.

### Genesis Agents

The Genesis Agency comprises four key agents:

1. **Genesis CEO**: Orchestrates the agency creation process
2. **Agent Creator**: Creates individual agents with instructions and tools
3. **OpenAPI Creator**: Converts API documentation into tools
4. **Browsing Agent**: Researches and gathers information for agent creation

### Using Genesis

#### Basic Usage

```bash
# Interactive mode
agency-swarm genesis

# With API key
agency-swarm genesis --openai_key "YOUR_API_KEY"
```

#### With Custom Models

```bash
# Using Claude
ANTHROPIC_API_KEY=<key> agency-swarm genesis --model claude-3-5-sonnet-20240620

# Using GPT-4
agency-swarm genesis --model gpt-4o
```

### What Genesis Creates

Genesis automatically generates:

1. **Agency Structure**: Complete organizational hierarchy
2. **Agent Definitions**: Each agent with:
   - Customized instructions
   - Appropriate tools
   - File configurations
3. **Communication Flows**: Optimal agent interaction patterns
4. **Tools**: Custom tools based on requirements
5. **Documentation**: README and usage guides

### Example Genesis Session

```
User: Create an agency for content marketing

Genesis CEO: I'll create a content marketing agency with the following agents:
- Marketing Manager (orchestrator)
- Content Writer (creates blog posts, articles)
- SEO Specialist (optimizes content)
- Social Media Manager (handles social distribution)
- Analytics Reporter (tracks performance)

[Genesis creates agents and tools]

Agency created successfully!
- Location: ./ContentMarketingAgency/
- Agents: 5
- Tools: 12
- Communication flows: Configured
```

### Genesis Workflow

1. **Requirement Analysis**: Understand what agency is needed
2. **Agent Design**: Determine required agents and their roles
3. **Tool Selection**: Identify needed tools
4. **Implementation**: Generate code for agents, tools, and agency
5. **Configuration**: Set up communication flows
6. **Documentation**: Create usage documentation

### Expanding Genesis Capabilities

Each agent or tool you add to Agency Swarm will automatically be available for import by the Genesis Swarm. This creates an exponentially larger and smarter system over time.

```python
# Your custom tool becomes available to Genesis
from agency_swarm.tools import BaseTool

class CustomMarketingTool(BaseTool):
    """Specialized tool for marketing automation."""
    # ... implementation

# Genesis can now use this in future agency creations
```

### Genesis Best Practices

1. **Clear Requirements**: Provide detailed, specific requirements
2. **Iterative Refinement**: Review and refine generated agencies
3. **Custom Tools**: Add domain-specific tools to your toolkit
4. **Test Generated Code**: Always test before production use
5. **Customize After Generation**: Use Genesis output as a starting point

### Limitations and Considerations

- Genesis creates a starting point, not production-ready code
- Review generated instructions for accuracy
- Test all generated tools thoroughly
- Customize communication flows for your specific needs
- May hit rate limits with complex agency creation

---

## 10. Best Practices for Building with Agency Swarm

### 1. Pre-Deployment Testing

**Test in Isolation:**
```python
# Test each tool
if __name__ == "__main__":
    tool = MyTool(param="test")
    result = asyncio.run(tool.run())
    assert result == expected_output

# Test each agent
agent = Agent(name="TestAgent", ...)
agency = Agency(agent)
agency.demo_gradio()  # Interactive testing
```

**Test in Combination:**
```python
# Test agent interactions
agency = Agency(
    agent1, agent2,
    communication_flows=[(agent1, agent2)]
)

# Run through scenarios
test_cases = [
    "Create a new feature",
    "Fix a bug",
    "Review code",
]

for test in test_cases:
    response = await agency.get_response(test)
    validate_response(response)
```

### 2. Production Deployment

#### Dynamic Thread Loading

```python
import sqlite3

def load_threads_callback():
    """Load threads from SQLite."""
    conn = sqlite3.connect('agency.db')
    cursor = conn.cursor()
    cursor.execute('SELECT threads FROM state WHERE id = 1')
    threads = json.loads(cursor.fetchone()[0])
    conn.close()
    return threads

def save_threads_callback(threads):
    """Save threads to SQLite."""
    conn = sqlite3.connect('agency.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE state SET threads = ? WHERE id = 1',
        (json.dumps(threads),)
    )
    conn.commit()
    conn.close()
```

#### Dynamic Settings Loading

```python
def load_settings_callback():
    """Load agent settings from database."""
    return db.query('SELECT settings FROM agency_config').first()

def save_settings_callback(settings):
    """Save agent settings when changed."""
    db.execute(
        'UPDATE agency_config SET settings = ?, updated_at = NOW()',
        settings
    )
```

#### Complete Deployment Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

# Initialize agency with persistence
agency = Agency(
    ceo, developer, qa,
    communication_flows=[
        (ceo, developer),
        (developer, qa),
    ],
    threads_callbacks={
        'load': load_threads_callback,
        'save': save_threads_callback
    },
    settings_callbacks={
        'load': load_settings_callback,
        'save': save_settings_callback
    }
)

class ChatRequest(BaseModel):
    message: str
    user_id: str
    thread_id: str | None = None

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get or create thread
        thread_id = request.thread_id or get_or_create_thread(request.user_id)

        # Get response
        response = await agency.get_response(
            message=request.message,
            thread_id=thread_id
        )

        return {
            "response": response,
            "thread_id": thread_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Deployment Architectures

#### Monolithic (Simplest)

```
┌─────────────────────────┐
│   Single Deployment     │
├─────────────────────────┤
│  Agency                 │
│  ├─ Agent 1 + Tools     │
│  ├─ Agent 2 + Tools     │
│  └─ Agent 3 + Tools     │
└─────────────────────────┘
```

**Pros**: Simple deployment, shared state works
**Cons**: Scales as one unit, single point of failure

#### Microservices (Most Scalable)

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Agent 1  │    │ Agent 2  │    │ Agent 3  │
│ Service  │◄──►│ Service  │◄──►│ Service  │
└──────────┘    └──────────┘    └──────────┘
     │               │               │
     └───────────────┼───────────────┘
                     ▼
            ┌─────────────────┐
            │  Shared State   │
            │  (Redis/DB)     │
            └─────────────────┘
```

**Pros**: Independent scaling, fault isolation
**Cons**: Complex, requires custom state management

#### Hybrid (Recommended)

```
┌─────────────────────┐    ┌──────────────┐
│  Core Agency        │    │ Tool Service │
│  ├─ Critical Agents │◄──►│ (API Tools)  │
│  └─ Orchestrator    │    └──────────────┘
└─────────────────────┘
```

**Pros**: Balance of simplicity and scalability
**Cons**: Requires planning to identify core vs. external

### 4. Agent Design Best Practices

#### Single Responsibility

```python
# Good: Focused agent
content_writer = Agent(
    name="ContentWriter",
    description="Writes blog posts and articles",
    instructions="./content_writer.md",
    tools=[ResearchTool, WritingTool, GrammarChecker]
)

# Bad: Overly broad agent
everything_agent = Agent(
    name="EverythingAgent",
    description="Does content, SEO, social media, analytics, and design",
    # This agent will be confused and ineffective
)
```

#### Clear Instructions

```python
# Good: Specific, actionable instructions
"""
You are a Code Reviewer specializing in Python.

For each code review:
1. Check for PEP 8 compliance
2. Identify potential bugs and edge cases
3. Suggest performance improvements
4. Verify proper error handling
5. Ensure adequate test coverage

Provide feedback in this format:
- Critical Issues: [list]
- Suggestions: [list]
- Positive Aspects: [list]
"""

# Bad: Vague instructions
"""
You review code and make it better.
"""
```

#### Appropriate Tool Selection

```python
# Give agents only the tools they need
ceo = Agent(
    name="CEO",
    tools=[
        TaskPlanner,           # ✅ Needs for planning
        SendMessage,           # ✅ Needs for delegation
        # CodeExecutor,        # ❌ CEO shouldn't execute code
        # DatabaseTool,        # ❌ CEO shouldn't access DB directly
    ]
)
```

### 5. Communication Flow Design

#### Hierarchical (Good for Clear Authority)

```python
communication_flows = [
    (ceo, project_manager),
    (project_manager, developer),
    (project_manager, designer),
    (developer, qa),
]
```

#### Collaborative (Good for Peer Interaction)

```python
communication_flows = [
    (researcher, analyst),
    (analyst, researcher),      # Bidirectional
    (analyst, writer),
    (writer, editor),
    (editor, writer),           # Bidirectional for revisions
]
```

#### Hub-and-Spoke (Good for Orchestration)

```python
communication_flows = [
    (orchestrator, specialist1),
    (specialist1, orchestrator),
    (orchestrator, specialist2),
    (specialist2, orchestrator),
    (orchestrator, specialist3),
    (specialist3, orchestrator),
]
```

### 6. Error Handling and Monitoring

```python
from agency_swarm import RunHooks

class ProductionHooks(RunHooks):
    def on_agent_start(self, ctx, agent):
        metrics.increment(f'agent.{agent.name}.starts')
        logger.info(f'Agent {agent.name} started', extra={'context': ctx})

    def on_agent_end(self, ctx, agent, output):
        metrics.increment(f'agent.{agent.name}.completions')
        logger.info(f'Agent {agent.name} completed', extra={'output': output})

    def on_tool_start(self, ctx, agent, tool):
        metrics.increment(f'tool.{tool.__class__.__name__}.calls')
        start_time = time.time()
        ctx['tool_start_time'] = start_time

    def on_tool_end(self, ctx, agent, tool, result):
        duration = time.time() - ctx.get('tool_start_time', time.time())
        metrics.timing(f'tool.{tool.__class__.__name__}.duration', duration)

        if 'error' in str(result).lower():
            logger.error(f'Tool {tool.__class__.__name__} error', extra={'result': result})

# Use in production
response = await agency.get_response(
    message=user_message,
    thread_id=thread_id,
    hooks_override=ProductionHooks()
)
```

### 7. Security Best Practices

```python
from agency_swarm.validators import Validator

class InputSanitizer(Validator):
    """Remove sensitive data and validate input."""

    def validate(self, value):
        # Remove PII
        value = remove_email_addresses(value)
        value = remove_phone_numbers(value)
        value = remove_credit_cards(value)

        # Validate length
        if len(value) > 10000:
            raise ValueError("Input too long")

        # Remove SQL injection attempts
        if contains_sql_injection(value):
            raise ValueError("Invalid input detected")

        return value

class OutputValidator(Validator):
    """Ensure output is safe."""

    def validate(self, value):
        # Don't leak API keys
        if contains_api_keys(value):
            raise ValueError("Output contains sensitive data")

        # Check for prompt injection results
        if contains_prompt_injection_markers(value):
            raise ValueError("Potential prompt injection detected")

        return value

secure_agent = Agent(
    name="SecureAgent",
    instructions="./instructions.md",
    input_guardrails=[InputSanitizer()],
    output_guardrails=[OutputValidator()],
)
```

### 8. Performance Optimization

#### Use Async Mode for I/O

```python
# Enable async tool execution
agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
    async_mode='tools_threading'  # Tools run concurrently
)
```

#### Optimize Tool Execution

```python
class OptimizedTool(BaseTool):
    """Tool with caching and batching."""

    _cache = {}

    async def run(self):
        # Check cache first
        cache_key = self.get_cache_key()
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Execute
        result = await self.execute()

        # Cache result
        self._cache[cache_key] = result
        return result
```

#### Limit Agent Scope

```python
# Instead of one agent doing everything
big_agent = Agent(
    name="SuperAgent",
    tools=[tool1, tool2, ..., tool50]  # ❌ Too many options
)

# Create focused agents
research_agent = Agent(
    name="Researcher",
    tools=[search_tool, scrape_tool]  # ✅ Focused
)

writing_agent = Agent(
    name="Writer",
    tools=[write_tool, grammar_tool]  # ✅ Focused
)
```

### 9. Testing Strategies

```python
import pytest

@pytest.fixture
async def test_agency():
    """Create agency for testing."""
    agent1 = Agent(name="A1", instructions="Test agent 1")
    agent2 = Agent(name="A2", instructions="Test agent 2")

    agency = Agency(
        agent1, agent2,
        communication_flows=[(agent1, agent2)]
    )
    return agency

@pytest.mark.asyncio
async def test_basic_interaction(test_agency):
    """Test basic agent interaction."""
    response = await test_agency.get_response(
        message="Test message",
        thread_id="test_thread"
    )

    assert response is not None
    assert len(response) > 0

@pytest.mark.asyncio
async def test_tool_execution(test_agency):
    """Test tool execution."""
    response = await test_agency.get_response(
        message="Execute tool X",
        thread_id="test_thread"
    )

    # Verify tool was called
    assert "tool result" in response.lower()
```

### 10. Documentation and Maintenance

```python
# Document your agency structure
"""
ContentMarketingAgency/
├── README.md                 # Overview and setup
├── ARCHITECTURE.md           # Agency design decisions
├── agents/
│   ├── manager/
│   │   ├── instructions.md  # Clear role definition
│   │   ├── tools/           # Tool documentation
│   │   └── tests/           # Agent-specific tests
│   ├── writer/
│   └── seo/
├── shared/
│   ├── manifesto.md         # Shared guidelines
│   └── tools/               # Shared tools
└── tests/
    ├── test_agency.py       # Integration tests
    └── test_flows.py        # Communication flow tests
"""

# Version your agents
ceo_v2 = Agent(
    name="CEO",
    description="CEO Agent v2.0 - Enhanced planning capabilities",
    instructions="./ceo_instructions_v2.md",
    # ...
)

# Log changes
CHANGELOG = """
## v2.0.0
- Added TaskPlanner tool
- Improved delegation logic
- Enhanced error handling

## v1.0.0
- Initial release
"""
```

### 11. Observability

```python
# Integration with observability tools
import sentry_sdk
from prometheus_client import Counter, Histogram

# Metrics
agent_calls = Counter('agent_calls_total', 'Total agent calls', ['agent_name'])
agent_duration = Histogram('agent_duration_seconds', 'Agent execution time', ['agent_name'])
tool_calls = Counter('tool_calls_total', 'Total tool calls', ['tool_name'])

class ObservabilityHooks(RunHooks):
    def on_agent_start(self, ctx, agent):
        agent_calls.labels(agent_name=agent.name).inc()
        ctx['start_time'] = time.time()

    def on_agent_end(self, ctx, agent, output):
        duration = time.time() - ctx.get('start_time', time.time())
        agent_duration.labels(agent_name=agent.name).observe(duration)

        # Send to Sentry if error
        if 'error' in str(output).lower():
            sentry_sdk.capture_message(
                f"Agent {agent.name} error",
                level='error',
                extras={'output': output}
            )

    def on_tool_start(self, ctx, agent, tool):
        tool_calls.labels(tool_name=tool.__class__.__name__).inc()
```

### 12. Gradual Rollout

```python
# Feature flags for gradual rollout
class FeatureFlags:
    USE_NEW_AGENT = os.getenv('USE_NEW_CEO_AGENT', 'false') == 'true'
    ENABLE_ASYNC_TOOLS = os.getenv('ENABLE_ASYNC_TOOLS', 'false') == 'true'

# Conditional agent selection
if FeatureFlags.USE_NEW_AGENT:
    ceo = new_ceo_v2
else:
    ceo = old_ceo_v1

# Conditional features
agency = Agency(
    ceo, developer,
    communication_flows=[(ceo, developer)],
    async_mode='tools_threading' if FeatureFlags.ENABLE_ASYNC_TOOLS else None
)
```

---

## Implementation Roadmap for indus-agents

Based on this research, here's a recommended approach for implementing Agency Swarm in the indus-agents project:

### Phase 1: Foundation (Week 1)
1. Install Agency Swarm: `pip install agency-swarm`
2. Create first agent (e.g., IndianMarketResearcher)
3. Implement basic tools for Indian market data
4. Test single-agent functionality

### Phase 2: Multi-Agent (Week 2)
1. Create 2-3 specialized agents
2. Define communication flows
3. Implement shared state for Indian market context
4. Test agent interactions

### Phase 3: Tool Ecosystem (Week 3)
1. Convert existing tools to BaseTool
2. Add India-specific API integrations (GST, GSTN, etc.)
3. Implement OpenAPI schema tools for government APIs
4. Create custom communication tools

### Phase 4: Production Ready (Week 4)
1. Implement persistence (threads & settings)
2. Add monitoring and hooks
3. Create deployment configuration
4. Comprehensive testing
5. Documentation

### Phase 5: Advanced Features (Ongoing)
1. Use Genesis to generate specialized agencies
2. Implement observability
3. Add input/output validation
4. Performance optimization
5. Security hardening

---

## Resources and References

### Official Documentation
- [Agency Swarm Official Site](https://agency-swarm.ai)
- [GitHub Repository](https://github.com/VRSEN/agency-swarm)
- [Installation Guide](https://agency-swarm.ai/welcome/installation)
- [Getting Started](https://agency-swarm.ai/welcome/getting-started/from-scratch)
- [API Reference](https://agency-swarm.ai/references/api)

### Guides and Tutorials
- [Agents Overview](https://agency-swarm.ai/core-framework/agents/overview)
- [Agencies Overview](https://agency-swarm.ai/core-framework/agencies/overview)
- [Communication Flows](https://agency-swarm.ai/core-framework/agencies/communication-flows)
- [State Management](https://agency-swarm.ai/core-framework/state-management)
- [Shared State](https://agency-swarm.ai/additional-features/shared-state)
- [Deployment to Production](https://agency-swarm.ai/additional-features/deployment-to-production)

### Community and Examples
- [Agency Swarm Lab](https://github.com/VRSEN/agency-swarm-lab) - Community contributions
- [Tutorial: Build AI Workforce in One Day](https://lunchpaillabs.com/blog/build-ai-workforce-one-day)
- [Agency Swarm Tutorial (Web Search Use Case)](https://github.com/john-adeojo/agency_swarm_tutorial)

### PyPI
- [agency-swarm on PyPI](https://pypi.org/project/agency-swarm/)

### Related Frameworks (for comparison)
- [OpenAI Swarm](https://github.com/openai/swarm) - Educational framework by OpenAI
- [Swarms by Kyegomez](https://github.com/kyegomez/swarms) - Alternative enterprise framework

---

## Conclusion

Agency Swarm is a powerful, production-ready framework for building multi-agent AI systems. Its key strengths are:

1. **Production Focus**: Built on stable OpenAI Agents SDK with async-first architecture
2. **Developer Control**: No hidden prompts or hard-coded behaviors
3. **Flexibility**: Uniform communication flows, multiple tool creation methods
4. **Scalability**: Multiple deployment architectures supported
5. **Rich Ecosystem**: Tool factory, Genesis code generation, hooks system
6. **Active Development**: Regular updates and community contributions

For the indus-agents project, Agency Swarm provides an excellent foundation for creating specialized AI agents for the Indian market. Its flexibility allows for India-specific customizations while maintaining production-grade reliability.

The framework's emphasis on organizational structures aligns well with creating domain-specific agents (e.g., GST Compliance Agent, Regional Marketing Agent, Legal Research Agent) that can collaborate effectively to serve Indian businesses.

---

**Report Generated**: 2026-01-02
**Framework Version**: Agency Swarm v1.0
**Research Scope**: Comprehensive analysis for indus-agents implementation
