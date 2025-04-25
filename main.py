from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
from langchain.prompts import PromptTemplate
import os

app = FastAPI()

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# SQLite setup
conn = sqlite3.connect("feedback.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS feedback (task TEXT, response TEXT, feedback TEXT)")
conn.commit()

class TaskRequest(BaseModel):
    task: str

class FeedbackRequest(BaseModel):
    task: str
    response: str
    feedback: str

def mock_grok_api(task: str) -> str:
    prompt = PromptTemplate(
        input_variables=["task"],
        template="You are an AI assistant with full authority to perform non-physical tasks. Execute this task: {task}"
    )
    # Mock response (replace with xAI API: https://x.ai/api)
    return f"Mock response: Executed task - {task}"

@app.post("/api/execute")
async def execute_task(request: TaskRequest):
    result = mock_grok_api(request.task)
    return {"result": result}

@app.post("/api/feedback")
async def store_feedback(request: FeedbackRequest):
    conn.execute(
        "INSERT INTO feedback (task, response, feedback) VALUES (?, ?, ?)",
        (request.task, request.response, request.feedback)
    )
    conn.commit()
    return {"message": "Feedback stored, model will adapt"}