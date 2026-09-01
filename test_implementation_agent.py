import json
from src.agents.planning_agent import generate_plan
from src.agents.implementation_agent import generate_implementation

issue = "The calculator tool crashes with a ZeroDivisionError when dividing by zero instead of returning a friendly error message."

plan = generate_plan(issue, repo="Multi-Tool-Agent")
print("PLAN:")
print(json.dumps(plan, indent=2))

result = generate_implementation(plan, owner="ok315", repo="Multi-Tool-Agent", branch="master")

print("\n\nORIGINAL CODE:")
print(result["original_code"])

print("\n\nUPDATED CODE:")
print(result["updated_code"])

print("\n\nEXPLANATION:")
print(result["explanation"])