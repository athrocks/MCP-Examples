from mcp import ClientSession
from mcp.client.sse import sse_client  # Use SSE transport for HTTP communication

# Define the MCP server URL
server_url = "http://127.0.0.1:3001/sse"  # Use the correct endpoint

async def run():
    # Start a client session using SSE transport
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available resources
            print("LISTING RESOURCES")
            resources = await session.list_resources()
            print(f"Resources object: {resources}")
            if hasattr(resources, 'resources') and resources.resources:
                for resource in resources.resources:
                    print("Resource:", resource)
            else:
                print("No resources found or empty resources list")

            # List available tools
            print("\nLISTING TOOLS")
            tools = await session.list_tools()
            for tool in tools.tools:
                print("Tool Name:", tool.name, "| Description:", tool.description)

            # Read a resource
            print("\nREADING RESOURCE")
            try:
                resource_result = await session.read_resource("greeting://hello")
                print(f"Resource result: {resource_result}")  # Debug line
                if hasattr(resource_result, 'contents') and resource_result.contents:
                    print("Read Resource Content:", resource_result.contents[0].text)
                else:
                    print("No content found in resource result")
            except Exception as e:
                print(f"Error reading resource: {e}")

            # Call a tool
            print("\nCALLING TOOL")
            result = await session.call_tool("add", arguments={"a": 5, "b": 7})
            print(f"Result of tool 'add': {result.content[0].text}")


if __name__ == "__main__":
    import asyncio
    # Run the async function
    asyncio.run(run())