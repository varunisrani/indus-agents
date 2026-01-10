# example_agency_improved.py - Updated to Latest Standards

## ✅ What Was Updated

The `example_agency_improved.py` script has been completely updated to match `example_agency_improved_anthropic.py` with all the latest features:

### 1. **Thread-Pool Support** 🧵
- Added `--thread-pool` CLI flag for isolated agent execution
- Added `--thread-timeout` CLI flag (default: 600 seconds)
- Each agent runs in a separate thread with its own GLM connection, tool registry, and context

### 2. **Critic Agent** 🔍
- Added `create_critic_agent()` function
- Full 3-agent system: Coder ↔ Planner ↔ Critic
- Critic performs risk analysis and QA reviews

### 3. **Parallel Handoffs** ⚡
- Coder can fan out to Planner + Critic simultaneously
- Results are automatically aggregated back to Coder
- Updated workflow explanation to show parallel execution

### 4. **Shared Preset Architecture** 🏗️
- Now uses `ImprovedAgencyOptions` and `create_improved_agency()` from shared preset
- Ensures consistency across all provider scripts (Anthropic, Groq, Ollama, OpenAI)
- Easier to maintain and update

### 5. **Unified Configuration** 🌡️
- All agents use `temperature=1` (consistent across providers)
- Planner: `max_tokens=16000` (comprehensive plans)
- Coder: `max_tokens=8000` (complex implementations)
- Critic: `max_tokens=8000` (detailed risk analysis)

### 6. **Prompt Files** 📄
- Created `example_agency_improved_prompts/` directory
- Copied all prompt files from Anthropic version:
  - `coder_instructions.md`
  - `planner_instructions.md`
  - `critic_instructions.md`

### 7. **Updated Display** 🎨
- Banner shows "OpenAI (GPT-4o)" provider
- Workflow explanation includes parallel execution (steps 5-6)
- Example prompts include parallel handoff examples
- Graceful shutdown with `agency.shutdown()` in finally block

### 8. **Argparse Integration** 🔧
- Added proper argument parsing for CLI flags
- Help message shows all available options
- Consistent with Anthropic and Groq scripts

---

## 🚀 How to Use

### Basic Usage (No Thread Pool)
```bash
python example_agency_improved.py
```

### With Thread Pool (Isolated Agents)
```bash
python example_agency_improved.py --thread-pool
```

### With Custom Timeout
```bash
python example_agency_improved.py --thread-pool --thread-timeout 300
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

Make sure you have `OPENAI_API_KEY` in your `.env` file:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Get your API key at: https://platform.openai.com/api-keys

---

## 📊 Comparison with Provider Scripts

All three provider scripts now have identical features:

| Feature | example_agency_improved.py | example_agency_improved_anthropic.py | example_agency_improved_groq.py |
|---------|---------------------------|-------------------------------------|--------------------------------|
| **Provider** | OpenAI | Anthropic (Z.AI) | Groq |
| **Model** | `gpt-4o` | `glm-4.7` | `llama-3.3-70b-versatile` |
| **Thread Pool** | ✅ | ✅ | ✅ |
| **Parallel Handoffs** | ✅ | ✅ | ✅ |
| **Critic Agent** | ✅ | ✅ | ✅ |
| **Temperature** | 1 (all agents) | 1 (all agents) | 1 (all agents) |
| **Shared Preset** | ✅ | ✅ | ✅ |
| **CLI Flags** | ✅ | ✅ | ✅ |

---

## 🎯 Key Benefits

### 1. **Consistency Across Providers**
- All scripts use the same architecture
- Same prompt files (copied to each provider directory)
- Same CLI interface
- Same features and capabilities

### 2. **Easy Provider Switching**
- Just change which script you run
- No code changes needed
- Same workflow and commands

### 3. **Thread Pool Isolation**
When you run with `--thread-pool`:
- Each agent gets its own GLM connection
- Separate tool registry per agent
- Cloned context for isolation
- No race conditions (file writes are serialized)

### 4. **Parallel Execution**
- Planner and Critic run simultaneously
- Faster workflow for complex tasks
- Results automatically merged by Coder

---

## 📁 File Structure

```
example_agency_improved.py                    ← Updated main script
example_agency_improved_prompts/              ← NEW directory
  ├── coder_instructions.md                   ← Copied from Anthropic
  ├── planner_instructions.md                 ← Copied from Anthropic
  └── critic_instructions.md                  ← Copied from Anthropic

example_agency_improved_anthropic.py          ← Reference script
example_agency_improved_anthropic_prompts/    ← Original prompts

example_agency_improved_groq.py               ← Groq version
example_agency_improved_groq_prompts/         ← Groq prompts

example_agency_improved_ollama.py             ← Ollama version (if exists)
example_agency_improved_ollama_prompts/       ← Ollama prompts (if exists)
```

---

## ✅ Testing

Run the script to verify everything works:
```bash
python example_agency_improved.py --thread-pool
```

Then try a parallel handoff:
```
You: Run Planner + Critic in parallel: Planner drafts a spec for a todo app; Critic lists top risks. Then implement.
```

You should see:
- "PARALLEL EXECUTION START" banner
- Both Planner and Critic logs running simultaneously
- "PARALLEL EXECUTION COMPLETE" with timing table
- Coder aggregating results and implementing

---

## 🔧 Troubleshooting

### Error: OPENAI_API_KEY not set
- Add `OPENAI_API_KEY=sk-your-key-here` to `.env` file
- Reload your shell or restart your terminal

### Timeout errors in thread pool mode
- Increase timeout: `--thread-timeout 1200` (20 minutes)
- OpenAI is usually fast, but complex tasks may take longer

### Parallel execution not showing
- Make sure you're using explicit parallel syntax in your prompt
- Example: "Run Planner + Critic in parallel" or "Handoff to Planner and Critic"

### Tool calling errors (like with Groq)
- OpenAI's GPT-4o has excellent tool-calling reliability
- If you see errors, check your API key and quota
- Anthropic (Claude) also has excellent tool-calling

---

## 🆚 When to Use Each Provider

### Use **OpenAI (example_agency_improved.py)** when:
- You need reliable tool calling
- You want GPT-4o's strong reasoning
- You have OpenAI credits

### Use **Anthropic (example_agency_improved_anthropic.py)** when:
- You need the highest quality output
- You want Claude's strong reasoning
- You have Anthropic API access (via Z.AI)

### Use **Groq (example_agency_improved_groq.py)** when:
- You need ultra-fast inference
- You're okay with occasional tool-calling issues
- You want to use the free tier

---

**Status**: ✅ `example_agency_improved.py` is now fully up-to-date and matches all provider scripts!

**Next Steps**:
1. Test with `python example_agency_improved.py --thread-pool`
2. Try parallel handoffs
3. Compare performance across providers
4. Choose your preferred provider based on needs
