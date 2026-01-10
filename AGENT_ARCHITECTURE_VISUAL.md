# Agent Architecture - Visual Flow Diagram

## How Each Agent Gets Its Own GLM Connection

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  example_agency_improved_anthropic.py           │
│                                                                 │
│  create_development_agency(                                     │
│      model="glm-4.7",        ← Same model for all              │
│      provider="anthropic"    ← Same provider type               │
│  )                                                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  src/indusagi/presets/improved_anthropic_agency.py              │
│                                                                 │
│  def create_improved_agency(opts):                              │
│                                                                 │
│      _register_default_tools()                                  │
│                                                                 │
│      # Create 3 separate agents                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼

    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Agent        │ │ Agent        │ │ Agent        │
    │ (name="Code" │ │ (name="Plan" │ │ (name="Crit" │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼

    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ AgentConfig  │ │ AgentConfig  │ │ AgentConfig  │
    │ temp: 0.5    │ │ temp: 0.7    │ │ temp: 0.4    │
    │ max_tok: 8k  │ │ max_tok: 16k │ │ max_tok: 8k  │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼

    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Agent.__init │ │ Agent.__init │ │ Agent.__init │
    │ line 249:    │ │ line 249:    │ │ line 249:    │
    │ _create_     │ │ _create_     │ │ _create_     │
    │ provider()   │ │ provider()   │ │ provider()   │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼
    
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Anthropic    │ │ Anthropic    │ │ Anthropic    │
    │ Provider     │ │ Provider     │ │ Provider     │
    │ Instance #1  │ │ Instance #2  │ │ Instance #3  │
    │              │ │              │ │              │
    │ (NEW object) │ │ (NEW object) │ │ (NEW object) │
    │ id=123...    │ │ id=456...    │ │ id=789...    │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼

    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   GLM-4.7    │ │   GLM-4.7    │ │   GLM-4.7    │
    │ API Client 1 │ │ API Client 2 │ │ API Client 3 │
    │ (SEPARATE)   │ │ (SEPARATE)   │ │ (SEPARATE)   │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Z.AI Anthropic API    │
                │ (backend service)     │
                │                       │
                │ Can receive 3         │
                │ simultaneous calls    │
                └───────────────────────┘
```

---

## Sequential vs Parallel Execution

### Sequential (Normal Flow)

```
User Request
    │
    ▼
Coder Agent ─[query GLM]─ wait for response
                            │
                            └─► Planner Agent ─[query GLM]─ wait for response
                                                                │
                                                                └─► Coder Agent ─[query GLM]─ Done

Timeline:
─────────────────────────────────────────────────────────────────────────────►
[Coder query][Planner query][Coder query]
     t1         t2           t3
```

### Parallel (New Feature)

```
User Request
    │
    ▼
Coder Agent ─[query GLM]
    │
    ├─ fork ThreadPoolExecutor
    │
    ├─ Thread 1: Planner ─[query GLM with Planner's provider]
    │                    ├─ temp: 0.7
    │                    ├─ max_tokens: 16000
    │                    └─ Independent connection
    │
    └─ Thread 2: Critic ─[query GLM with Critic's provider]
                         ├─ temp: 0.4
                         ├─ max_tokens: 8000
                         └─ Independent connection

Timeline:
─────────────────────────────────────────────────────────────────────────────►
[Coder query]
├─ [Planner query parallel]
└─ [Critic query parallel]
     (simultaneous)
```

---

## Agent Configuration Comparison

```
┌──────────────┬──────────────────┬──────────────────┬──────────────────┐
│  Property    │  Coder Agent     │  Planner Agent   │  Critic Agent    │
├──────────────┼──────────────────┼──────────────────┼──────────────────┤
│  Name        │  "Coder"         │  "Planner"       │  "Critic"        │
│  Role        │  Code impl.      │  Planning        │  QA & Risk       │
│  Model       │  glm-4.7         │  glm-4.7         │  glm-4.7         │
│  Provider    │  anthropic       │  anthropic       │  anthropic       │
│              │                  │                  │                  │
│  Temperature │  0.5 ← PRECISE   │  0.7 ← BALANCED  │  0.4 ← CAREFUL   │
│  Max Tokens  │  8,000           │  16,000          │  8,000           │
│              │                  │                  │                  │
│  Instance ID │  id(prov)=123    │  id(prov)=456    │  id(prov)=789    │
│  Connection  │  SEPARATE #1     │  SEPARATE #2     │  SEPARATE #3     │
└──────────────┴──────────────────┴──────────────────┴──────────────────┘
```

---

## Code Creation Path

```
File: src/indusagi/presets/improved_anthropic_agency.py, Line 98-134

def create_improved_agency(opts):
    
    # ═══════════════════════════════════════════════════════════════════
    # AGENT 1: CODER
    # ═══════════════════════════════════════════════════════════════════
    coder = Agent(
        name="Coder",
        role="Code implementation and execution",
        config=AgentConfig(
            model=opts.model,              # "glm-4.7"
            provider=opts.provider,        # "anthropic"
            temperature=0.5,               # ← Coder-specific!
            max_tokens=8000,              # ← Coder-specific!
        ),
    )
    # Execution: Agent.__init__() → line 249 → self.provider = self._create_provider("anthropic")
    #            → returns AnthropicProvider instance #1
    
    
    # ═══════════════════════════════════════════════════════════════════
    # AGENT 2: PLANNER
    # ═══════════════════════════════════════════════════════════════════
    planner = Agent(
        name="Planner",
        role="Strategic planning and task breakdown specialist",
        config=AgentConfig(
            model=opts.model,              # "glm-4.7" (same model)
            provider=opts.provider,        # "anthropic" (same type)
            temperature=0.7,               # ← Different! (Planner-specific)
            max_tokens=16000,             # ← Different! (Planner-specific)
        ),
    )
    # Execution: Agent.__init__() → line 249 → self.provider = self._create_provider("anthropic")
    #            → returns AnthropicProvider instance #2 (NEW object!)
    
    
    # ═══════════════════════════════════════════════════════════════════
    # AGENT 3: CRITIC
    # ═══════════════════════════════════════════════════════════════════
    critic = Agent(
        name="Critic",
        role="Risk and quality reviewer (edge cases, failure modes, test ideas)",
        config=AgentConfig(
            model=opts.model,              # "glm-4.7" (same model)
            provider=opts.provider,        # "anthropic" (same type)
            temperature=0.4,               # ← Different! (Critic-specific)
            max_tokens=8000,              # ← Different! (Critic-specific)
        ),
    )
    # Execution: Agent.__init__() → line 249 → self.provider = self._create_provider("anthropic")
    #            → returns AnthropicProvider instance #3 (NEW object!)
    
    
    # ═══════════════════════════════════════════════════════════════════
    # RESULT: 3 Agents with 3 Separate GLM Connections
    # ═══════════════════════════════════════════════════════════════════
    agency = Agency(
        entry_agent=coder,
        agents=[coder, planner, critic],  # ← 3 independent agents
        communication_flows=[...],
        tools=tools,
        tool_executor=registry,
    )
    return agency
```

---

## Memory Usage Illustration

```
RAM Address Space:
────────────────────────────────────────────────────────────

Coder Agent Object
├── self.name = "Coder"
├── self.config = AgentConfig(..., temp=0.5, ...)
├── self.provider = AnthropicProvider instance #1
│   ├── api_key = "sk-..."
│   ├── base_url = "https://api.z.ai/..."
│   └── client = httpx.Client()  ← Connection 1
│
├── self.messages = [...]
└── ...

Planner Agent Object
├── self.name = "Planner"
├── self.config = AgentConfig(..., temp=0.7, ...)
├── self.provider = AnthropicProvider instance #2  ← DIFFERENT object!
│   ├── api_key = "sk-..."
│   ├── base_url = "https://api.z.ai/..."
│   └── client = httpx.Client()  ← Connection 2
│
├── self.messages = [...]
└── ...

Critic Agent Object
├── self.name = "Critic"
├── self.config = AgentConfig(..., temp=0.4, ...)
├── self.provider = AnthropicProvider instance #3  ← DIFFERENT object!
│   ├── api_key = "sk-..."
│   ├── base_url = "https://api.z.ai/..."
│   └── client = httpx.Client()  ← Connection 3
│
├── self.messages = [...]
└── ...

                    ↓ ↓ ↓ (3 separate connections)
                    
                Z.AI Backend
                (handles all 3)
```

---

## Network Connections

```
                            Z.AI API Server

                          (Anthropic compatible)
                                   ▲ ▲ ▲
                                   │ │ │
                ┌──────────────────┘ │ └──────────────────┐
                │                    │                    │
                │                    │                    │
        Connection 1         Connection 2         Connection 3
        (Coder: 0.5)         (Planner: 0.7)       (Critic: 0.4)
                │                    │                    │
                │                    │                    │
        ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
        │ Coder Agent   │    │ Planner Agent │    │ Critic Agent  │
        │ Provider #1   │    │ Provider #2   │    │ Provider #3   │
        └───────────────┘    └───────────────┘    └───────────────┘


During parallel execution:
                    Query 1 ──►
                    Query 2 ──► Z.AI Backend processes all 3 in parallel
                    Query 3 ──►
```

---

## Summary Table

| # | Agent | Temp | Tokens | Provider Instance | Connection | Status |
|---|-------|------|--------|-------------------|------------|--------|
| 1 | Coder | 0.5 | 8k | AnthropicProvider #1 | GLM-4.7 #1 | ✅ Active |
| 2 | Planner | 0.7 | 16k | AnthropicProvider #2 | GLM-4.7 #2 | ✅ Active |
| 3 | Critic | 0.4 | 8k | AnthropicProvider #3 | GLM-4.7 #3 | ✅ Active |

**Result:** 3 agents × 1 connection each = **3 independent GLM-4.7 connections**

---

## Key Code Locations

| File | Line | What Happens |
|------|------|--------------|
| `example_agency_improved_anthropic.py` | 257 | `create_development_agency()` called |
| `src/indusagi/presets/improved_anthropic_agency.py` | 88 | `create_improved_agency()` function |
| `src/indusagi/presets/improved_anthropic_agency.py` | 98 | Coder Agent created |
| `src/indusagi/presets/improved_anthropic_agency.py` | 111 | Planner Agent created |
| `src/indusagi/presets/improved_anthropic_agency.py` | 124 | Critic Agent created |
| `src/indusagi/agent.py` | 217 | Agent `__init__` called |
| `src/indusagi/agent.py` | 249 | **`self.provider = self._create_provider()`** ← Creates separate instance! |
| `src/indusagi/agent.py` | ~280 | `_create_provider()` returns new AnthropicProvider |

---

## Final Answer

```
Question: Does each agent have its own GLM connection or do all agents share one?

Answer: ✅ EACH AGENT HAS ITS OWN SEPARATE GLM CONNECTION!

Evidence:
• 3 different Agent objects created
• 3 different AgentConfig objects with different settings
• 3 different AnthropicProvider instances created
• 3 different GLM-4.7 API connections
• Can run in parallel without blocking

Architecture:
Coder (temp 0.5) → GLM Connection #1
Planner (temp 0.7) → GLM Connection #2
Critic (temp 0.4) → GLM Connection #3

This is the CORRECT design! ✅
```
