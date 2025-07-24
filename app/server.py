from fastmcp.server import FastMCP
from atlassian import Jira, Confluence
from bs4 import BeautifulSoup
import openai
import os

from .model import SearchResult, Document

mcp = FastMCP(name="FastMCP Atlassian Server")

ATLASSIAN_URL = os.environ.get("ATLASSIAN_URL")
ATLASSIAN_USERNAME = os.environ.get("ATLASSIAN_USERNAME")
ATLASSIAN_API_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN")

jira = None
conf = None
if ATLASSIAN_URL and ATLASSIAN_USERNAME and ATLASSIAN_API_TOKEN:
    jira = Jira(
        url=ATLASSIAN_URL, username=ATLASSIAN_USERNAME, password=ATLASSIAN_API_TOKEN
    )
    conf = Confluence(
        url=ATLASSIAN_URL, username=ATLASSIAN_USERNAME, password=ATLASSIAN_API_TOKEN
    )

openai.api_key = os.environ.get("OPENAI_API_KEY")


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
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return completion


@mcp.tool(title="Search", description="Search Confluence pages")
def search(query: str, limit: int = 5) -> list:
    """Search Confluence pages using a query string."""
    if conf is None:
        raise RuntimeError("Confluence not configured")
    # Use the generic search endpoint to find pages relevant to the query
    response = conf.search(str=query, limit=limit, excerpt="highlight")
    results: list[dict] = []
    for item in response.get("results", []):
        content = item.get("content", {})
        snippet_html = item.get("excerpt", "")
        snippet_text = BeautifulSoup(snippet_html, "html.parser").get_text()
        sr = SearchResult(
            id=str(content.get("id")),
            title=content.get("title", ""),
            text=snippet_text,
            url=f"{ATLASSIAN_URL}/wiki{content.get('_links', {}).get('web', '')}",
        )
        results.append(sr.asdict())
    return results


@mcp.tool(title="Fetch", description="Fetch a Confluence page by id")
def fetch(page_id: str) -> dict:
    """Fetch a Confluence page by id."""
    if conf is None:
        raise RuntimeError("Confluence not configured")
    page = conf.get_page_by_id(page_id, expand="body.storage,metadata.labels")
    body_html = page.get("body", {}).get("storage", {}).get("value", "")
    text = BeautifulSoup(body_html, "html.parser").get_text()
    doc = Document(
        id=str(page_id),
        title=page.get("title", ""),
        text=text,
        url=f"{ATLASSIAN_URL}/wiki{page.get('_links', {}).get('web', '')}",
        metadata={"space": page.get("space", {}).get("key")},
    )
    return doc.asdict()


# alias for CLI discovery
app = mcp
server = mcp
