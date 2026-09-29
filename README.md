# NexusRAG

A simple, production-oriented Retrieval-Augmented Generation (RAG) chatbot designed to be easy to understand and explain in a software engineering interview.

## Architecture

Streamlit Frontend <-> HTTPS <-> FastAPI Backend (Docker/Render) <-> RAG Pipeline <-> Gemini API

## RAG Pipeline
1. **PDF Processing:** PyMuPDF extracts text preserving page numbers.
2. **Chunking:** Text is split into page-aware chunks.
3. **Embeddings:** FastEmbed generates local embeddings (BAAI/bge-small-en-v1.5).
4. **Vector Store:** ChromaDB stores chunks and embeddings persistently.
5. **Retrieval:** Semantic search against ChromaDB using cosine distance.
6. **Reranking:** FlashRank reranks candidates to select the top context.
7. **Generation:** Gemini API answers using grounded prompts with streaming (SSE).

## Tech Stack
- Frontend: Python, Streamlit
- Backend: Python 3.11, FastAPI, PyMuPDF, FastEmbed, ChromaDB, FlashRank, httpx
- LLM: Google Gemini API (Streaming)
- Deployment: Docker, Render

## Project Structure
- `backend/`: FastAPI application, tests, and backend Dockerfile.
- `frontend/`: Streamlit application and frontend Dockerfile.
- `docker-compose.yml`: Local development setup.

## Local Setup

### 1. Environment Variables
Create `.env` in `backend/` based on `backend/.env.example`.
Create `.env` in `frontend/` based on `frontend/.env.example`.

Provide your Gemini API key in `backend/.env`.

### 2. Running with Docker Compose
```bash
docker-compose up --build
```
- Frontend: `http://localhost:8502`
- Backend: `http://localhost:8001`

### 3. Running Locally (without Docker)
Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## GitHub & Render Deployment

### 1. Push to GitHub
Make sure secrets are never committed (`backend/.env` is strictly ignored by `.gitignore`).
```bash
git add .
git commit -m "Production release of NexusRAG"
git push origin main
```

### 2. Deploy Backend on Render (Docker Web Service)
1. On the Render Dashboard, select **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Runtime**: Docker
   - **Root Directory**: `backend` (or set Dockerfile Path to `./backend/Dockerfile`)
   - **Instance Type**: Minimum 1GB RAM recommended for FastEmbed & FlashRank in-memory models.
4. Set Environment Variables:
   - `GEMINI_API_KEY`: Your Gemini API key (Required)
   - `GEMINI_MODEL`: `gemini-3.5-flash-lite` (Default)
   - `FRONTEND_ORIGIN`: `*` (or your deployed frontend URL)
   - `CHROMA_PERSIST_DIRECTORY`: `/app/data/chroma`
5. Persistent Storage:
   - Add a Render Persistent Disk mounted at `/app/data/chroma` (e.g. 1GB–5GB) to ensure vector embeddings persist across container restarts.
6. Port Binding:
   - Render automatically injects the `PORT` environment variable. The backend Dockerfile binds to `--port ${PORT:-8000}` automatically.

### 3. Deploy Frontend (Render or Streamlit Community Cloud)
- **On Render**: Deploy as a Docker Web Service using `./frontend/Dockerfile`, and configure:
  - `BACKEND_URL`: `https://your-backend-service.onrender.com`
- **On Streamlit Community Cloud**: Select your repository, set the path to `frontend/app.py`, and configure `BACKEND_URL` under Settings -> Secrets.

## Testing
Run backend tests:
```bash
cd backend
pytest tests/
```

## Known Limitations
- Supports one active document at a time to prevent cross-contamination.
- Local embeddings and reranking happen in-memory and require adequate RAM depending on document size.

## Interview Explanation
Streamlit is the frontend. It sends the PDF and questions to a FastAPI backend. The backend extracts text from the PDF using PyMuPDF, creates page-aware chunks, generates local embeddings using FastEmbed, and stores them in ChromaDB. When the user asks a question, the backend embeds the question, retrieves the most similar chunks from ChromaDB, reranks them using FlashRank, and sends the best context to Gemini with a grounded prompt. Gemini streams the answer back through FastAPI using SSE, and Streamlit displays the response.
