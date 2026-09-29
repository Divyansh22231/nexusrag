from typing import List

_model = None

def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _model

def get_embeddings(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    return [e.tolist() for e in model.embed(texts)]

