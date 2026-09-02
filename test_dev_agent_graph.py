from src.graphs.dev_agent_graph import build_graph

app = build_graph()

initial_state = {
    "issue_description": "The calculator tool crashes with a ZeroDivisionError when dividing by zero instead of returning a friendly error message.",
    "owner": "ok315",
    "repo": "Multi-Tool-Agent",
    "branch": "master",
    "plan": {},
    "original_code": "",
    "current_code": "",
    "current_test": "",
    "test_result": {},
    "iteration_count": 0,
    "max_iterations": 3,
    "status": "starting"
}

result = app.invoke(initial_state)

print("\n\nFINAL STATUS:", result["status"])
print("ITERATIONS USED:", result["iteration_count"])
print("TEST PASSED:", result["test_result"]["success"])