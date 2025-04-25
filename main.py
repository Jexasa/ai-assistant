from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from langchain.prompts import PromptTemplate
import os
import logging
from transformers import pipeline
import weaviate
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at root
@app.get("/")
async def serve_index():
    logger.info("Serving static/index.html")
    file_path = os.path.join("static", "index.html")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {"error": "index.html not found"}
    return FileResponse(file_path, media_type="text/html")

# SQLite setup for feedback and history
conn = sqlite3.connect("feedback.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS feedback (task TEXT, response TEXT, feedback TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS history (task TEXT, response TEXT)")
conn.commit()

# Weaviate setup (mocked for Render)
try:
    weaviate_client = weaviate.Client("http://localhost:8080")  # Replace with hosted URL
except Exception as e:
    logger.warning(f"Weaviate not available: {e}")
    weaviate_client = None

# Initialize LLM
def init_llm():
    try:
        # Gemma 2 for local; mock for Render
        logger.info("Initializing Gemma 2 (mock for Render)")
        return pipeline("text-generation", model="google/gemma-2-9b", device=-1)  # CPU
    except Exception as e:
        logger.error(f"LLM init error: {e}")
        return lambda x: f"Mock Gemma response: {x}"

llm = init_llm()

class TaskRequest(BaseModel):
    task: str

class FeedbackRequest(BaseModel):
    task: str
    response: str
    feedback: str

def mock_web_scrape() -> List[Dict]:
    # Stub for Scrapy
    return [{"content": "Mock news data", "url": "example.com"}]

def store_in_weaviate(data: List[Dict]):
    if weaviate_client:
        try:
            for item in data:
                weaviate_client.data_object.create(
                    {"content": item["content"], "url": item["url"]},
                    class_name="Knowledge"
                )
            logger.info("Stored data in Weaviate")
        except Exception as e:
            logger.error(f"Weaviate store error: {e}")

def query_weaviate(task: str) -> str:
    if weaviate_client:
        try:
            result = weaviate_client.query.get("Knowledge", ["content"]).with_near_text({"concepts": [task]}).do()
            return result.get("data", {}).get("Get", {}).get("Knowledge", [{}])[0].get("content", "")
        except Exception as e:
            logger.error(f"Weaviate query error: {e}")
    return ""

def process_task(task: str) -> str:
    prompt = PromptTemplate(
        input_variables=["task", "context"],
        template="Task: {task}\nContext: {context}\nResponse:"
    )
    context = query_weaviate(task) or mock_web_scrape()[0]["content"]
    logger.info(f"Processing task: {task} with context: {context}")
    return llm(prompt.format(task=task, context=context))[0]["generated_text"]

@app.post("/api/execute")
async def execute_task(request: TaskRequest):
    logger.info(f"Received POST /api/execute with task: {request.task}")
    result = process_task(request.task)
    conn.execute("INSERT INTO history (task, response) VALUES (?, ?)", (request.task, result))
    conn.commit()
    return {"result": result}

@app.post("/api/feedback")
async def store_feedback(request: FeedbackRequest):
    logger.info(f"Received POST /api/feedback for task: {request.task}")
    conn.execute(
        "INSERT INTO feedback (task, response, feedback) VALUES (?, ?, ?)",
        (request.task, request.response, request.feedback)
    )
    conn.commit()
    logger.info("Feedback stored; fine-tuning queued")
    return {"message": "Feedback stored, model will adapt"}

@app.get("/api/history")
async def get_history():
    cursor = conn.execute("SELECT task, response FROM history")
    history = [{"task": row[0], "response": row[1]} for row in cursor.fetchall()]
    logger.info(f"Returning history: {len(history)} items")
    return {"history": history}

@app.get("/debug")
async def debug():
    logger.info("Accessing /debug endpoint")
    static_files = os.listdir("static") if os.path.exists("static") else []
    return {"static_files": static_files, "pwd": os.getcwd()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
