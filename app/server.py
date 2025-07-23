from fastmcp.server import FastMCP
from atlassian import Jira, Confluence
import openai
import os

mcp = FastMCP(name="FastMCP Atlassian Server")

ATLASSIAN_URL = os.environ.get("ATLASSIAN_URL")
ATLASSIAN_USERNAME = os.environ.get("ATLASSIAN_USERNAME")
ATLASSIAN_API_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN")

jira = None
conf = None
if ATLASSIAN_URL and ATLASSIAN_USERNAME and ATLASSIAN_API_TOKEN:
    jira = Jira(url=ATLASSIAN_URL, username=ATLASSIAN_USERNAME, password=ATLASSIAN_API_TOKEN)
    conf = Confluence(url=ATLASSIAN_URL, username=ATLASSIAN_USERNAME, password=ATLASSIAN_API_TOKEN)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@mcp.tool
def create_jira_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> dict:
    """Create a Jira issue"""
    if jira is None:
        raise RuntimeError("Jira not configured")
    return jira.issue_create(fields={
        "project": {"key": project_key},
        "summary": summary,
        "description": description,
        "issuetype": {"name": issue_type}
    })

@mcp.tool
def list_jira_boards() -> list:
    """List Jira boards"""
    if jira is None:
        raise RuntimeError("Jira not configured")
    return jira.get_all_boards()

@mcp.tool
def create_confluence_page(space: str, title: str, body: str) -> dict:
    """Create a Confluence page"""
    if conf is None:
        raise RuntimeError("Confluence not configured")
    return conf.create_page(space=space, title=title, body=body)

@mcp.tool
def ask_openai(prompt: str, model: str = "gpt-4") -> dict:
    """Query an OpenAI model"""
    if not openai.api_key:
        raise RuntimeError("OpenAI API key not configured")
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion

# alias for CLI discovery
app = mcp
server = mcp
