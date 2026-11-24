from sentence_transformers import CrossEncoder

from hybrid import hybrid_search

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model = None


def get_reranker():
    global _model
    if _model is None:
        _model = CrossEncoder(RERANK_MODEL, max_length=512)
    return _model


def rerank_search(query, k=5, pool=20):
    """Get the best `pool` hybrid candidates, then reorder them with a cross-encoder."""
    candidates = hybrid_search(query, k=pool, pool=pool)
    pairs = [(query, c["text"]) for c in candidates]
    scores = get_reranker().predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:k]
    return [{**c, "score": float(s)} for c, s in ranked]