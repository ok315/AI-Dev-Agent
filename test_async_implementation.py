import asyncio
from src.agents.implementation_agent import generate_implementation

async def main():
    plan = {
        "issue_summary": "test",
        "files_likely_affected": ["tools/calculator.py"]
    }
    
    result = await generate_implementation(
        plan, owner="ok315", repo="Multi-Tool-Agent", branch="master"
    )
    
    print("File:", result["file_path"])
    print("Original code (first 100 chars):", result["original_code"][:100])
    print("Updated code (first 200 chars):", result["updated_code"][:200])

asyncio.run(main())