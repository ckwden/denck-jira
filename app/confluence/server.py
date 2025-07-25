from fastmcp.server import FastMCP
from bs4 import BeautifulSoup
import os
import requests
from requests.auth import HTTPBasicAuth

from ..common.model import SearchResult, Document

mcp = FastMCP(name="Confluence MCP Server")

ATLASSIAN_URL = os.environ.get("ATLASSIAN_URL")
ATLASSIAN_USERNAME = os.environ.get("ATLASSIAN_USERNAME")
ATLASSIAN_API_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN")

session = None
if ATLASSIAN_URL and ATLASSIAN_USERNAME and ATLASSIAN_API_TOKEN:
    session = requests.Session()
    session.auth = HTTPBasicAuth(ATLASSIAN_USERNAME, ATLASSIAN_API_TOKEN)
    session.headers.update({"Accept": "application/json"})


@mcp.tool
def create_confluence_page(space: str, title: str, body: str) -> dict:
    """Create a Confluence page"""
    if session is None:
        raise RuntimeError("Confluence not configured")
    url = f"{ATLASSIAN_URL}/wiki/rest/api/content"
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space},
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    resp = session.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()


@mcp.tool(title="Search", description="Search Confluence pages")
def search(query: str, limit: int = 5) -> list:
    """Search Confluence pages using a query string."""
    if session is None:
        raise RuntimeError("Confluence not configured")
    url = f"{ATLASSIAN_URL}/wiki/rest/api/search"
    params = {"cql": query, "limit": limit, "excerpt": "highlight"}
    resp = session.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    results: list[dict] = []
    for item in data.get("results", []):
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
    if session is None:
        raise RuntimeError("Confluence not configured")
    url = f"{ATLASSIAN_URL}/wiki/rest/api/content/{page_id}"
    params = {"expand": "body.storage,metadata.labels,space"}
    resp = session.get(url, params=params)
    resp.raise_for_status()
    page = resp.json()
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
