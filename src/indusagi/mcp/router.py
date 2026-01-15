from __future__ import annotations

import asyncio
import inspect
import json
import re
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from indusagi.mcp.config import McpConfig, StdioMcpServer, StreamableHttpMcpServer

_MCP_LOADED = False
_MCP_IMPORT_ERROR: Optional[Exception] = None
_MCP_CLIENT_SESSION: Any = None
_MCP_STDIO_PARAMS: Any = None
_MCP_TYPES: Any = None
_MCP_STDIO_CLIENT: Any = None
_MCP_STREAMABLE_HTTP_CLIENT: Any = None


def _require_mcp() -> Tuple[Any, Any, Any, Any, Any]:
    global _MCP_LOADED
    global _MCP_IMPORT_ERROR
    global _MCP_CLIENT_SESSION
    global _MCP_STDIO_PARAMS
    global _MCP_TYPES
    global _MCP_STDIO_CLIENT
    global _MCP_STREAMABLE_HTTP_CLIENT

    if not _MCP_LOADED:
        try:
            from mcp import ClientSession, StdioServerParameters, types
            from mcp.client.stdio import stdio_client
            try:
                from mcp.client.streamable_http import streamable_http_client
            except Exception:
                from mcp.client.streamable_http import streamablehttp_client as streamable_http_client
        except Exception as exc:  # pragma: no cover - import guard
            _MCP_IMPORT_ERROR = exc
        else:
            _MCP_CLIENT_SESSION = ClientSession
            _MCP_STDIO_PARAMS = StdioServerParameters
            _MCP_TYPES = types
            _MCP_STDIO_CLIENT = stdio_client
            _MCP_STREAMABLE_HTTP_CLIENT = streamable_http_client
        _MCP_LOADED = True

    if _MCP_IMPORT_ERROR is not None:
        raise ImportError(
            "MCP SDK is required for indusagi.mcp. "
            "Install it with: pip install \"mcp[cli]\""
        ) from _MCP_IMPORT_ERROR

    return (
        _MCP_CLIENT_SESSION,
        _MCP_STDIO_PARAMS,
        _MCP_TYPES,
        _MCP_STDIO_CLIENT,
        _MCP_STREAMABLE_HTTP_CLIENT,
    )


@dataclass(frozen=True)
class IndusToolDef:
    """Minimal tool definition shape for IndusAGI integration."""

    name: str
    description: str
    parameters_json_schema: Dict[str, Any]
    server: str
    original_tool_name: str


@dataclass(frozen=True)
class ToolExecResult:
    """Normalized tool execution result."""

    tool_name: str
    is_error: bool
    text: str
    structured: Optional[Any]
    raw: Dict[str, Any]


ApprovalFn = Callable[[str, Dict[str, Any]], bool]


class McpToolRouter:
    """
    MCP router that discovers tools and executes tool calls across servers.

    - Loads multiple MCP servers
    - Exposes tools with safe namespacing
    - Executes tool calls and normalizes results
    """

    def __init__(
        self,
        config: McpConfig,
        *,
        name_joiner: str = "__",
        approval: Optional[ApprovalFn] = None,
        cache_sessions: bool = False,
    ):
        self._config = config
        self._name_joiner = name_joiner
        self._approval = approval
        self._cache_sessions = cache_sessions
        self._sessions: Dict[str, _SessionHandle] = {}
        self._tool_map: Dict[str, Tuple[str, str]] = {}
        self._tool_defs: List[IndusToolDef] = []

    async def aclose(self) -> None:
        """Close all open sessions."""
        if not self._cache_sessions:
            return
        for handle in self._sessions.values():
            await handle.aclose()
        self._sessions.clear()

    async def list_tools(self, *, refresh: bool = False) -> List[IndusToolDef]:
        """Fetch tools from all configured MCP servers."""
        _require_mcp()

        if self._tool_defs and not refresh:
            return self._tool_defs

        self._tool_map.clear()
        tool_defs: List[IndusToolDef] = []
        errors: Dict[str, BaseException] = {}

        for server_name in self._config.servers.keys():
            try:
                if self._cache_sessions:
                    session = await self._get_or_connect(server_name)
                    tools_result = await session.list_tools()
                else:
                    handle = await _SessionHandle.connect(self._config.servers[server_name])
                    error: Optional[BaseException] = None
                    try:
                        await handle.session.initialize()
                        tools_result = await handle.session.list_tools()
                    except BaseException as exc:
                        error = exc
                        tools_result = None
                    finally:
                        try:
                            await handle.aclose()
                        except BaseException as exc:
                            if error is None:
                                error = exc
                    if error is not None:
                        raise error
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit, GeneratorExit)):
                    raise
                if isinstance(exc, asyncio.CancelledError):
                    errors[server_name] = exc
                    continue
                errors[server_name] = exc
                continue

            for tool in tools_result.tools:
                safe = self._safe_tool_name(server_name, tool.name)
                self._tool_map[safe] = (server_name, tool.name)

                tool_defs.append(
                    IndusToolDef(
                        name=safe,
                        description=tool.description or "",
                        parameters_json_schema=tool.inputSchema or {"type": "object"},
                        server=server_name,
                        original_tool_name=tool.name,
                    )
                )

        self._tool_defs = tool_defs
        if not tool_defs and errors:
            error_summary = "; ".join(
                f"{name}: {type(err).__name__}: {err}" for name, err in errors.items()
            )
            raise RuntimeError(f"Failed to load tools from MCP servers. {error_summary}")
        return tool_defs

    async def call_tool(
        self,
        safe_tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> ToolExecResult:
        """Execute a namespaced tool against the correct MCP server."""
        _require_mcp()

        arguments = arguments or {}

        if safe_tool_name not in self._tool_map:
            await self.list_tools(refresh=True)
            if safe_tool_name not in self._tool_map:
                raise KeyError(f"Unknown tool: {safe_tool_name}")

        server_name, original_tool = self._tool_map[safe_tool_name]

        if self._approval is not None:
            allowed = self._approval(safe_tool_name, arguments)
            if not allowed:
                return ToolExecResult(
                    tool_name=safe_tool_name,
                    is_error=True,
                    text="Tool call denied by approval policy.",
                    structured=None,
                    raw={"denied": True},
                )

        try:
            if self._cache_sessions:
                session = await self._get_or_connect(server_name)
                result = await session.call_tool(original_tool, arguments=arguments)
            else:
                handle = await _SessionHandle.connect(self._config.servers[server_name])
                try:
                    await handle.session.initialize()
                    result = await handle.session.call_tool(original_tool, arguments=arguments)
                finally:
                    try:
                        await handle.aclose()
                    except BaseException:
                        pass
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit, GeneratorExit)):
                raise
            if isinstance(exc, asyncio.CancelledError):
                return ToolExecResult(
                    tool_name=safe_tool_name,
                    is_error=True,
                    text="Tool call cancelled.",
                    structured=None,
                    raw={"exception": "CancelledError"},
                )
            return ToolExecResult(
                tool_name=safe_tool_name,
                is_error=True,
                text=f"Tool call failed: {exc}",
                structured=None,
                raw={"exception": repr(exc)},
            )

        text, structured, raw = _normalize_call_tool_result(result)
        return ToolExecResult(
            tool_name=safe_tool_name,
            is_error=bool(result.isError),
            text=text,
            structured=structured,
            raw=raw,
        )

    async def _get_or_connect(self, server_name: str) -> Any:
        if server_name in self._sessions:
            return self._sessions[server_name].session

        server = self._config.servers[server_name]
        handle = await _SessionHandle.connect(server)
        self._sessions[server_name] = handle

        await handle.session.initialize()
        return handle.session

    def _safe_tool_name(self, server: str, tool: str) -> str:
        base = f"{server}{self._name_joiner}{tool}".strip()
        base = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
        base = re.sub(r"_+", "_", base)
        return base


class _SessionHandle:
    def __init__(self, session: Any, stack: AsyncExitStack):
        self.session = session
        self._stack = stack

    @classmethod
    async def connect(cls, server: Union[StdioMcpServer, StreamableHttpMcpServer]) -> "_SessionHandle":
        (
            _client_session,
            stdio_params_cls,
            _types,
            stdio_client_fn,
            streamable_http_client_fn,
        ) = _require_mcp()

        stack = AsyncExitStack()

        if isinstance(server, StdioMcpServer):
            params = stdio_params_cls(
                command=server.command,
                args=server.args,
                env=server.env or None,
            )
            read_stream, write_stream = await stack.enter_async_context(stdio_client_fn(params))
            session = await stack.enter_async_context(_client_session(read_stream, write_stream))
            return cls(session=session, stack=stack)

        kwargs: Dict[str, Any] = {}
        try:
            sig = inspect.signature(streamable_http_client_fn)
        except (TypeError, ValueError):
            sig = None

        if sig and "headers" in sig.parameters:
            kwargs["headers"] = server.headers or None

        if sig and "url" in sig.parameters:
            kwargs["url"] = server.url
            streams = await stack.enter_async_context(streamable_http_client_fn(**kwargs))
        else:
            streams = await stack.enter_async_context(streamable_http_client_fn(server.url, **kwargs))

        if not isinstance(streams, tuple) or len(streams) < 2:
            raise RuntimeError("Unexpected streamable_http_client return value.")

        read_stream, write_stream = streams[0], streams[1]
        session = await stack.enter_async_context(_client_session(read_stream, write_stream))
        return cls(session=session, stack=stack)

    async def aclose(self) -> None:
        await self._stack.aclose()


def _normalize_call_tool_result(result: Any) -> Tuple[str, Optional[Any], Dict[str, Any]]:
    """Normalize MCP tool results into text and structured payloads."""
    _require_mcp()
    types = _MCP_TYPES

    parts: List[str] = []
    text_type = getattr(types, "TextContent", None)
    image_type = getattr(types, "ImageContent", None)
    audio_type = getattr(types, "AudioContent", None)
    link_type = getattr(types, "ResourceLink", None)
    embedded_type = getattr(types, "EmbeddedResource", None)

    for block in result.content or []:
        if text_type and isinstance(block, text_type):
            parts.append(block.text)
        elif image_type and isinstance(block, image_type):
            parts.append(f"[image mimeType={block.mimeType} bytes={len(block.data)}]")
        elif audio_type and isinstance(block, audio_type):
            parts.append(f"[audio mimeType={block.mimeType} bytes={len(block.data)}]")
        elif link_type and isinstance(block, link_type):
            parts.append(f"[resource_link name={block.name} uri={block.uri}]")
        elif embedded_type and isinstance(block, embedded_type):
            parts.append("[embedded resource]")
        else:
            parts.append(f"[unknown content block: {type(block).__name__}]")

    structured = getattr(result, "structuredContent", None)

    raw = {
        "isError": bool(getattr(result, "isError", False)),
        "content_types": [getattr(b, "type", type(b).__name__) for b in (result.content or [])],
        "structuredContent": structured,
    }

    if structured is not None and not parts:
        parts.append(json.dumps(structured))

    return "\n".join(parts).strip(), structured, raw
