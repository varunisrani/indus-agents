# Groq Script Updates - Now Matches Anthropic Script

## ✅ What Was Updated

The `example_agency_improved_groq.py` script has been updated to match all the latest features from `example_agency_improved_anthropic.py`:

### 1. **Thread-Pool Support** 🧵
- Added `--thread-pool` CLI flag
- Added `--thread-timeout` CLI flag (default: 600 seconds)
- Each agent now runs in an isolated thread with separate GLM connection, tool registry, and context

### 2. **Critic Agent** 🔍
- Added `create_critic_agent()` function
- Created `example_agency_improved_groq_prompts/critic_instructions.md`
- Critic now included in agency (Coder ↔ Planner ↔ Critic)

### 3. **Parallel Handoffs** ⚡
- Coder can now fan out to Planner + Critic in parallel
- Results are aggregated back to Coder
- Updated workflow explanation to show parallel execution

### 4. **Unified Temperature** 🌡️
- All agents now use `temperature=1` (consistent with Anthropic script)
- Planner: `max_tokens=16000` (increased from 8000)
- Coder: `max_tokens=8000`
- Critic: `max_tokens=8000`

### 5. **Shared Preset Architecture** 🏗️
- Now uses `ImprovedAgencyOptions` and `create_improved_agency()` from shared preset
- Ensures consistency across Anthropic, Groq, and Ollama presets
- Easier to maintain and update

### 6. **Updated Display** 🎨
- Workflow explanation now includes parallel execution (steps 5-6)
- Example prompts include parallel handoff examples
- Graceful shutdown with `agency.shutdown()` in finally block

---

## 🚀 How to Use

### Basic Usage (No Thread Pool)
```bash
python example_agency_improved_groq.py
```

### With Thread Pool (Isolated Agents)
```bash
python example_agency_improved_groq.py --thread-pool
```

### With Custom Timeout
```bash
python example_agency_improved_groq.py --thread-pool --thread-timeout 300
```

---

## 📋 Example Prompts

### Simple Tasks (Coder handles directly)
- "Create a hello world HTML page"
- "Create a simple calculator with HTML/CSS/JS"

### Complex Tasks (Coder → Planner → Coder)
- "Create plan.md for a todo app, then implement it"
- "Plan and build a weather dashboard with API integration"

### Parallel Handoffs (Coder fans out to multiple agents)
- "Run Planner + Critic in parallel for a spec and risk list"
- "Handoff in parallel: Planner creates plan.md for AI agent builder, Critic creates critic_report.md with risks"

---

## 🔑 Requirements

Make sure you have `GROQ_API_KEY` in your `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at: https://console.groq.com/keys

---

## ⚡ Groq vs Anthropic

| Feature | Groq | Anthropic |
|---------|------|-----------|
| **Model** | `llama-3.3-70b-versatile` | `glm-4.7` (via Z.AI) |
| **Speed** | ⚡ Ultra-fast (optimized inference) | 🐢 Slower but higher quality |
| **Cost** | 💰 Free tier available | 💰💰 Paid (via Anthropic API) |
| **Thread Pool** | ✅ Supported | ✅ Supported |
| **Parallel Handoffs** | ✅ Supported | ✅ Supported |
| **Critic Agent** | ✅ Included | ✅ Included |
| **Temperature** | 1 (all agents) | 1 (all agents) |

---

## 🎯 Key Benefits of Thread Pool Mode

When you run with `--thread-pool`:

1. **Isolated Resources**: Each agent gets its own GLM connection, tool registry, and context
2. **True Parallelism**: Planner and Critic run simultaneously (not sequentially)
3. **No Race Conditions**: File writes are serialized via write lock
4. **Better Debugging**: Each agent's logs are clearly separated
5. **Scalability**: Can handle more complex multi-agent workflows

---

## 📁 File Structure

```
example_agency_improved_groq.py          ← Updated main script
example_agency_improved_groq_prompts/
  ├── coder_instructions.md              ← Existing
  ├── planner_instructions.md            ← Existing
  └── critic_instructions.md             ← NEW (copied from Anthropic)
```

---

## ✅ Testing

Run the script to verify everything works:
```bash
python example_agency_improved_groq.py --thread-pool
```

Then try a parallel handoff:
```
You: Run Planner + Critic in parallel: Planner drafts a spec for a todo app; Critic lists top risks
```

You should see:
- "PARALLEL EXECUTION START" banner
- Both Planner and Critic logs running simultaneously
- "PARALLEL EXECUTION COMPLETE" with timing table
- Coder aggregating results and implementing

---

## 🔧 Troubleshooting

### Error: GROQ_API_KEY not set
- Add `GROQ_API_KEY=your_key_here` to `.env` file
- Reload your shell: `source .env` (Linux/Mac) or restart PowerShell (Windows)

### Timeout errors in thread pool mode
- Increase timeout: `--thread-timeout 1200` (20 minutes)
- Groq is usually very fast, so timeouts are rare

### Parallel execution not showing
- Make sure you're using explicit parallel syntax in your prompt
- Example: "Run Planner + Critic in parallel" or "Handoff to Planner and Critic"

---

**Status**: ✅ Groq script is now fully up-to-date with Anthropic script!
