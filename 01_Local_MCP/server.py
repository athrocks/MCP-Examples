# Create Server Code
from mcp.server.fastmcp import FastMCP

# Create an MCP server with port 3001 specified in constructor
mcp = FastMCP("Demo", port=3001)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Main execution block - this is required to run the server
if __name__ == "__main__":
    # Run with SSE transport (which the inspector expects)
    mcp.run(transport="sse")