import json
from src.tools.llm_client import call_llm
from src.agents.codebase_agent import ask_codebase


PLANNING_SYSTEM_PROMPT = """You are a senior software engineer creating a plan to fix a bug.

You will be given a bug description AND relevant code snippets found in the
actual codebase. Base your plan on the ACTUAL files and code shown to you —
do not guess or invent file paths that weren't shown to you.

Respond with ONLY a JSON object in this exact format, with no other text
before or after it:

{
    "issue_summary": "one sentence restating what the bug is",
    "files_likely_affected": ["path/to/file.py"],
    "steps": ["Step 1 description", "Step 2 description"],
    "risk_notes": "anything that could go wrong or needs care"
}

Do not include markdown code fences, explanations, or any text outside the JSON object."""


def generate_plan(issue_description: str, repo: str) -> dict:
    """
    Takes a bug/issue description, retrieves relevant real code from
    the indexed codebase, and asks the LLM to produce a structured
    plan grounded in the actual repo — not guessed file paths.
    """
    relevant_code = ask_codebase(issue_description, repo=repo, n_results=3)
    
    context = "Relevant code found in the codebase:\n\n"
    for chunk in relevant_code:
        context += f"File: {chunk['file_path']} (lines {chunk['start_line']}-{chunk['end_line']})\n"
        context += f"```python\n{chunk['code']}\n```\n\n"
    
    full_prompt = f"{context}\nBug description:\n{issue_description}"
    
    raw_response = call_llm(
        prompt=full_prompt,
        system_prompt=PLANNING_SYSTEM_PROMPT
    )
    
    try:
        plan = json.loads(raw_response)
    except json.JSONDecodeError:
        raise ValueError(
            f"LLM did not return valid JSON. Raw response:\n{raw_response}"
        )
    
    return plan