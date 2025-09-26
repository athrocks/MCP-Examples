from mcp import ClientSession
from mcp.client.sse import sse_client  # Use SSE transport for HTTP communication

# llm
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import json

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Create server parameters for stdio connection
server_url = "http://127.0.0.1:3001/sse"  # Use the correct endpoint

def call_llm(prompt, functions):
    token = os.environ["GITHUB_TOKEN"] # github_token expiring in 7 days
    endpoint = "https://models.inference.ai.azure.com"

    model_name = "gpt-4o"

    # ChatCompletionsClient is Azure's inference client for calling large language models (e.g., OpenAI GPT models).
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )

    print("CALLING LLM")

    # sending message to Azure OpenAI API (GPT-4o Model)
    response = client.complete(
        # System Mssg sets AI's personality to <You are a helpful assistant.>
        # user Mssg contains actual query (eg: <Add 2 to 20>)
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        model=model_name,
        tools = functions, # tells the AI about available function it can call (eg: add with parameter a & b)
        # Optional parameters
        temperature=1., # temp=1 -> controls randomness, 0->deterministic, 2-> very random
        max_tokens=1000, # maximum response length
        top_p=1. # controles diversity of response
    )

    # extract response message
    # the API returns a response object with multiple possible completions
    # choice[0] gets the first completion choice
    # .message: extracts the actual message
    response_message = response.choices[0].message
    
    # creates empty list to store functions the AI wants to call, will be populated if AI decides to use tools.
    functions_to_call = []

    # process toll calls
    if response_message.tool_calls: # if AI decides to use function, this contains the function call details
        for tool_call in response_message.tool_calls: # process each tool call
            print("TOOL: ", tool_call)
            name = tool_call.function.name # extract name
            args = json.loads(tool_call.function.arguments) # parse function arguments
            functions_to_call.append({ "name": name, "args": args }) # store function call details

    return functions_to_call # returns a list of functions AI wants to call

# Converts each MCP tool on the server into a schema that is consumable by the LLM.
def convert_to_llm_tool(tool):
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"]
            }
        }
    }

    return tool_schema

# async def run():
#     async with sse_client(server_url) as (read, write):
#         async with ClientSession(
#             read, write
#         ) as session:
#             # Initialize the connection
#             await session.initialize()

#             # List available resources
#             # resources = await session.list_resources()
#             # print("LISTING RESOURCES")
#             # print(f"Raw resources list: {resources}")
#             # for resource in resources:
#             #     print("Resource: ", resource)

#             # List available tools
#             tools = await session.list_tools() # queries the server for all registered tools.
#             print("LISTING TOOLS")

#             functions = []

#             for tool in tools.tools:
#                 print("Tool: ", tool.name)
#                 print("Tool", tool.inputSchema["properties"])
#                 functions.append(convert_to_llm_tool(tool))
            
#             # prompt = "Add 2 to 20" # natural language prompt defined here.
#             prompt = "Summation of 2 & 20" # natural language prompt defined here.

#             # ask LLM what tools to all, if any
#             functions_to_call = call_llm(prompt, functions)

#             # call suggested functions
#             for f in functions_to_call:
#                 result = await session.call_tool(f["name"], arguments=f["args"])
#                 print("TOOLS result: ", result.content)

async def run():
    async with sse_client(server_url) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available resources
            resources = await session.list_resources()
            print("LISTING RESOURCES")
            print(f"Raw resources list: {resources}")
            print("Note: FastMCP has resource listing bug - resources work but don't show in list")
            
            # Fix the resource iteration
            if resources.resources:
                for resource in resources.resources:  # Correct way
                    print(f"Resource URI: {resource.uri}")
                    print(f"Resource Name: {resource.name}")
                    print(f"Resource Description: {resource.description}")
            else:
                print("No resources found in list")

            # TEST: Try reading resource directly even if not listed
            print("\n=== TESTING DIRECT RESOURCE ACCESS ===")
            test_resources = [
                "greeting://Alice",
                "greeting://Bob", 
                "greeting://TestUser"
            ]

            for resource_uri in test_resources:
                try:
                    resource_content = await session.read_resource(resource_uri)
                    print(f"✅ SUCCESS: Read resource {resource_uri}")
                    print(f"Content: {resource_content.contents}")
                    break  # If one works, they all should work
                except Exception as e:
                    print(f" FAILED: Could not read resource {resource_uri}: {e}")

            # List available tools
            tools = await session.list_tools()
            print("\nLISTING TOOLS")

            functions = []

            for tool in tools.tools:
                print("Tool: ", tool.name)
                print("Tool", tool.inputSchema["properties"])
                functions.append(convert_to_llm_tool(tool))
            
            prompt = "Addition of 20 & 10"

            # ask LLM what tools to call, if any
            functions_to_call = call_llm(prompt, functions)

            # call suggested functions
            for f in functions_to_call:
                result = await session.call_tool(f["name"], arguments=f["args"])
                print("TOOLS result: ", result.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())