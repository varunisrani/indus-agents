# Mistral Provider Guide (IndusAGI)

This guide explains how to enable and use the Mistral provider in IndusAGI.

## 1) Configure credentials

```bash
export MISTRAL_API_KEY="your-api-key"
export MISTRAL_MODEL="mistral-large-latest"
export LLM_PROVIDER="mistral"
```

Optional (custom endpoint):

```bash
export MISTRAL_BASE_URL="https://api.mistral.ai/v1"
```

## 2) Use in code

```python
from indusagi import Agent, AgentConfig

agent = Agent(
    name="Helper",
    role="Helpful assistant",
    config=AgentConfig(
        model="mistral-large-latest",
        provider="mistral",
        temperature=0.7,
    ),
)

print(agent.process("Summarize this repo in 3 bullets."))
```

## 3) Tool calling support

IndusAGI keeps tool schemas in OpenAI format. The Mistral provider passes these
directly to Mistral’s OpenAI-compatible API, and normalizes tool calls into
IndusAGI’s standard `ToolCall` format.

## 4) Optional: Mistral web search tools

Mistral offers built-in web search tools for agents. You can opt-in by adding
the tool to your `tools` list when calling `process_with_tools`:

```python
tools = [
    {"type": "web_search"},
]

response = agent.process_with_tools(
    "Find today’s top AI headlines.",
    tools=tools,
)
```

Use `"web_search_premium"` for the premium pipeline. This is intentionally
opt-in so you can control latency and cost.
