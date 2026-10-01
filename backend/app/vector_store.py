import chromadb
from typing import List, Dict
from app.config import settings
from app.embeddings import get_embeddings

def _get_collection():
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks(chunks: List[Dict]):
    if not chunks:
        return
    
    collection = _get_collection()
    texts = [c["text"] for c in chunks]
    embeddings = get_embeddings(texts)
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [c.get("metadata", {
        "document_id": c.get("document_id", ""),
        "filename": c.get("filename", ""),
        "page": c.get("page", 0)
    }) for c in chunks]
    
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

def clear_collection():
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
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
