# DeepWiki MCP Server (IndusAGI)

This guide shows how to use the official DeepWiki MCP server with IndusAGI.

## What is MCP

MCP (Model Context Protocol) is a standard that lets AI apps connect to external tools
and data sources through a consistent interface.

## Server details

- Base URL: https://mcp.deepwiki.com/
- Authentication: not required
- Repositories: public only

## Available tools

- read_wiki_structure
- read_wiki_contents
- ask_question

## Wire protocols

- SSE (official spec): https://mcp.deepwiki.com/sse
- Streamable HTTP: https://mcp.deepwiki.com/mcp

IndusAGI's MCP client currently supports streamable HTTP and stdio. Use the /mcp
endpoint for DeepWiki.

## IndusAGI config (mcp.json)

```json
{
  "mcpServers": {
    "deepwiki": {
      "type": "streamable-http",
      "url": "https://mcp.deepwiki.com/mcp"
    }
  }
}
```

## Example usage

```powershell
Copy-Item example_agents/mcp.example.json mcp.json
python example_agents/example_mcp_agent.py "Summarize the docs for owner/repo"
```

## Notes

- DeepWiki only supports public repositories.
- For private repos, use the Devin MCP server with an API key.

## References

- DeepWiki MCP: https://mcp.deepwiki.com/
- MCP spec: https://modelcontextprotocol.io/
- Devin MCP (private repos): https://mcp.devin.ai/
