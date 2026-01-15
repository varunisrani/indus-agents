# Devin MCP Server (IndusAGI)

This guide shows how to use the official Devin MCP server with IndusAGI.

## What is MCP

MCP (Model Context Protocol) is a standard that lets AI apps connect to external tools
and data sources through a consistent interface.

## Server details

- Base URL: https://mcp.devin.ai/
- Authentication: required (API key)
- Supports public and private repositories

## Available tools

- read_wiki_structure
- read_wiki_contents
- ask_question

## Wire protocols

- SSE (official spec): https://mcp.devin.ai/sse
- Streamable HTTP: https://mcp.devin.ai/mcp

IndusAGI's MCP client currently supports streamable HTTP and stdio. Use the /mcp
endpoint for Devin.

## IndusAGI config (mcp.json)

```json
{
  "mcpServers": {
    "devin": {
      "type": "streamable-http",
      "url": "https://mcp.devin.ai/mcp",
      "headers": {
        "Authorization": "Bearer <API_KEY>"
      }
    }
  }
}
```

Replace `<API_KEY>` with a key from your Devin account settings.

## Example usage

```powershell
Copy-Item example_agents/mcp.example.json mcp.json
# edit mcp.json to add your Devin API key
python example_agents/example_mcp_agent.py "Summarize the docs for owner/repo"
```

## Notes

- Keep API keys out of source control.
- The Devin MCP server supports private repositories, so protect access carefully.

## References

- Devin MCP server: https://mcp.devin.ai/
- MCP spec: https://modelcontextprotocol.io/
- DeepWiki MCP (public repos only): https://mcp.deepwiki.com/
