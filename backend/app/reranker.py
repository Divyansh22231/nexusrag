from typing import List, Dict
from app.config import settings

_ranker = None

def _get_ranker():
    global _ranker
    if _ranker is None:
        from flashrank import Ranker
        _ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2")
    return _ranker

def rerank_candidates(query: str, candidates: List[Dict]) -> List[Dict]:
    if not candidates:
        return []
        
    from flashrank import RerankRequest
    ranker = _get_ranker()
    passages = []
    for c in candidates:
        passages.append({
            "id": c["chunk_id"],
            "text": c["text"],
            "meta": c["metadata"]
        })
        
    rerankrequest = RerankRequest(query=query, passages=passages)
    results = ranker.rerank(rerankrequest)
    del passages
    del rerankrequest
    
    sorted_results = sorted(
        results,
        key=lambda x: (round(x.get("score", 0.0), 3), -x.get("meta", {}).get("page", 999)),
        reverse=True
    )
    top_results = sorted_results[:settings.RAG_TOP_K]
    
    final_chunks = []
    for r in top_results:
        final_chunks.append({
            "chunk_id": r["id"],
            "text": r["text"],
            "metadata": r["meta"],
            "score": r["score"]
        })
        
    return final_chunks
