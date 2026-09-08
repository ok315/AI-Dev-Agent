import asyncio
from mcp import Client
from src.mcp_servers.github_server import mcp


async def main():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_repo_info",
            {"owner": "ok315", "repo": "Multi-Tool-Agent"}
        )
        print("is_error:", result.is_error)
        print("content:", result.content)
        print("structured_content:", result.structured_content)


asyncio.run(main())