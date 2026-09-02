from typing import TypedDict
from src.agents.planning_agent import generate_plan
from src.agents.implementation_agent import generate_implementation
from src.agents.test_agent import generate_test
from src.tools.sandbox import run_code_in_sandbox
from langgraph.graph import StateGraph, END

class DevAgentState(TypedDict):
    issue_description: str
    owner: str
    repo: str
    branch: str
    plan: dict
    original_code: str
    current_code: str
    current_test: str
    test_result: dict
    iteration_count: int
    max_iterations: int
    status: str

def plan_node(state: DevAgentState) -> dict:
    print("PLANNING...")
    plan = generate_plan(state["issue_description"], repo=state["repo"])
    return {"plan": plan, "status": "planned"}

def implement_node(state: DevAgentState) -> dict:
    print(f"IMPLEMENTING (attempt {state['iteration_count'] + 1})...")
    
    implementation = generate_implementation(
        state["plan"], owner=state["owner"], repo=state["repo"], branch=state["branch"]
    )
    
    updates = {
        "current_code": implementation["updated_code"],
        "iteration_count": state["iteration_count"] + 1,
        "status": "implemented"
    }
    
    # Only set original_code on the very first attempt — keep it
    # stable across retries so we always compare against the true
    # starting point, not a previous failed attempt.
    if not state.get("original_code"):
        updates["original_code"] = implementation["original_code"]
    
    return updates

def test_gen_node(state: DevAgentState) -> dict:
    print("GENERATING TEST...")
    
    # Only generate the test ONCE — on the first pass. On retries,
    # we keep using the same test (test defines "correct", it shouldn't
    # move between attempts).
    if state.get("current_test"):
        print("  (reusing existing test)")
        return {}
    
    test = generate_test(
        original_code=state["original_code"],
        updated_code=state["current_code"],
        issue_description=state["issue_description"]
    )
    return {"current_test": test["test_code"]}

def run_test_node(state: DevAgentState) -> dict:
    print("RUNNING TEST IN SANDBOX...")
    
    files = {
        "solution.py": state["current_code"],
        "test_solution.py": state["current_test"]
    }
    result = run_code_in_sandbox(files, entry_point="test_solution.py")
    
    print(f"  Result: {'PASSED' if result['success'] else 'FAILED'}")
    
    return {"test_result": result, "status": "tested"}

def should_continue(state: DevAgentState) -> str:
    """
    Decides what happens after a test run:
      - test passed -> we're done, succeed
      - test failed, but we still have retries left -> loop back and try again
      - test failed, and we've hit max_iterations -> give up, report failure
    """
    if state["test_result"]["success"]:
        print("TEST PASSED — stopping loop.")
        return "success"
    
    if state["iteration_count"] >= state["max_iterations"]:
        print(f"Max iterations ({state['max_iterations']}) reached — giving up.")
        return "give_up"
    
    print("Test failed — retrying implementation.")
    return "retry"

def build_graph():
    """
    Assembles the full graph:
    
    plan -> implement -> generate_test -> run_test -> (conditional)
                              ^                              |
                              |______________________________|
                                    (retry, back to implement)
    """
    graph = StateGraph(DevAgentState)
    
    graph.add_node("plan", plan_node)
    graph.add_node("implement", implement_node)
    graph.add_node("generate_test", test_gen_node)
    graph.add_node("run_test", run_test_node)
    
    graph.set_entry_point("plan")
    
    # Straight-line steps: plan -> implement -> generate_test -> run_test
    graph.add_edge("plan", "implement")
    graph.add_edge("implement", "generate_test")
    graph.add_edge("generate_test", "run_test")
    
    # The actual loop: after run_test, decide what happens next
    graph.add_conditional_edges(
        "run_test",
        should_continue,
        {
            "success": END,
            "give_up": END,
            "retry": "implement"    # <- this is the cycle: loop back
        }
    )
    
    return graph.compile()