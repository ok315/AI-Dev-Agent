import asyncio
from src.graphs.dev_agent_graph import run_test_node

async def main():
    fake_state = {
        "current_code": "def add(a, b):\n    return a + b\n",
        "current_test": "from solution import add\nassert add(2, 3) == 5\nprint('Test passed!')\n"
    }
    
    result = await run_test_node(fake_state)
    print(result)

asyncio.run(main())