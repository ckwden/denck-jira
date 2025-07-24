from fastmcp.server import FastMCP
from atlassian import Jira
import os

from ..common.model import SearchResult, Document

mcp = FastMCP(name="Jira MCP Server")

ATLASSIAN_URL = os.environ.get("ATLASSIAN_URL")
ATLASSIAN_USERNAME = os.environ.get("ATLASSIAN_USERNAME")
ATLASSIAN_API_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN")

jira = None
if ATLASSIAN_URL and ATLASSIAN_USERNAME and ATLASSIAN_API_TOKEN:
    jira = Jira(
        url=ATLASSIAN_URL,
        username=ATLASSIAN_USERNAME,
        password=ATLASSIAN_API_TOKEN,
    )


@mcp.tool
def create_jira_issue(
    project_key: str, summary: str, description: str, issue_type: str = "Task"
) -> dict:
    """Create a Jira issue"""
    if jira is None:
        raise RuntimeError("Jira not configured")
    return jira.issue_create(
        fields={
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
    )


@mcp.tool
def list_jira_boards() -> list:
    """List Jira boards"""
    if jira is None:
        raise RuntimeError("Jira not configured")
    return jira.get_all_boards()


@mcp.tool(title="Search", description="Search Jira issues")
def search(query: str, limit: int = 5) -> list:
    """Search Jira issues using a JQL query string."""
    if jira is None:
        raise RuntimeError("Jira not configured")
    response = jira.jql(query, limit=limit)
    issues = response.get("issues", [])
    results: list[dict] = []
    for issue in issues:
        fields = issue.get("fields", {})
        sr = SearchResult(
            id=issue.get("key", ""),
            title=fields.get("summary", ""),
            text=(fields.get("description") or ""),
            url=f"{ATLASSIAN_URL}/browse/{issue.get('key')}",
        )
        results.append(sr.asdict())
    return results


@mcp.tool(title="Fetch", description="Fetch a Jira issue by id")
def fetch(issue_id: str) -> dict:
    """Fetch a Jira issue by id."""
    if jira is None:
        raise RuntimeError("Jira not configured")
    issue = jira.issue(issue_id)
    fields = issue.get("fields", {})
    doc = Document(
        id=issue.get("key", ""),
        title=fields.get("summary", ""),
        text=(fields.get("description") or ""),
        url=f"{ATLASSIAN_URL}/browse/{issue.get('key')}",
        metadata={"project": fields.get("project", {}).get("key")},
    )
    return doc.asdict()

# alias for CLI discovery
app = mcp
server = mcp
