from src.tools.github_client import github
from src.tools.llm_client import call_llm
from mcp import Client
from src.mcp_servers.github_server import mcp as github_mcp

IMPLEMENTATION_SYSTEM_PROMPT = """You are a senior software engineer fixing a bug.

You will be given:
1. A plan describing what needs to change
2. The COMPLETE current content of the file that needs to be modified

Your job is to return the COMPLETE corrected version of the file —
not just the changed function, the entire file with the fix applied,
keeping everything else exactly as it was.

Respond with ONLY a JSON object in this exact format, with no other
text before or after it:

{
    "updated_code": "the complete corrected file content as a string",
    "explanation": "a brief explanation of what you changed and why"
}

Do not include markdown code fences, explanations, or any text outside
the JSON object. The "updated_code" value must be the full file, ready
to replace the original file exactly as-is."""


async def generate_implementation(
    plan: dict, owner: str, repo: str, branch: str,
    previous_code: str = None, test_code: str = None, failure_output: str = None
) -> dict:
    if not plan.get("files_likely_affected"):
        raise ValueError("Plan has no files_likely_affected — nothing to implement.")
    
    file_path = plan["files_likely_affected"][0]
    
    async with Client(github_mcp) as client:
        mcp_result = await client.call_tool(
            "get_file_content",
            {"owner": owner, "repo": repo, "path": file_path, "branch": branch}
        )
    
    original_code = mcp_result.content[0].text
    
    prompt = (
        f"Plan:\n{plan}\n\n"
        f"Current content of {file_path}:\n"
        f"```python\n{original_code}\n```"
    )
    
    if previous_code and test_code and failure_output:
        prompt += (
            f"\n\nA PREVIOUS ATTEMPT at this fix FAILED. Here is what was tried:\n"
            f"```python\n{previous_code}\n```\n\n"
            f"The test that verifies this fix:\n"
            f"```python\n{test_code}\n```\n\n"
            f"The failure output was:\n{failure_output}\n\n"
            f"Fix the SPECIFIC problem shown above. Pay close attention to exact "
            f"expected values, strings, or behavior the test requires."
        )
    
    raw_response = call_llm(
        prompt=prompt,
        system_prompt=IMPLEMENTATION_SYSTEM_PROMPT
    )
    
    import json
    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError:
        raise ValueError(
            f"LLM did not return valid JSON. Raw response:\n{raw_response}"
        )
    
    return {
        "file_path": file_path,
        "original_code": original_code,
        "updated_code": result["updated_code"],
        "explanation": result["explanation"]
    }