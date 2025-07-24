# FastMCP Server

This repository contains a collection of small [FastMCP](https://github.com/jlowin/fastmcp) servers that integrate with Atlassian Jira and Confluence. Each set of tools is exposed from its own MCP server.

## Features
- Jira MCP server
  - Create Jira issues
  - List Jira boards
  - Search Jira issues with the `search` tool
  - Fetch issues with the `fetch` tool
- Confluence MCP server
  - Create Confluence pages
  - Search Confluence pages with the `search` tool using a query string
  - Fetch full pages with the `fetch` tool

## Setup
1. Install dependencies using [uv](https://github.com/astral-sh/uv):
   ```bash
   uv pip install --system
   ```
2. Set the following environment variables for Atlassian:
   - `ATLASSIAN_URL`
   - `ATLASSIAN_USERNAME`
   - `ATLASSIAN_API_TOKEN`

## Running
Run one of the servers depending on the tools you need:
```bash
# Confluence tools
python -m app.confluence.main

# Jira tools
python -m app.jira.main
```

Both servers use the FastMCP SSE transport, which is required for OpenAI Agent Mode if OpenAI tools are added.
