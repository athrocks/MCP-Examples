#!/usr/bin/env python3
"""
Simple MCP client to test the stdio server
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server with proper initialization"""
    
    # Configure server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None
    )
    
    print("Connecting to MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            print("\n1. Initializing connection...")
            await session.initialize()
            print("✓ Initialization complete")
            
            # List available tools
            print("\n2. Listing available tools...")
            tools = await session.list_tools()
            print(f"✓ Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")
            
            # Test the add tool
            print("\n3. Testing 'add' tool (5 + 3)...")
            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"✓ Result: {result.content[0].text}")
            
            # Test the multiply tool
            print("\n4. Testing 'multiply' tool (7 * 6)...")
            result = await session.call_tool("multiply", {"a": 7, "b": 6})
            print(f"✓ Result: {result.content[0].text}")
            
            # Test the greeting tool
            print("\n5. Testing 'get_greeting' tool...")
            result = await session.call_tool("get_greeting", {"name": "Alice"})
            print(f"✓ Result: {result.content[0].text}")
            
            # Test the server info tool
            print("\n6. Getting server info...")
            result = await session.call_tool("get_server_info", {})
            print(f"✓ Result: {result.content[0].text}")
            
            print("\n✅ All tests passed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_mcp_server())
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)