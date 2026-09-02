import json
from src.agents.planning_agent import generate_plan
from src.agents.implementation_agent import generate_implementation
from src.agents.test_agent import generate_test
from src.tools.sandbox import run_code_in_sandbox

issue = "The calculator tool crashes with a ZeroDivisionError when dividing by zero instead of returning a friendly error message."

plan = generate_plan(issue, repo="Multi-Tool-Agent")
implementation = generate_implementation(plan, owner="ok315", repo="Multi-Tool-Agent", branch="master")

test = generate_test(
    original_code=implementation["original_code"],
    updated_code=implementation["updated_code"],
    issue_description=issue
)

print("GENERATED TEST CODE:")
print(test["test_code"])
print("\nEXPLANATION:", test["explanation"])

# Now actually run the fix + test together in the sandbox
files = {
    "solution.py": implementation["updated_code"],
    "test_solution.py": test["test_code"]
}

result = run_code_in_sandbox(files, entry_point="test_solution.py")

print("\n\nSANDBOX RESULT:")
print(result)