import asyncio
from src.graphs.dev_agent_graph import build_graph


async def main():
    app = build_graph()
    config = {"configurable": {"thread_id": "async-test-1"}}
    
    initial_state = {
        "issue_description": "The calculator tool crashes with a ZeroDivisionError when dividing by zero instead of returning a friendly error message.",
        "owner": "ok315",
        "repo": "Multi-Tool-Agent",
        "branch": "master",
        "plan": {}, "original_code": "", "current_code": "", "current_test": "",
        "test_result": {}, "iteration_count": 0, "max_iterations": 3, "status": "starting",
        "pr_url": ""
    }
    
    print("=== RUNNING UNTIL INTERRUPT (ASYNC, VIA MCP) ===\n")
    result = await app.ainvoke(initial_state, config=config)
    
    state_snapshot = await app.aget_state(config)
    next_nodes = state_snapshot.next
    
    if next_nodes:
        print(f"\n=== GRAPH GENUINELY PAUSED before: {next_nodes} ===")
        print("Proposed fix for:", result["plan"]["issue_summary"])
        print("Iterations used:", result["iteration_count"])
        print("Test verification: PASSED" if result["test_result"]["success"] else "FAILED")
        
        approval = input("\nApprove this PR? (yes/no): ")
        
        if approval.lower() == "yes":
            print("\n=== RESUMING GRAPH ===\n")
            final = await app.ainvoke(None, config=config)
            print("\nPR URL:", final["pr_url"])
        else:
            print("\nRejected — graph stopped, no PR created.")
    else:
        print("\n=== GRAPH FINISHED WITHOUT PAUSING (gave up or errored) ===")
        print("Final status:", result["status"])
        print("Last test result:", result["test_result"])


asyncio.run(main())