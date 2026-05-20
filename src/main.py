from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from src.graph.workflow import sprint_graph
from dotenv import load_dotenv


app = FastAPI(title="Sprint Analyzer AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# In-memory chat history — persists for the session
chat_history: List[dict] = []


class QueryRequest(BaseModel):
    query: str


@app.post("/analyze")
async def analyze(req: QueryRequest):
    global chat_history

    # Add user message to history
    chat_history.append({
        "role": "user",
        "content": req.query
    })

    # Build initial state
    initial_state = {
        "user_query": req.query,
        "chat_history": chat_history.copy(),
        "sprint_data": {},
        "agents_to_run": [],
        "todo_output": None,
        "health_output": None,
        "blocker_output": None,
        "recommendation_output": None,
        "create_output": None,
        "final_answer": "",
    }

    # Run the graph
    result = sprint_graph.invoke(initial_state)

    # Add assistant response to history
    chat_history.append({
        "role": "assistant",
        "content": result["final_answer"]
    })

    # Keep history from growing too large
    # Keep only last 6 messages instead of 20
    if len(chat_history) > 6:
        chat_history = chat_history[-6:]
    return {
        "answer": result["final_answer"],
        "agents_used": result["agents_to_run"],
        "sprint_name": result["sprint_data"]["meta"]["sprint_name"],
    }


@app.get("/sprint-meta")
async def sprint_meta():
    from src.data.mock_jira import get_sprint_data
    return get_sprint_data()["meta"]


@app.post("/reset")
async def reset_chat():
    global chat_history
    chat_history = []
    return {"status": "Chat history cleared"}