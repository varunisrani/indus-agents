from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Literal


@dataclass(frozen=True)
class StdioMcpServer:
    """Configuration for a stdio MCP server (local subprocess)."""

    transport: Literal["stdio"] = "stdio"
    command: str = ""
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    cwd: Optional[str] = None


@dataclass(frozen=True)
class StreamableHttpMcpServer:
    """Configuration for a streamable HTTP MCP server (remote endpoint)."""

    transport: Literal["streamable-http"] = "streamable-http"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)


McpServer = Union[StdioMcpServer, StreamableHttpMcpServer]


@dataclass(frozen=True)
class McpConfig:
    """Container for multiple MCP server configs."""

    servers: Dict[str, McpServer]


def load_mcp_json(path: str) -> McpConfig:
    """
    Load the emergent MCP JSON format:
      {
        "mcpServers": {
          "name": { ...server config... }
        }
      }
    """
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    servers_raw = raw.get("mcpServers", {}) or {}
    if not isinstance(servers_raw, dict):
        raise ValueError("Invalid mcp.json: 'mcpServers' must be an object.")

    servers: Dict[str, McpServer] = {}

    for name, entry in servers_raw.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid MCP server entry for '{name}': expected object.")

        entry_type = entry.get("type") or entry.get("transport")
        if entry_type in ("streamable-http", "http", "https"):
            url = entry.get("url")
            if not url:
                raise ValueError(f"Missing 'url' for MCP server '{name}'.")
            headers_raw = entry.get("headers") or {}
            if not isinstance(headers_raw, dict):
                raise ValueError(f"Invalid 'headers' for MCP server '{name}'.")
            servers[name] = StreamableHttpMcpServer(
                url=str(url),
                headers={str(k): str(v) for k, v in headers_raw.items()},
            )
            continue

        if "command" in entry:
            command = entry.get("command")
            if not command:
                raise ValueError(f"Missing 'command' for MCP server '{name}'.")
            args_raw = entry.get("args") or []
            if not isinstance(args_raw, list):
                raise ValueError(f"Invalid 'args' for MCP server '{name}'.")
            env_raw = entry.get("env") or {}
            if not isinstance(env_raw, dict):
                raise ValueError(f"Invalid 'env' for MCP server '{name}'.")
            servers[name] = StdioMcpServer(
                command=str(command),
                args=[str(a) for a in args_raw],
                env={str(k): str(v) for k, v in env_raw.items()},
                cwd=str(entry["cwd"]) if entry.get("cwd") else None,
            )
            continue

        raise ValueError(
            f"Unsupported MCP server config for '{name}'. "
            f"Expected either (type/url) or (command/args/env). "
            f"Got keys={list(entry.keys())}"
        )

    return McpConfig(servers=servers)
