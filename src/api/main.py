from fastapi import FastAPI
from pydantic import BaseModel
from src.graphs.dev_agent_graph import build_graph

app = FastAPI()
graph_app = build_graph()


class FixBugRequest(BaseModel):
    thread_id: str
    issue_description: str
    owner: str
    repo: str
    branch: str


class ApproveRequest(BaseModel):
    thread_id: str
    approved: bool


@app.post("/fix-bug")
async def fix_bug(request: FixBugRequest):
    """
    Starts the pipeline: plan -> implement -> test -> (retry if needed).
    Blocks until it either succeeds and pauses for review, or gives up.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    
    initial_state = {
        "issue_description": request.issue_description,
        "owner": request.owner,
        "repo": request.repo,
        "branch": request.branch,
        "plan": {}, "original_code": "", "current_code": "", "current_test": "",
        "test_result": {}, "iteration_count": 0, "max_iterations": 3,
        "status": "starting", "pr_url": ""
    }
    
    result = await graph_app.ainvoke(initial_state, config=config)
    
    state_snapshot = await graph_app.aget_state(config)
    awaiting_review = bool(state_snapshot.next)
    
    return {
        "thread_id": request.thread_id,
        "awaiting_review": awaiting_review,
        "plan": result.get("plan"),
        "proposed_code": result.get("current_code"),
        "test_code": result.get("current_test"),
        "test_passed": result.get("test_result", {}).get("success"),
        "iterations_used": result.get("iteration_count"),
        "status": result.get("status")
    }


@app.post("/approve")
async def approve(request: ApproveRequest):
    """
    Resumes a paused pipeline run. If approved, creates the real PR.
    If rejected, just confirms the run is stopped.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    
    if not request.approved:
        return {"thread_id": request.thread_id, "status": "rejected", "pr_url": None}
    
    final = await graph_app.ainvoke(None, config=config)
    
    return {
        "thread_id": request.thread_id,
        "status": "approved",
        "pr_url": final.get("pr_url")
    }