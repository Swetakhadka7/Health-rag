import json
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

DB_URL = "postgresql://rag:rag@localhost:5433/healthrag"
IN = Path("data/processed/chunks_fixed.jsonl")
TABLE = "chunks_fixed"
MODEL = "BAAI/bge-small-en-v1.5"


def main():
    chunks = [json.loads(line) for line in IN.open(encoding="utf-8")]
    print("Chunks loaded:", len(chunks))

    model = SentenceTransformer(MODEL)
    vectors = model.encode(
        [c["text"] for c in chunks],
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    with psycopg.connect(DB_URL, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)
        conn.execute(f"DROP TABLE IF EXISTS {TABLE}")
        conn.execute(
            f"""
            CREATE TABLE {TABLE} (
                id SERIAL PRIMARY KEY,
                chunk_id TEXT UNIQUE,
                doc TEXT,
                page INT,
                text TEXT,
                embedding vector(384)
            )
            """
        )
        rows = [
            (c["chunk_id"], c["doc"], c["page"], c["text"], v)
            for c, v in zip(chunks, vectors)
        ]
        with conn.cursor() as cur:
            cur.executemany(
                f"INSERT INTO {TABLE} (chunk_id, doc, page, text, embedding) "
                "VALUES (%s, %s, %s, %s, %s)",
                rows,
            )
        count = conn.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]

    print("Rows in database:", count)


if __name__ == "__main__":
    main()