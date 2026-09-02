from typing import TypedDict
from langgraph.graph import StateGraph, END


class FakeState(TypedDict):
    attempt: int
    max_iterations: int
    succeeded: bool


def fake_implement(state: FakeState) -> dict:
    print(f"  [fake implement] attempt {state['attempt'] + 1}")
    return {"attempt": state["attempt"] + 1}


def fake_test(state: FakeState) -> dict:
    # Deliberately fail the first 2 attempts, succeed on the 3rd —
    # simulates a real debug loop needing multiple tries.
    success = state["attempt"] >= 3
    print(f"  [fake test] attempt {state['attempt']} -> {'PASS' if success else 'FAIL'}")
    return {"succeeded": success}


def route(state: FakeState) -> str:
    if state["succeeded"]:
        return "success"
    if state["attempt"] >= state["max_iterations"]:
        return "give_up"
    return "retry"


graph = StateGraph(FakeState)
graph.add_node("implement", fake_implement)
graph.add_node("test", fake_test)
graph.set_entry_point("implement")
graph.add_edge("implement", "test")
graph.add_conditional_edges(
    "test", route,
    {"success": END, "give_up": END, "retry": "implement"}
)

app = graph.compile()

print("Scenario: should succeed on attempt 3 (max_iterations=3)")
result = app.invoke({"attempt": 0, "max_iterations": 3, "succeeded": False})
print("Final:", result)

print("\nScenario: should give up (max_iterations=2, needs 3 to succeed)")
result = app.invoke({"attempt": 0, "max_iterations": 2, "succeeded": False})
print("Final:", result)