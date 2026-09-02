import json
from src.tools.llm_client import call_llm


TEST_GENERATION_SYSTEM_PROMPT = """You are a senior software engineer writing tests to verify a bug fix.

You will be given the original buggy code and the fixed code. Write a
test file using plain Python assert statements (NOT pytest) that verifies
the fix actually works.

The test file will import from a file called "solution.py" — assume the
fixed code will be saved there. Write test code accordingly, e.g.:
    from solution import function_name

At the end of your test code, if all asserts pass, print "All tests passed".

Respond with ONLY a JSON object in this exact format, with no other text
before or after it:

{
    "test_code": "the complete test file content as a string",
    "explanation": "brief explanation of what this test checks"
}

Do not include markdown code fences, explanations, or any text outside
the JSON object."""


def generate_test(original_code: str, updated_code: str, issue_description: str) -> dict:
    """
    Takes the before/after code from the Implementation Agent and
    generates a test file to verify the fix actually works.
    
    Returns:
        {"test_code": ..., "explanation": ...}
    """
    prompt = (
        f"Bug description:\n{issue_description}\n\n"
        f"Original (buggy) code:\n```python\n{original_code}\n```\n\n"
        f"Fixed code:\n```python\n{updated_code}\n```"
    )
    
    raw_response = call_llm(
        prompt=prompt,
        system_prompt=TEST_GENERATION_SYSTEM_PROMPT
    )
    
    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError:
        raise ValueError(
            f"LLM did not return valid JSON. Raw response:\n{raw_response}"
        )
    
    return result