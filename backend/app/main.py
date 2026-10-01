from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import ChatRequest, UploadResponse
from app.pdf import extract_text_from_pdf
from app.chunking import chunk_document
from app.vector_store import add_chunks, clear_collection
from app.retrieval import retrieve_context
from app.reranker import rerank_candidates
from app.llm import generate_rag_response
import uuid
import gc

app = FastAPI(title="NexusRAG Backend")

origins = [settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    try:
        pages = extract_text_from_pdf(content)
    finally:
        del content
        await file.close()
    
    document_id = str(uuid.uuid4())
    try:
        chunks = chunk_document(document_id, file.filename, pages)
    finally:
        del pages
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")

    clear_collection()
    try:
        add_chunks(chunks)
    finally:
        del chunks
        gc.collect()
    
    return UploadResponse(document_id=document_id, message="Document processed and indexed.")

@app.post("/chat")
async def chat(request: ChatRequest):
    candidates = retrieve_context(request.message)
    
    if settings.RERANKING_ENABLED and candidates:
        top_context = rerank_candidates(request.message, candidates)
    else:
        top_context = candidates[:settings.RAG_TOP_K]
        
    return StreamingResponse(
        generate_rag_response(request.message, top_context),
        media_type="text/event-stream"
    )
