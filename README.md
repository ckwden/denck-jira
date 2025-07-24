# FastMCP Server

This repository contains a simple [FastMCP](https://github.com/jlowin/fastmcp) server that integrates with Atlassian Jira and Confluence and can also make requests to OpenAI models.

## Features
- Create Jira issues
- List Jira boards
- Create Confluence pages
- Query OpenAI models
- Search Confluence content with the `search` tool using a query string
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
3. (Optional) Set `OPENAI_API_KEY` for OpenAI integration.

## Running
```bash
python -m app.main
```

The server will start using the FastMCP SSE transport, which is required for OpenAI Agent Mode.
