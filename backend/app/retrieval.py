from typing import List, Dict
from app.config import settings
from app.vector_store import search

def retrieve_context(query: str) -> List[Dict]:
    candidates = search(query, k=settings.RAG_CANDIDATE_K)
    filtered = []
    for c in candidates:
        similarity = 1.0 - c["distance"]
        if similarity >= settings.RAG_SCORE_THRESHOLD:
            c["score"] = similarity
            filtered.append(c)
    filtered.sort(key=lambda x: x["score"], reverse=True)
    return filtered
