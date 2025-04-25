from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
from langchain.prompts import PromptTemplate
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files and serve index.html at root
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    logger.info("Serving index.html")
    return FileResponse("static/index.html")

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
    logger.info(f"Processing task: {task}")
    # Mock response (replace with xAI API: https://x.ai/api)
    return f"Mock response: Executed task - {task}"

@app.post("/api/execute")
async def execute_task(request: TaskRequest):
    logger.info(f"Received POST /api/execute with task: {request.task}")
    result = mock_grok_api(request.task)
    return {"result": result}

@app.post("/api/feedback")
async def store_feedback(request: FeedbackRequest):
    logger.info(f"Received POST /api/feedback for task: {request.task}")
    conn.execute(
        "INSERT INTO feedback (task, response, feedback) VALUES (?, ?, ?)",
        (request.task, request.response, request.feedback)
    )
    conn.commit()
    return {"message": "Feedback stored, model will adapt"}

@app.get("/debug")
async def debug():
    logger.info("Accessing /debug endpoint")
    return {"static_files": os.listdir("static"), "pwd": os.getcwd()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
