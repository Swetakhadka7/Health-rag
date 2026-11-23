from bm25_search import keyword_search
from search import search as vector_search


def hybrid_search(query, k=5, pool=20, rrf_k=60):
    """Combine vector and keyword rankings with Reciprocal Rank Fusion (RRF)."""
    scores = {}
    items = {}
    for results in (vector_search(query, k=pool), keyword_search(query, k=pool)):
        for rank, r in enumerate(results, start=1):
            cid = r["chunk_id"]
            scores[cid] = scores.get(cid, 0) + 1 / (rrf_k + rank)
            items[cid] = r
    best = sorted(scores, key=scores.get, reverse=True)[:k]
    return [{**items[cid], "score": scores[cid]} for cid in best]