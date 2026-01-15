# Indus Agents Repository Guide

## What this repo is
- IndusAgents (package name `indusagi`) is a Python framework for building LLM-powered agents with tools, memory, and multi-agent orchestration.
- Primary code lives in `src/indusagi/`; many root-level scripts are demos or historical standalone versions.
- Static HTML demo sites are grouped under `example-html-website-create-by-agents/` and are unrelated to the Python package.
- Reference subprojects live under `useful-resource/` (e.g., `Agency-Code/`, `Mini-Agent/`, `claude-agent-sdk/`).

## Core package layout (`src/indusagi`)
- `agent.py`: main `Agent` implementation and `AgentConfig` (provider selection, tool loop, retries).
- `agency.py`: multi-agent "agency" coordination (Coder/Planner style workflows).
- `orchestrator.py`: routing system that selects specialized agents.
- `providers/`: provider adapters (`openai_provider.py`, `anthropic_provider.py`, `groq_provider.py`, `ollama_provider.py`, `google_provider.py`).
- `tools.py` + `tools/`: tool registry and built-in tools (bash, read, write, edit, glob, grep, todo_write, handoff).
- `memory.py`: conversation memory and message tracking.
- `cli.py`: Typer-based CLI commands.
- `tui/`: Textual-based terminal UI (optional dependency).
- `templates/`: scaffolding for new agents (`scaffolder.py`).
- `presets/`: preset configurations for improved agency demos.

## Key docs to understand behavior
- `PROJECT_ANALYSIS.md`: consolidated overview of architecture and features.
- `00-OVERVIEW.md`, `02-ARCHITECTURE.md`, `03-IMPLEMENTATION-GUIDE.md`, `04-TOOL-SYSTEM.md`: deeper design notes.
- `CLI_README.md`, `QUICK_REFERENCE.md`, `RUN_PLANNING_AGENT.md`: usage quick starts.

## CLI entry points and demos
- CLI entry point: `indusagi` (from `pyproject.toml`) or `python -m indusagi`.
- Main CLI commands (see `src/indusagi/cli.py`):
  - `indusagi run "prompt"`
  - `indusagi interactive`
  - `indusagi list-tools`
  - `indusagi test-connection`
  - `indusagi list-agents`
  - `indusagi create-agent --output ./agents`
  - `indusagi tui` (requires `textual`)
  - `indusagi agency-demo` (Coder <-> Planner demo)
- Provider demos:
  - `example_agency_improved_anthropic.py`
  - `example_agency_improved_groq.py`
  - `example_agency_improved_ollama.py`
  - Prompt files live in `example_agency_improved_*_prompts/`.

## Configuration and environment variables
- Provider API keys:
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `GROQ_API_KEY`
  - `OLLAMA_API_KEY` (Ollama Cloud)
  - `GEMINI_API_KEY` / `GOOGLE_API_KEY` (Google Gemini Developer API)
- Optional defaults used by `AgentConfig.from_env` (see `src/indusagi/agent.py`).
- Dependencies:
  - Core: `openai`, `anthropic`, `pydantic`, `typer`, `rich`, `httpx`, `python-dotenv`.
  - Optional TUI: `textual` (`pip install "indusagi[tui]"`).

## Tests
- `pytest` is configured in `pyproject.toml` with `pythonpath = ["src"]`.
- Tests live in `tests/` and include provider, tool, orchestrator, and integration checks.
- Common command: `pytest`.

## Non-core folders (static demos and assets)
- `example-html-website-create-by-agents/` contains static HTML/CSS/JS demo sites (not used by `indusagi` or tests).
- `useful-resource/` holds archived or reference subprojects (not part of the core package).
- Treat `node_modules/`, `dist/`, and similar directories as generated or external.

## Working conventions for agents
- Prefer editing `src/indusagi/*` for library changes; root-level `agent.py`, `tools.py`, etc are standalone/demo copies.
- Use prompts in `example_agency_improved_*_prompts/` when modifying the Coder/Planner demo.
- Keep new changes ASCII-only unless the file already uses Unicode.
