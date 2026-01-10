# MiniMax-M2.1 Setup Guide

## 🎯 What is MiniMax-M2.1?

MiniMax-M2.1 is a powerful coding model that provides:
- **Polyglot programming mastery** - supports multiple languages
- **Precision code refactoring** - high-quality code generation
- **Anthropic-compatible API** - works with Claude Code and other tools

Reference: https://platform.minimax.io/docs/coding-plan/claude-code

---

## 🔧 Setup Instructions

### Step 1: Get MiniMax API Key

1. Visit [MiniMax Platform](https://platform.minimax.io/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy your API key

### Step 2: Configure Environment Variables

Add these to your `.env` file:

```bash
# MiniMax API Configuration
MINIMAX_API_KEY=your-minimax-api-key-here
MINIMAX_BASE_URL=https://api.minimax.io/anthropic

# For users in China, use:
# MINIMAX_BASE_URL=https://api.minimaxi.com/anthropic
```

**Important:** 
- The script will use `MINIMAX_API_KEY` first, then fall back to `ANTHROPIC_API_KEY` if not set
- The script automatically sets `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` environment variables internally
- This allows the Anthropic provider to connect to MiniMax's API

### Step 3: Run the Script

```bash
python example_agency_improved_anthropic-mini-max.py
```

Or with thread-pool mode:

```bash
python example_agency_improved_anthropic-mini-max.py --thread-pool
```

---

## 🆚 Why the 404 Error Happened

### The Problem:
```
[Agent Coder] Error in tool calling loop (turn 1): <html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

### The Cause:
1. **Wrong API Endpoint**: The script was using Z.AI's endpoint (`https://api.z.ai/v1`) which only supports `glm-4.7`
2. **Wrong Model**: Trying to use `MiniMax-M2.1` with Z.AI's API
3. **Result**: 404 Not Found because Z.AI doesn't have a MiniMax endpoint

### The Fix:
✅ Updated the script to use **MiniMax's Anthropic-compatible endpoint**:
- International: `https://api.minimax.io/anthropic`
- China: `https://api.minimaxi.com/anthropic`

✅ Each agent now gets the correct `api_key` and `base_url` in their `AgentConfig`

---

## 📊 Comparison: MiniMax vs Z.AI vs OpenAI

| Feature | MiniMax-M2.1 | Z.AI (GLM-4.7) | OpenAI (GPT-4o) |
|---------|--------------|----------------|-----------------|
| **API Endpoint** | `api.minimax.io/anthropic` | `api.z.ai/v1` | `api.openai.com/v1` |
| **Model Name** | `MiniMax-M2.1` | `glm-4.7` | `gpt-4o` |
| **Provider Type** | Anthropic-compatible | Anthropic-compatible | Native OpenAI |
| **Coding Focus** | ✅ Optimized for coding | ⚠️ General purpose | ✅ Strong coding |
| **Tool Calling** | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Speed** | 🚀 Fast | 🚀 Fast | 🐢 Moderate |
| **Cost** | 💰 Paid | 💰 Paid | 💰💰 Paid |

---

## 🔑 Key Configuration Changes

### Before (Broken):
```python
config = AgentConfig(
    model="MiniMax-M2.1",
    provider="anthropic",
    temperature=1,
    max_tokens=16000,
    # ❌ No api_key or base_url specified
    # ❌ Uses default Z.AI endpoint
)
```

### After (Fixed):
```python
# In main(), set environment variables before creating agents
api_key = os.getenv("MINIMAX_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/anthropic")

# Set these so AnthropicProvider uses MiniMax endpoint
os.environ["ANTHROPIC_API_KEY"] = api_key
os.environ["ANTHROPIC_BASE_URL"] = base_url

# Now create agents normally
config = AgentConfig(
    model="MiniMax-M2.1",
    provider="anthropic",  # ✅ Uses Anthropic provider with MiniMax endpoint
    temperature=1,
    max_tokens=16000,
)
```

---

## 📝 Example Usage

### Simple Task:
```
You: Create a hello world HTML page
```

### Complex Task with Planning:
```
You: Create plan.md for a todo app, then implement it
```

### Parallel Handoff:
```
You: Run Planner + Critic in parallel: Planner drafts a spec for a Samsung company website (multiple pages). Critic lists top risks. Then merge - critic should create report.md and planner generates plan.md. After that, Coder builds the Samsung company website using HTML, CSS, and JS (no React).
```

---

## 🐛 Troubleshooting

### Error: "MINIMAX_API_KEY not set"
**Solution:** Add `MINIMAX_API_KEY=your-key-here` to your `.env` file

### Error: "404 Not Found"
**Solution:** Make sure `MINIMAX_BASE_URL` is set correctly:
- International: `https://api.minimax.io/anthropic`
- China: `https://api.minimaxi.com/anthropic`

### Error: "Invalid API key"
**Solution:** 
1. Verify your API key is correct
2. Check if you're using the right endpoint (international vs China)
3. Make sure your account has API access enabled

### Tool calling errors
**Solution:** MiniMax-M2.1 has excellent tool-calling support. If you see errors:
1. Check your API quota
2. Verify the model name is exactly `MiniMax-M2.1` (case-sensitive)
3. Ensure you're using the latest version of the script

---

## 🎉 Features Supported

✅ **Thread-Pool Mode** - Isolated agent execution
✅ **Parallel Handoffs** - Fan-out to multiple agents
✅ **Critic Agent** - Risk analysis and QA
✅ **Dynamic Routing** - Intelligent task distribution
✅ **Tool Calling** - Full support for all tools

---

## 📚 Additional Resources

- [MiniMax Platform](https://platform.minimax.io/)
- [MiniMax Documentation](https://platform.minimax.io/docs)
- [Claude Code Integration](https://platform.minimax.io/docs/coding-plan/claude-code)
- [Cursor Integration](https://platform.minimax.io/docs/coding-plan/cursor)

---

**Status**: ✅ Script updated and ready to use with MiniMax-M2.1!

**Next Steps**:
1. Get your MiniMax API key
2. Add it to `.env`
3. Run `python example_agency_improved_anthropic-mini-max.py`
4. Start coding! 🚀
