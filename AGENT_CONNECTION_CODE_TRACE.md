# Agent GLM Connection - Exact Code Trace

## How Each Agent Gets Its Own Separate GLM Connection

### Step 1: Create Agency Function Called

**File:** `example_agency_improved_anthropic.py`, Line 257

```python
agency = create_development_agency(
    model="glm-4.7",           # Same model for all
    reasoning_effort="medium",
    max_handoffs=100
)
```

---

### Step 2: Agency Preset Called

**File:** `src/indusagi/presets/improved_anthropic_agency.py`, Line 88-158

```python
def create_improved_agency(opts: ImprovedAgencyOptions = ImprovedAgencyOptions()) -> Agency:
    """Create the improved Coder <-> Planner (+ Critic) agency"""
    _register_default_tools()
```

---

### Step 3A: Create CODER Agent

**File:** `src/indusagi/presets/improved_anthropic_agency.py`, Line 98-108

```python
# ✅ AGENT 1
coder = Agent(
    name="Coder",
    role="Code implementation and execution",
    config=AgentConfig(
        model=opts.model,              # "glm-4.7"
        provider=opts.provider,        # "anthropic"
        temperature=0.5,               # ← Coder-specific!
        max_tokens=8000,              # ← Coder-specific!
    ),
    prompt_file=opts.coder_prompt_file,
)
```

**Execution Flow:**
```
1. Agent(name="Coder", ...) called
   ↓
2. Agent.__init__() called (src/indusagi/agent.py, line 217)
   ├── self.name = "Coder"
   ├── self.role = "Code implementation and execution"
   ├── self.config = AgentConfig(model="glm-4.7", provider="anthropic", temp=0.5, ...)
   │
   └── Line 249: self.provider = self._create_provider(provider_name)
       ↓
3. self._create_provider("anthropic") called (src/indusagi/agent.py, ~line 280)
   ↓
4. Returns: NEW AnthropicProvider instance #1
   └── This is Coder's independent GLM-4.7 connection!

Result: coder.provider = AnthropicProvider instance #1
```

---

### Step 3B: Create PLANNER Agent

**File:** `src/indusagi/presets/improved_anthropic_agency.py`, Line 111-121

```python
# ✅ AGENT 2
planner = Agent(
    name="Planner",
    role="Strategic planning and task breakdown specialist",
    config=AgentConfig(
        model=opts.model,              # "glm-4.7" (same model)
        provider=opts.provider,        # "anthropic" (same type)
        temperature=0.7,               # ← Different! Planner-specific!
        max_tokens=16000,             # ← Different! Planner-specific!
    ),
    prompt_file=opts.planner_prompt_file,
)
```

**Execution Flow:**
```
1. Agent(name="Planner", ...) called
   ↓
2. Agent.__init__() called (src/indusagi/agent.py, line 217)
   ├── self.name = "Planner"
   ├── self.role = "Strategic planning and task breakdown specialist"
   ├── self.config = AgentConfig(model="glm-4.7", provider="anthropic", temp=0.7, ...)
   │
   └── Line 249: self.provider = self._create_provider(provider_name)
       ↓
3. self._create_provider("anthropic") called again
   ↓
4. Returns: NEW AnthropicProvider instance #2  ← DIFFERENT from #1!
   └── This is Planner's independent GLM-4.7 connection!

Result: planner.provider = AnthropicProvider instance #2 (NOT #1!)
```

---

### Step 3C: Create CRITIC Agent

**File:** `src/indusagi/presets/improved_anthropic_agency.py`, Line 124-134

```python
# ✅ AGENT 3
critic = Agent(
    name="Critic",
    role="Risk and quality reviewer (edge cases, failure modes, test ideas)",
    config=AgentConfig(
        model=opts.model,              # "glm-4.7" (same model)
        provider=opts.provider,        # "anthropic" (same type)
        temperature=0.4,               # ← Different! Critic-specific!
        max_tokens=8000,              # ← Different! Critic-specific!
    ),
    prompt_file=opts.critic_prompt_file,
)
```

**Execution Flow:**
```
1. Agent(name="Critic", ...) called
   ↓
2. Agent.__init__() called (src/indusagi/agent.py, line 217)
   ├── self.name = "Critic"
   ├── self.role = "Risk and quality reviewer..."
   ├── self.config = AgentConfig(model="glm-4.7", provider="anthropic", temp=0.4, ...)
   │
   └── Line 249: self.provider = self._create_provider(provider_name)
       ↓
3. self._create_provider("anthropic") called again (third time)
   ↓
4. Returns: NEW AnthropicProvider instance #3  ← DIFFERENT from #1 and #2!
   └── This is Critic's independent GLM-4.7 connection!

Result: critic.provider = AnthropicProvider instance #3 (NOT #1 or #2!)
```

---

### Step 4: Create Agency with All 3 Agents

**File:** `src/indusagi/presets/improved_anthropic_agency.py`, Line 140-154

```python
agency = Agency(
    entry_agent=coder,
    agents=[coder, planner, critic],  # ← All 3 agents with their own providers
    communication_flows=[
        (coder, planner), (planner, coder),
        (coder, critic), (critic, coder),
        (planner, critic), (critic, planner),
    ],
    shared_instructions=None,
    name=opts.name,
    max_handoffs=opts.max_handoffs,
    max_turns=opts.max_turns,
    tools=tools,
    tool_executor=registry,
)
```

---

## 🔬 The Actual _create_provider() Method

**File:** `src/indusagi/agent.py`, Around line 280-300

```python
def _create_provider(self, provider_name: str) -> BaseProvider:
    """Create provider instance based on provider name."""
    if provider_name == "anthropic":
        # ✅ Returns NEW AnthropicProvider instance
        return AnthropicProvider(self.config)  # ← Each call returns NEW object!
    elif provider_name == "openai":
        return OpenAIProvider(self.config)
    elif provider_name == "groq":
        return GroqProvider(self.config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
```

**KEY INSIGHT:** 
- Called 3 times (once per agent)
- Each call creates NEW instance (different memory address)
- Each gets its own independent GLM connection

---

## 📊 Memory Layout After Creation

```
Python Memory:
────────────────────────────────────────────────────────────

Address: 0x7f123456  →  Coder Agent object
├── name: "Coder"
├── config: AgentConfig(temp=0.5, max_tokens=8000)
├── provider: AnthropicProvider(id=0x7f111111)
│   ├── api_key: "sk-..."
│   ├── base_url: "https://api.z.ai/..."
│   └── client: httpx.Client()  ← GLM Connection 1
└── ...

Address: 0x7f234567  →  Planner Agent object
├── name: "Planner"
├── config: AgentConfig(temp=0.7, max_tokens=16000)
├── provider: AnthropicProvider(id=0x7f222222)  ← DIFFERENT address!
│   ├── api_key: "sk-..."
│   ├── base_url: "https://api.z.ai/..."
│   └── client: httpx.Client()  ← GLM Connection 2
└── ...

Address: 0x7f345678  →  Critic Agent object
├── name: "Critic"
├── config: AgentConfig(temp=0.4, max_tokens=8000)
├── provider: AnthropicProvider(id=0x7f333333)  ← DIFFERENT address!
│   ├── api_key: "sk-..."
│   ├── base_url: "https://api.z.ai/..."
│   └── client: httpx.Client()  ← GLM Connection 3
└── ...
```

---

## 🔗 Network Connections

When agents process requests:

```
Coder Agent processes request
└── Uses coder.provider (instance #1)
    └── Calls api.z.ai with coder's config
        └── GLM-4.7 API Connection 1

    └─ When parallel handoff:
       ├── Planner Agent (in Thread 1)
       │  └── Uses planner.provider (instance #2)
       │     └── Calls api.z.ai with planner's config
       │         └── GLM-4.7 API Connection 2
       │
       └── Critic Agent (in Thread 2)
          └── Uses critic.provider (instance #3)
             └── Calls api.z.ai with critic's config
                 └── GLM-4.7 API Connection 3

Result: 3 SIMULTANEOUS API CALLS to GLM-4.7!
```

---

## 📈 Timeline of Creation

```
Time  Event                              Provider Count
──────────────────────────────────────────────────
 t0   create_improved_agency() called
 
 t1   coder = Agent(...)
      └── Line 249: _create_provider()
      └── AnthropicProvider instance #1 created     Providers: 1

 t2   planner = Agent(...)
      └── Line 249: _create_provider()
      └── AnthropicProvider instance #2 created     Providers: 2

 t3   critic = Agent(...)
      └── Line 249: _create_provider()
      └── AnthropicProvider instance #3 created     Providers: 3

 t4   Agency(agents=[coder, planner, critic])
      └── Returns agency with 3 agents              Providers: 3 ✅
```

---

## ✅ Proof Summary

### Each Agent Gets Own Provider:

1. **Coder Agent**
   - Line of creation: `coder = Agent(name="Coder", config=AgentConfig(..., temp=0.5, ...))`
   - Provider instance created: `AnthropicProvider instance #1`
   - Connection type: `GLM-4.7 API Connection #1`

2. **Planner Agent**
   - Line of creation: `planner = Agent(name="Planner", config=AgentConfig(..., temp=0.7, ...))`
   - Provider instance created: `AnthropicProvider instance #2`
   - Connection type: `GLM-4.7 API Connection #2`

3. **Critic Agent**
   - Line of creation: `critic = Agent(name="Critic", config=AgentConfig(..., temp=0.4, ...))`
   - Provider instance created: `AnthropicProvider instance #3`
   - Connection type: `GLM-4.7 API Connection #3`

### Total: 3 Separate GLM-4.7 Connections ✅

---

## 🎯 The Answer in Code

```python
# Inside create_improved_agency():

# Call 1: Create Coder with provider
coder = Agent(...)  # → self.provider = self._create_provider() → Instance #1

# Call 2: Create Planner with provider
planner = Agent(...)  # → self.provider = self._create_provider() → Instance #2 (DIFFERENT!)

# Call 3: Create Critic with provider
critic = Agent(...)  # → self.provider = self._create_provider() → Instance #3 (DIFFERENT!)

# Result:
# coder.provider != planner.provider != critic.provider
# id(coder.provider) != id(planner.provider) != id(critic.provider)
#
# Therefore: 3 separate GLM connections! ✅
```

---

## 📚 Key Files and Lines

| File | Lines | Description |
|------|-------|-------------|
| `example_agency_improved_anthropic.py` | 257 | Call `create_development_agency()` |
| `src/indusagi/presets/improved_anthropic_agency.py` | 88-158 | `create_improved_agency()` function |
| `src/indusagi/presets/improved_anthropic_agency.py` | 98-108 | Create Coder agent (provider #1) |
| `src/indusagi/presets/improved_anthropic_agency.py` | 111-121 | Create Planner agent (provider #2) |
| `src/indusagi/presets/improved_anthropic_agency.py` | 124-134 | Create Critic agent (provider #3) |
| `src/indusagi/agent.py` | 217-249 | Agent `__init__` and provider creation |
| `src/indusagi/agent.py` | ~280-300 | `_create_provider()` method |

**The magic happens on line 249 of `src/indusagi/agent.py`:**
```python
self.provider = self._create_provider(provider_name)
```

Each agent gets a new provider instance!

---

## 🏆 Final Conclusion

```
Question: How many GLM connections?
Code Trace: 3 (one per agent)
Proof: id(agent1.provider) ≠ id(agent2.provider) ≠ id(agent3.provider)
Result: ✅ EACH AGENT HAS ITS OWN SEPARATE GLM-4.7 CONNECTION!
```
