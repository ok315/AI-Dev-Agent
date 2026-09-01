import json
from src.agents.planning_agent import generate_plan

issue = "The calculator tool crashes with a ZeroDivisionError when dividing by zero instead of returning a friendly error message."

plan = generate_plan(issue, repo="Multi-Tool-Agent")

print(json.dumps(plan, indent=2))