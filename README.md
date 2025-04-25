# AI Assistant

A modular AI assistant built to perform non-physical tasks, evolve daily via internet data and user feedback, and remember interactions. It uses a lightweight LLM (Gemma 2 9B), a React frontend, FastAPI backend, Weaviate for memory, and Scrapy for web scraping. Deployable locally or on Render’s free tier.

## Features
- **Core LLM**: Gemma 2 (9B) for local inference; mock for Render.
- **Memory**: Weaviate for conversation history and scraped data (RAG).
- **Continuous Learning**: Scrapy for daily web scraping, TRL for RLHF/fine-tuning.
- **Task Execution**: LangChain for tool integration (e.g., Gmail API stubbed).
- **Frontend**: React with Tailwind CSS, showing task input, responses, feedback, and history.
- **Backend**: FastAPI for API and LLM inference.
- **Deployment**: Local (CPU/GPU) or Render (free tier, mock LLM).

## Prerequisites
- Python 3.9+
- Docker (for Weaviate)
- Git
- Render account (for cloud deployment)
- Hugging Face account (for Gemma 2 weights)

## Project Structure
```
ai-assistant/
├── static/
│   └── index.html        # React frontend
├── spiders/
│   └── news_spider Asc    # Scrapy spider for web scraping
├── main.py              # FastAPI backend
├── finetune.py          # Fine-tuning script
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment config
├── README.md            # This file
```

## Setup and Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-assistant.git
   cd ai-assistant
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install torch datasets
   ```
4. Setup Weaviate and Gemma 2 (see personal_readme.md for details).
5. Run locally:
   ```bash
   python main.py
   ```

## Deployment on Render
1. Push to GitHub.
2. Create a Web Service on Render, connect the repo.
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Usage
- Open `http://localhost:8000` (local) or Render URL.
- Enter tasks (e.g., "Draft an email").
- Provide feedback to improve the model.
- View conversation history.

## Continuous Learning
- **Web Scraping**: Daily news scraping via Scrapy.
- **Memory**: Weaviate stores history and scraped data.
- **RLHF/Fine-Tuning**: Feedback-driven model improvement using TRL.

## Contributing
Pull requests are welcome. Please open an issue to discuss changes.

## License
MIT
