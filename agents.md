# Agents Quick Guide

Single Coder entry agent with dynamic handoff to Planner. Works across three provider presets: Anthropic (Z.AI GLM-4.7), Groq (Llama 3.3 70B), and Ollama Cloud (GLM-4.7).

## Architecture (shared)
- `Coder` receives every request and decides whether to handle directly or handoff.
- `Planner` produces detailed `plan.md` and returns to `Coder`.
- Bidirectional flow: `Coder ↔ Planner`; max handoffs default 100; max_turns defaults to provider-specific 1000 fallback when `None`.
- Tools registered globally via `indusagi.tools` (Bash, Read, Edit, Write, Glob, Grep, TodoWrite) plus `handoff_to_agent`.

## Provider presets
- Anthropic: model `glm-4.7`, env `ANTHROPIC_API_KEY`, prompts in `example_agency_improved_anthropic_prompts/`.
- Groq: model `llama-3.3-70b-versatile`, env `GROQ_API_KEY`, prompts in `example_agency_improved_groq_prompts/`.
- Ollama Cloud: model `glm-4.7`, env `OLLAMA_API_KEY`, prompts in `example_agency_improved_ollama_prompts/`.

## Setup
1) `pip install -r requirements.txt`
2) Add required API key(s) to `.env` (per provider above).
3) Optional: adjust model names or `reasoning_effort` in the factory functions.

## Run commands
- Anthropic: `python example_agency_improved_anthropic.py`
- Groq: `python example_agency_improved_groq.py`
- Ollama Cloud: `python example_agency_improved_ollama.py`

## Interactive demo controls
Each script launches `agency.terminal_demo(show_reasoning=False)` with commands like `/quit`, `/agents`, `/handoffs`, `/logs`, `/stats`.

## When Coder hands off to Planner
- Task explicitly requests planning or `plan.md`.
- Work spans multi-step architecture or large refactors.
- Complexity > simple CRUD or single-file edits.

## Deliverables produced
- Direct implementations for simple tasks.
- `plan.md` followed by implementation for complex tasks.

## Troubleshooting
- If you see an API key error, verify `.env` and reload shell.
- For token limits, lower `max_tokens` in `AgentConfig` of the corresponding factory.
- Use `agency.visualize()` output in the script to confirm communication flows.
