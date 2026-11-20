import sys

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

DB_URL = "postgresql://rag:rag@localhost:5433/healthrag"
TABLE = "chunks_fixed"
MODEL = "BAAI/bge-small-en-v1.5"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL)
    return _model


def search(query, k=5):
    vec = get_model().encode(query, normalize_embeddings=True)
    with psycopg.connect(DB_URL) as conn:
        register_vector(conn)
        rows = conn.execute(
            f"""
            SELECT chunk_id, doc, page, text, 1 - (embedding <=> %s) AS score
            FROM {TABLE}
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (vec, vec, k),
        ).fetchall()
    return [
        {"chunk_id": r[0], "doc": r[1], "page": r[2], "text": r[3], "score": float(r[4])}
        for r in rows
    ]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # avoids Windows errors on symbols like ≥
    query = " ".join(sys.argv[1:]) or "What are the warning signs of severe dengue?"
    for i, r in enumerate(search(query), start=1):
        print(f"\n#{i}  score={r['score']:.3f}  {r['doc']}  page {r['page']}")
        print(r["text"][:300].replace("\n", " "))