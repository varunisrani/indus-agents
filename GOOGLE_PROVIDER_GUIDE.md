# Google Gemini Provider Guide (IndusAGI)

This guide explains how to enable and use the Google Gemini provider in IndusAGI.

## 1) Install dependencies

```bash
pip install google-genai
```

## 2) Configure credentials

### Option A: Gemini Developer API (AI Studio)

```bash
export GEMINI_API_KEY="your-api-key"
export GOOGLE_MODEL="gemini-2.0-flash"
export LLM_PROVIDER="google"
```

### Option B: Vertex AI Gemini (recommended for production)

```bash
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_MODEL="gemini-2.0-flash"
export LLM_PROVIDER="google"
```

## 3) Use in code

```python
from indusagi import Agent, AgentConfig

agent = Agent(
    name="Helper",
    role="Helpful assistant",
    config=AgentConfig(
        model="gemini-2.0-flash",
        provider="google",
        temperature=0.7,
    ),
)

print(agent.process("Summarize this repo in 3 bullets."))
```

## 4) Tool calling support

IndusAGI keeps its internal tool schemas in OpenAI format. The Google provider
automatically converts these tool schemas into Gemini function declarations and
normalizes tool calls back into IndusAGI’s standard `ToolCall` format.

## 5) Optional: Google Search grounding

If you want real-time web grounding, Gemini supports a built-in Google Search tool.
To add it, extend the `GoogleProvider` call parameters with the `googleSearch` tool:

```python
# in src/indusagi/providers/google_provider.py
api_params["tools"] = [{"googleSearch": {}}]
```

This is intentionally opt-in so you can control latency and cost.
