import asyncio
from mcp import Client
from src.mcp_servers.sandbox_server import mcp


async def main():
    async with Client(mcp) as client:
        files = {
            "solution.py": "def add(a, b):\n    return a + b\n",
            "test_solution.py": "from solution import add\nassert add(2, 3) == 5\nprint('Test passed!')\n"
        }
        
        result = await client.call_tool(
            "run_code",
            {"files": files, "entry_point": "test_solution.py"}
        )
        
        print("is_error:", result.is_error)
        print("content:", result.content)
        print("structured_content:", result.structured_content)


asyncio.run(main())