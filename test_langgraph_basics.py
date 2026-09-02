from typing import TypedDict
from langgraph.graph import StateGraph, END


# Step 1: define the state shape
class SimpleState(TypedDict):
    count: int
    message: str


# Step 2: define nodes — each takes state, returns updates
def increment_node(state: SimpleState) -> dict:
    new_count = state["count"] + 1
    print(f"  incrementing: {state['count']} -> {new_count}")
    return {"count": new_count}


def check_done(state: SimpleState) -> str:
    """
    This is a CONDITIONAL function — not a node itself, but decides
    which node to go to next. It returns a string label, which we'll
    map to actual node names below.
    """
    if state["count"] >= 3:
        return "finish"
    else:
        return "loop_again"


def finish_node(state: SimpleState) -> dict:
    print("  done!")
    return {"message": "Reached target count"}


# Step 3: build the graph
graph = StateGraph(SimpleState)

graph.add_node("increment", increment_node)
graph.add_node("finish", finish_node)

graph.set_entry_point("increment")

# This is the conditional edge — after "increment" runs, call
# check_done() to decide: go back to "increment" again, or go to "finish"
graph.add_conditional_edges(
    "increment",
    check_done,
    {
        "loop_again": "increment",
        "finish": "finish"
    }
)

graph.add_edge("finish", END)

app = graph.compile()

# Run it
result = app.invoke({"count": 0, "message": ""})
print("\nFinal state:", result)