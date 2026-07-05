import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def test_mcp():
    print("Testing MCP Server connection...")
    
    url = "http://127.0.0.1:8000/mcp/sse"
    
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                print("Successfully initialized MCP session.")
                
                # List tools
                tools_response = await session.list_tools()
                print(f"Discovered {len(tools_response.tools)} tools:")
                for tool in tools_response.tools:
                    print(f" - {tool.name}: {tool.description}")
                    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to connect or test: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp())
