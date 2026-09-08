import asyncio
from src.graphs.dev_agent_graph import build_graph


async def main():
    app = build_graph()
    config = {"configurable": {"thread_id": "async-inventory-test-1"}}
    
    initial_state = {
        "issue_description": "The remove_stock function should not allow negative quantity arguments — if quantity is negative, it should raise a ValueError instead of silently adding to the stock (since removing a negative quantity would incorrectly increase stock).",
        "owner": "ok315",
        "repo": "inventory-tracker",
        "branch": "main",
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
        print("\nCode to be committed:\n", result["current_code"])
        
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