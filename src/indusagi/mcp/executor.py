from __future__ import annotations

import asyncio
import threading
from typing import Any, Dict, List, Optional

from indusagi.mcp.router import IndusToolDef, McpToolRouter, ToolExecResult


class _AsyncRunner:
    """Run coroutines on a dedicated event loop thread."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="indusagi-mcp-loop",
            daemon=True,
        )
        self._closed = False
        self._thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro: Any) -> Any:
        if self._closed:
            raise RuntimeError("MCP async runner is closed.")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=2)


class McpToolRegistry:
    """
    Sync adapter that exposes MCP tools using IndusAGI's tool executor shape.

    - schemas -> OpenAI tool schemas
    - execute(name, **kwargs) -> tool result text
    """

    def __init__(self, router: McpToolRouter, *, auto_refresh: bool = False) -> None:
        self._router = router
        self._auto_refresh = auto_refresh
        self._runner = _AsyncRunner()
        self._closed = False

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        tool_defs = self._runner.run(self._router.list_tools(refresh=self._auto_refresh))
        return [self._to_openai_schema(tool_def) for tool_def in tool_defs]

    def list_tool_defs(self, *, refresh: bool = False) -> List[IndusToolDef]:
        return self._runner.run(self._router.list_tools(refresh=refresh))

    def execute(self, name: str, **kwargs: Any) -> str:
        result: ToolExecResult = self._runner.run(
            self._router.call_tool(name, arguments=kwargs)
        )
        if result.is_error:
            return f"MCP tool error: {result.text}"
        return result.text

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._runner.run(self._router.aclose())
        self._runner.close()

    def _to_openai_schema(self, tool_def: IndusToolDef) -> Dict[str, Any]:
        parameters = tool_def.parameters_json_schema or {"type": "object"}
        if not isinstance(parameters, dict):
            parameters = {"type": "object"}
        else:
            parameters = dict(parameters)
        if "type" not in parameters:
            parameters["type"] = "object"
        return {
            "type": "function",
            "function": {
                "name": tool_def.name,
                "description": tool_def.description,
                "parameters": parameters,
            },
        }

    def __enter__(self) -> "McpToolRegistry":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()


class ToolExecutorMux:
    """Combine multiple tool executors into one."""

    def __init__(self, *executors: Any) -> None:
        self._executors = list(executors)
        self._tool_map: Dict[str, Any] = {}
        self._schemas: List[Dict[str, Any]] = []

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        self._build_index()
        return list(self._schemas)

    def execute(self, name: str, **kwargs: Any) -> str:
        executor = self._tool_map.get(name)
        if executor is None:
            self._build_index()
            executor = self._tool_map.get(name)
        if executor is None:
            raise ValueError(f"Tool '{name}' not found in executor mux.")
        return executor.execute(name, **kwargs)

    def close(self) -> None:
        for executor in self._executors:
            close_fn = getattr(executor, "close", None)
            if callable(close_fn):
                close_fn()

    def _build_index(self) -> None:
        self._tool_map.clear()
        self._schemas = []
        for executor in self._executors:
            schemas = getattr(executor, "schemas", None)
            if schemas is None:
                continue
            if callable(schemas):
                schemas_list = schemas()
            else:
                schemas_list = schemas
            if not isinstance(schemas_list, list):
                continue
            self._schemas.extend(schemas_list)
            for schema in schemas_list:
                name = self._schema_name(schema)
                if name:
                    self._tool_map[name] = executor

    @staticmethod
    def _schema_name(schema: Dict[str, Any]) -> Optional[str]:
        if not isinstance(schema, dict):
            return None
        if schema.get("type") == "function":
            return schema.get("function", {}).get("name")
        return schema.get("name")
