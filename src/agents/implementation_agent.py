from src.tools.github_client import github
from src.tools.llm_client import call_llm


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


def generate_implementation(plan: dict, owner: str, repo: str, branch: str) -> dict:
    """
    Takes a plan (from generate_plan) and produces actual corrected
    code for the first affected file.
    
    Fetches the REAL, full, current file from GitHub — not the
    isolated chunk from ChromaDB — so the LLM has complete context
    and won't accidentally destroy unrelated code in the file.
    
    Returns:
        {
            "file_path": which file was modified,
            "original_code": the file's content before changes,
            "updated_code": the LLM's proposed corrected file,
            "explanation": what changed and why
        }
    """
    if not plan.get("files_likely_affected"):
        raise ValueError("Plan has no files_likely_affected — nothing to implement.")
    
    file_path = plan["files_likely_affected"][0]
    
    original_code = github.get_file_content(owner, repo, file_path, branch=branch)
    
    prompt = (
        f"Plan:\n{plan}\n\n"
        f"Current content of {file_path}:\n"
        f"```python\n{original_code}\n```"
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