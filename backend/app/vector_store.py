import chromadb
from typing import List, Dict
from app.config import settings
from app.embeddings import get_embeddings

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
    return _client

def _get_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks(chunks: List[Dict], batch_size: int = 16):
    if not chunks:
        return
    
    collection = _get_collection()
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        embeddings = get_embeddings(texts)
        ids = [c["chunk_id"] for c in batch]
        metadatas = [c.get("metadata", {
            "document_id": c.get("document_id", ""),
            "filename": c.get("filename", ""),
            "page": c.get("page", 0)
        }) for c in batch]
        
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=texts
            )
        finally:
            del texts
            del embeddings
            del ids
            del metadatas
            del batch

def clear_collection():
    client = _get_client()
    try:
        client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
    except Exception:
        pass

def search(query_text: str, k: int, where: Dict = None, where_document: Dict = None) -> List[Dict]:
    collection = _get_collection()
    query_embedding = get_embeddings([query_text])[0]
    
    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": k,
        "include": ["documents", "metadatas", "distances"]
    }
    if where:
        kwargs["where"] = where
    if where_document:
        kwargs["where_document"] = where_document
        
    results = collection.query(**kwargs)
    
    if not results["ids"] or not results["ids"][0]:
        return []
        
    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })
    return chunks
