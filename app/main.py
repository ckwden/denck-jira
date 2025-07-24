from .server import mcp

if __name__ == "__main__":
    # Run the server using SSE transport for OpenAI compatibility
    mcp.run(transport="sse")
