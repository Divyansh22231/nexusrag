from typing import List, Dict
import re
from app.config import settings
from app.vector_store import search
from app.chunking import normalize_q_id

def retrieve_context(query: str) -> List[Dict]:
    query_norm = re.sub(r'\s+', ' ', query).strip()
    q_id = normalize_q_id(query_norm)
    
    if q_id:
        exact_candidates = search(query_norm, k=settings.RAG_CANDIDATE_K, where={"question_id": q_id})
        if exact_candidates:
            for c in exact_candidates:
                c["score"] = 1.0
            return exact_candidates
            
    candidates = search(query_norm, k=settings.RAG_CANDIDATE_K)
    filtered = []
    for c in candidates:
        similarity = 1.0 - c["distance"]
        if similarity >= settings.RAG_SCORE_THRESHOLD:
            c["score"] = similarity
            filtered.append(c)
            
    if filtered:
        filtered.sort(key=lambda x: x["score"], reverse=True)
        return filtered
        
    words = [w for w in query_norm.split() if len(w) > 3]
    if words:
        longest_word = max(words, key=len)
        fallback_candidates = search(query_norm, k=settings.RAG_CANDIDATE_K, where_document={"$contains": longest_word})
        if fallback_candidates:
            for c in fallback_candidates:
                c["score"] = 0.5
            return fallback_candidates
            
    return []
