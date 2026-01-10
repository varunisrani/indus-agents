# Agent Isolation Architecture - Each Agent Separate

## Current Issue (Shared Resources)

```
Current Setup (All in ONE process):
┌─────────────────────────────────────────┐
│  Single Python Process                  │
│  ├── Shared GLM Connection              │
│  ├── Shared Tool Registry               │
│  ├── Shared Context                     │
│  │                                      │
│  ├── Agent: Coder                       │
│  ├── Agent: Planner                     │
│  └── Agent: Critic                      │
└─────────────────────────────────────────┘

Problem: All agents compete for same GLM connection
```

---

## Desired Solution (Separate Processes)

```
Desired Setup (Each agent SEPARATE):
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Python Process 1 │  │ Python Process 2 │  │ Python Process 3 │
│                  │  │                  │  │                  │
│ Agent: Coder     │  │ Agent: Planner   │  │ Agent: Critic    │
│ GLM Connect: 1   │  │ GLM Connect: 2   │  │ GLM Connect: 3   │
│ Tool Registry: 1 │  │ Tool Registry: 2 │  │ Tool Registry: 3 │
│ Tools: All       │  │ Tools: All       │  │ Tools: All       │
│                  │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
      ↑                    ↑                      ↑
      └────────────────────┴──────────────────────┘
              Communicate via Handoff Queue
              or Message Broker (RabbitMQ/Redis)
```

---

## What Needs to Change

### Option 1: Multiple Processes (Recommended)

**Advantages:**
- ✅ True isolation
- ✅ Each agent has own GLM connection
- ✅ Each agent has own tool registry
- ✅ Scales to many agents
- ✅ Fault isolation (one agent fails, others continue)

**Architecture:**
- Each agent runs in separate Python process
- Communication via message queue (RabbitMQ, Redis, or simple TCP)
- Coordinator orchestrates handoffs between agents

**Files to create:**
```
agents/
├── agent_coder.py      # Coder agent as separate process
├── agent_planner.py    # Planner agent as separate process
├── agent_critic.py     # Critic agent as separate process
├── message_queue.py    # Message broker (Redis/RabbitMQ wrapper)
├── coordinator.py      # Orchestrates handoffs between agents
└── shared_config.py    # Shared constants between processes
```

### Option 2: Thread Pool with Isolated Resources

**Advantages:**
- Simpler than separate processes
- Still isolates GLM connections
- Easier debugging

**Disadvantages:**
- ❌ GIL limits true parallelism
- ❌ Harder to scale

---

## Implementation Plan for Option 1 (Recommended)

### 1. Create Agent Base Class for Standalone Execution

```python
# agents/base_agent.py

class StandaloneAgent:
    def __init__(self, name, role, config, message_queue):
        self.name = name
        self.role = role
        self.config = config
        self.message_queue = message_queue
        
        # SEPARATE for each agent
        self.glm_connection = AnthropicProvider(config)
        self.tool_registry = ToolRegistry()
        self.context = ToolContext()
    
    def run(self):
        """Main event loop for this agent"""
        while True:
            # Wait for message from queue
            message = self.message_queue.receive(self.name)
            
            if message.type == "task":
                response = self.process(message.content)
                self.message_queue.send(message.reply_to, response)
            
            elif message.type == "handoff_request":
                self.message_queue.send(
                    message.target_agent,
                    message
                )
```

### 2. Create Separate Agent Scripts

**File: agents/agent_coder.py**
```python
if __name__ == "__main__":
    from base_agent import StandaloneAgent
    from message_queue import MessageQueue
    
    queue = MessageQueue("redis://localhost:6379")
    
    agent = StandaloneAgent(
        name="Coder",
        role="Code implementation",
        config=AgentConfig(...),
        message_queue=queue
    )
    
    agent.run()  # Run forever
```

**File: agents/agent_planner.py**
```python
if __name__ == "__main__":
    from base_agent import StandaloneAgent
    from message_queue import MessageQueue
    
    queue = MessageQueue("redis://localhost:6379")
    
    agent = StandaloneAgent(
        name="Planner",
        role="Strategic planning",
        config=AgentConfig(...),
        message_queue=queue
    )
    
    agent.run()  # Run forever
```

**File: agents/agent_critic.py**
```python
if __name__ == "__main__":
    from base_agent import StandaloneAgent
    from message_queue import MessageQueue
    
    queue = MessageQueue("redis://localhost:6379")
    
    agent = StandaloneAgent(
        name="Critic",
        role="Risk analysis",
        config=AgentConfig(...),
        message_queue=queue
    )
    
    agent.run()  # Run forever
```

### 3. Create Coordinator/Orchestrator

**File: coordinator.py**
```python
class AgentCoordinator:
    def __init__(self, queue, agents):
        self.queue = queue
        self.agents = agents  # ["Coder", "Planner", "Critic"]
    
    def start_user_request(self, user_input):
        """Send initial request to Coder"""
        self.queue.send("Coder", {
            "type": "task",
            "content": user_input,
            "reply_to": "coordinator"
        })
    
    def handle_handoff(self, handoff_request):
        """Route handoff between agents"""
        if handoff_request.mode == "parallel":
            # Fan out to multiple agents
            for agent_name in handoff_request.agent_names:
                self.queue.send(agent_name, handoff_request)
        else:
            # Single handoff
            self.queue.send(
                handoff_request.agent_name,
                handoff_request
            )
    
    def run(self):
        """Main orchestrator loop"""
        while True:
            message = self.queue.receive("coordinator")
            
            if message.type == "handoff_request":
                self.handle_handoff(message)
            elif message.type == "task_complete":
                return message.result
```

### 4. Run All Agents

```bash
# Terminal 1: Start Redis (or RabbitMQ)
redis-server

# Terminal 2: Start Coder agent
python agents/agent_coder.py

# Terminal 3: Start Planner agent
python agents/agent_planner.py

# Terminal 4: Start Critic agent
python agents/agent_critic.py

# Terminal 5: Run coordinator with user input
python coordinator.py
```

---

## Data Flow Diagram

```
User Input
    ↓
Coordinator (main.py)
    ├─→ send to Coder
    │
Coder Agent (agent_coder.py)
    ├─ Separate GLM Connection
    ├─ Separate Tool Registry
    ├─ Separate Context
    └─ Process message
        ↓
    Decides to handoff
        ↓
    send to Coordinator
        ↓
Coordinator
    ├─ mode == "parallel"
    │   ├─→ send to Planner
    │   └─→ send to Critic
    │
Planner Agent (agent_planner.py)      Critic Agent (agent_critic.py)
    ├─ Separate GLM Connection           ├─ Separate GLM Connection
    ├─ Separate Tool Registry            ├─ Separate Tool Registry
    ├─ Separate Context                  ├─ Separate Context
    └─ Process                           └─ Process
        ↓                                   ↓
    Results ─────┬─────────────────────────┘
                 ↓
           Coordinator
                 ├─ Aggregate results
                 └─ send to Coder
                    ↓
                 Coder Agent
                   ↓
                 Final output
```

---

## Message Queue Schema

### Using Redis (Simpler)

```python
# agents/message_queue.py using Redis

import redis

class MessageQueue:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    def send(self, target_agent, message):
        """Send message to agent's queue"""
        queue_key = f"agent:{target_agent}:messages"
        self.redis.lpush(queue_key, json.dumps(message))
    
    def receive(self, agent_name, timeout=0):
        """Receive message from agent's queue"""
        queue_key = f"agent:{agent_name}:messages"
        # Blocking pop
        message_json = self.redis.brpop(queue_key, timeout)
        return json.loads(message_json)
```

### Using RabbitMQ (Production)

```python
# agents/message_queue.py using RabbitMQ

import pika

class MessageQueue:
    def __init__(self, rabbitmq_url):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(rabbitmq_url)
        )
        self.channel = self.connection.channel()
    
    def send(self, target_agent, message):
        queue_name = f"agent_{target_agent}"
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message)
        )
    
    def receive(self, agent_name):
        queue_name = f"agent_{agent_name}"
        method, properties, body = self.channel.basic_get(queue_name)
        return json.loads(body)
```

---

## Summary: What Makes Each Agent Separate

| Aspect | Current | After Refactor |
|--------|---------|-----------------|
| **Process** | All in 1 | 3 separate Python processes |
| **GLM Connection** | 1 shared | 3 separate connections |
| **Tool Registry** | 1 shared | 3 separate registries |
| **Tool Context** | 1 shared | 3 separate contexts |
| **Communication** | Direct (same thread) | Message queue (Redis/RabbitMQ) |
| **Isolation** | ❌ None | ✅ Complete |
| **Scalability** | Limited | ✅ Easily add more agents |
| **Fault tolerance** | ❌ One fails, all fail | ✅ One fails, others continue |

---

## Would You Like Me To:

1. ✅ Implement Option 1 (Separate processes with Redis)?
2. Implement Option 2 (Thread pool with isolated resources)?
3. Keep current shared architecture but improve logging?

Let me know which approach you prefer!
