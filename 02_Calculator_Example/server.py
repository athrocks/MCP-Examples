# Create Server Code
from mcp.server.fastmcp import FastMCP

# Create an MCP server with port 3001 specified in constructor
mcp = FastMCP("Demo", port=3001)

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together and return the result."""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a and return the result."""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together and return the result."""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divide a by b and return the result.
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def help() -> str:
    """Get help information about available calculator operations."""
    return """
Available Calculator Operations:
- add(a, b): Add two numbers together
- subtract(a, b): Subtract b from a  
- multiply(a, b): Multiply two numbers together
- divide(a, b): Divide a by b (b cannot be zero)
"""

# Main execution block - this is required to run the server
if __name__ == "__main__":
    # Run with SSE transport (which the inspector expects)
    mcp.run(transport="sse")