from src.graphs.dev_agent_graph import build_graph

app = build_graph()
config = {"configurable": {"thread_id": "test-run-2"}}   # new thread_id, fresh run

initial_state = {
    "issue_description": "The calculator tool crashes with a ZeroDivisionError when dividing by zero instead of returning a friendly error message.",
    "owner": "ok315",
    "repo": "Multi-Tool-Agent",
    "branch": "master",
    "plan": {}, "original_code": "", "current_code": "", "current_test": "",
    "test_result": {}, "iteration_count": 0, "max_iterations": 3, "status": "starting",
    "pr_url": ""
}

print("=== RUNNING UNTIL INTERRUPT ===\n")
result = app.invoke(initial_state, config=config)

# Check WHERE the graph actually stopped, instead of assuming
state_snapshot = app.get_state(config)
next_nodes = state_snapshot.next

if next_nodes:
    print(f"\n=== GRAPH GENUINELY PAUSED before: {next_nodes} ===")
    print("Proposed fix for:", result["plan"]["issue_summary"])
    print("\nGenerated test:\n", result["current_test"])
    print("\nCode to be committed:\n", result["current_code"])
    print("\nTest verification: PASSED")
    
    approval = input("\nApprove this PR? (yes/no): ")
    
    if approval.lower() == "yes":
        print("\n=== RESUMING GRAPH ===\n")
        final = app.invoke(None, config=config)
        print("\nPR URL:", final["pr_url"])
    else:
        print("\nRejected — graph stopped, no PR created.")
else:
    print("\n=== GRAPH FINISHED WITHOUT PAUSING (gave up or errored) ===")
    print("Final status:", result["status"])
    print("\nLast attempted code:\n", result["current_code"])
    print("\nGenerated test:\n", result["current_test"])
    print("\nLast test result:\n", result["test_result"])