# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agents.graph import build_graph

load_dotenv()

app = FastAPI(
    title="Multi-Agent Coding Assistant",
    description="LangGraph multi-agent system that writes, reviews, and tests code.",
    version="1.0.0"
)

class RunRequest(BaseModel):
    task: str

class RunResponse(BaseModel):
    code:         str
    review:       str
    test_results: str
    iterations:   int
    messages:     list

@app.get("/")
def root():
    return {"status": "running", "message": "Multi-Agent Coding Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run", response_model=RunResponse)
def run_pipeline(request: RunRequest):
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")
    try:
        graph  = build_graph()
        result = graph.invoke({
            "task":         request.task,
            "code":         "",
            "review":       "",
            "review_json":  {},
            "tests":        "",
            "test_results": "",
            "iterations":   0,
            "messages":     []
        })
        return RunResponse(
            code=         result.get("code",         ""),
            review=       result.get("review",       ""),
            test_results= result.get("test_results", ""),
            iterations=   result.get("iterations",   0),
            messages=     result.get("messages",     [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")