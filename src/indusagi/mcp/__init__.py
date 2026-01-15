"""
MCP integration utilities for IndusAGI.
"""

from indusagi.mcp.config import McpConfig, StdioMcpServer, StreamableHttpMcpServer, load_mcp_json
from indusagi.mcp.executor import McpToolRegistry, ToolExecutorMux
from indusagi.mcp.router import IndusToolDef, McpToolRouter, ToolExecResult

__all__ = [
    "McpConfig",
    "StdioMcpServer",
    "StreamableHttpMcpServer",
    "load_mcp_json",
    "IndusToolDef",
    "ToolExecResult",
    "McpToolRouter",
    "McpToolRegistry",
    "ToolExecutorMux",
]
