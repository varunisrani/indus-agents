from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from indusagi import Agent, AgentConfig
from indusagi.tool_usage_logger import tool_logger
from indusagi.mcp import McpToolRegistry, McpToolRouter, ToolExecutorMux, load_mcp_json
from indusagi.tools import registry as core_registry


def _approval_gate(tool_name: str, arguments: dict) -> bool:
    """Simple approval gate for MCP tool calls."""
    if os.getenv("MCP_APPROVE_ALL") == "1":
        return True
    print("\nMCP tool call requested:")
    print(f"  tool: {tool_name}")
    print(f"  args: {arguments}")
    answer = input("Approve? [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def _build_agent() -> Agent:
    agent_config = AgentConfig.from_env()
    agent_config.provider = "anthropic"
    agent_config.model = "glm-4.7"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "example_mcp_prompts")
    prompt_file = os.path.join(prompt_dir, "mcp_instructions.md")

    return Agent(
        name="MCP-Test",
        role="MCP-enabled assistant",
        config=agent_config,
        prompt_file=prompt_file,
    )


def _resolve_config_path(path: str) -> str:
    if os.path.exists(path):
        return path
    if not os.path.isabs(path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.join(current_dir, path)
        if os.path.exists(candidate):
            return candidate
        basename_candidate = os.path.join(current_dir, os.path.basename(path))
        if os.path.exists(basename_candidate):
            return basename_candidate
    return path


def _load_tools(mux: ToolExecutorMux) -> list[dict]:
    try:
        return mux.schemas
    except Exception:
        return []


def _render_tools(mcp_registry: McpToolRegistry) -> list[dict]:
    tool_defs = mcp_registry.list_tool_defs(refresh=True)
    return [
        {
            "name": tool.name,
            "server": tool.server,
            "description": tool.description or "",
        }
        for tool in tool_defs
    ]


def _collect_tool_results(calls, max_chars: int = 6000) -> str:
    parts = []
    for call in calls:
        result = getattr(call, "result", "")
        if not result:
            continue
        snippet = result.strip()
        if not snippet:
            continue
        parts.append(f"[{call.tool_name}] {snippet}")
    combined = "\n\n".join(parts)
    if len(combined) > max_chars:
        combined = combined[:max_chars].rstrip() + "\n...[truncated]"
    return combined


def _summarize_from_tool_logs(agent: Agent, calls_before: int) -> str:
    new_calls = tool_logger.calls[calls_before:]
    tool_text = _collect_tool_results(new_calls)
    if not tool_text:
        return ""
    summary = agent.process(
        "Using the following tool outputs, write a concise, plain-text summary. "
        "Do not call tools again.\n\n"
        f"{tool_text}"
    )
    if summary and summary.strip() and summary.strip() != "I've completed the task.":
        return summary
    return f"Tool outputs (truncated):\n{tool_text}"


def _interactive_session(
    agent: Agent,
    mux: ToolExecutorMux,
    mcp_registry: McpToolRegistry,
    config_path: str,
    mcp_config,
) -> int:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich.theme import Theme
    from rich import box

    theme = Theme({
        "banner": "bold bright_cyan",
        "agent_name": "bold bright_blue",
        "user": "bold blue",
        "tool": "bold yellow",
        "success": "bold green",
        "warning": "yellow",
        "error": "bold red",
        "dim": "dim white",
        "box_border": "bright_cyan",
    })
    console = Console(theme=theme)

    servers = ", ".join(mcp_config.servers.keys()) if mcp_config.servers else "(none)"
    header = (
        f"[banner]MCP-Test[/banner]\n"
        f"[dim]Interactive MCP Agent[/dim]\n\n"
        f"[dim]Config:[/dim] {config_path}\n"
        f"[dim]Provider:[/dim] {agent.config.provider}    [dim]Model:[/dim] {agent.config.model}\n"
        f"[dim]Servers:[/dim] {servers}\n"
    )
    console.print()
    console.print(Panel(
        header,
        box=box.DOUBLE_EDGE,
        border_style="box_border",
        padding=(1, 2),
        width=80,
    ))

    commands_md = (
        "**Commands**\n"
        "- `/quit`, `/exit`: Exit\n"
        "- `/tools`: List MCP tools\n"
        "- `/servers`: Show MCP servers\n"
        "- `/refresh`: Refresh tool list\n"
        "- `/clear`: Clear conversation history\n"
        "- `/logs`: Show recent tool usage\n"
        "- `/stats`: Tool usage statistics\n"
    )
    console.print(Panel(Markdown(commands_md), border_style="dim", box=box.ROUNDED, width=80))
    console.print()

    tools_cache = _load_tools(mux)
    if not tools_cache:
        console.print("[warning]No tools loaded yet. Use /refresh if needed.[/warning]")
        console.print()

    while True:
        try:
            user_input = Prompt.ask("[user]You[/user]").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/quit", "/exit"]:
                console.print("[dim]Goodbye![/dim]")
                break

            if user_input.lower() == "/tools":
                try:
                    tool_rows = _render_tools(mcp_registry)
                except Exception as exc:
                    console.print(Panel(str(exc), title="[error]Error[/error]", border_style="error", box=box.ROUNDED))
                    continue
                table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
                table.add_column("Tool", style="tool")
                table.add_column("Server", style="agent_name")
                table.add_column("Description", style="white")
                for row in tool_rows:
                    table.add_row(row["name"], row["server"], row["description"])
                console.print(Panel(table, title="[banner]MCP Tools[/banner]", border_style="box_border"))
                continue

            if user_input.lower() == "/servers":
                table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
                table.add_column("Server", style="agent_name", width=16)
                table.add_column("Transport", style="white")
                table.add_column("Details", style="white")
                for name, server in mcp_config.servers.items():
                    if hasattr(server, "url"):
                        details = getattr(server, "url", "")
                        transport = "streamable-http"
                    else:
                        details = getattr(server, "command", "")
                        transport = "stdio"
                    table.add_row(name, transport, details)
                console.print(Panel(table, title="[banner]MCP Servers[/banner]", border_style="box_border"))
                continue

            if user_input.lower() == "/refresh":
                tools_cache = _load_tools(mux)
                console.print("[success]Tool list refreshed.[/success]")
                continue

            if user_input.lower() == "/clear":
                agent.clear_history()
                tool_logger.clear()
                console.print("[success]Conversation history cleared.[/success]")
                continue

            if user_input.lower() == "/logs":
                tool_logger.print_recent_calls(limit=10)
                continue

            if user_input.lower() == "/stats":
                tool_logger.print_statistics()
                continue

            if not tools_cache:
                tools_cache = _load_tools(mux)

            calls_before = len(tool_logger.calls)
            response = agent.process_with_tools(
                user_input,
                tools=tools_cache if tools_cache else None,
                tool_executor=mux if tools_cache else None,
            )
            if not response or response.strip() == "I've completed the task.":
                response = _summarize_from_tool_logs(agent, calls_before)
            if not response:
                response = "No response generated. Try /refresh or provide a more specific prompt."

            console.print()
            console.print(Panel(
                Markdown(response or "*No response generated*"),
                title=f"[agent_name]{agent.name}[/agent_name]",
                border_style="agent_name",
                box=box.ROUNDED,
                padding=(1, 2),
                width=80,
            ))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as exc:
            console.print(Panel(str(exc), title="[error]Error[/error]", border_style="error", box=box.ROUNDED))
            console.print()

    return 0


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Example IndusAGI agent that uses MCP tools."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="User prompt to send to the agent.",
    )
    parser.add_argument(
        "--config",
        default=os.getenv("MCP_CONFIG_PATH", "mcp.json"),
        help="Path to mcp.json configuration file.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run an interactive CLI session.",
    )
    args = parser.parse_args()

    config_path = _resolve_config_path(args.config)
    if not os.path.exists(config_path):
        print(f"Config not found: {config_path}")
        print("Create one from example_agents/mcp.example.json and rename to mcp.json.")
        return 1

    config = load_mcp_json(config_path)
    router = McpToolRouter(config, approval=_approval_gate)
    mcp_registry = McpToolRegistry(router)
    mux = ToolExecutorMux(core_registry, mcp_registry)
    agent = _build_agent()

    try:
        if args.interactive or not args.prompt:
            return _interactive_session(agent, mux, mcp_registry, config_path, config)

        tools_cache = _load_tools(mux)
        calls_before = len(tool_logger.calls)
        response = agent.process_with_tools(
            args.prompt,
            tools=tools_cache if tools_cache else None,
            tool_executor=mux if tools_cache else None,
        )
        if not response or response.strip() == "I've completed the task.":
            response = _summarize_from_tool_logs(agent, calls_before)
        if not response:
            response = "No response generated. Try a more specific prompt."
        print(response)
    finally:
        mux.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
