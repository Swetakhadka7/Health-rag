import json
import re
from pathlib import Path

from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi

CHUNKS = Path("data/processed/chunks_fixed.jsonl")

STOPWORDS = set(
    "a an and are as at be by can do does for from how in is it of on or the to "
    "what when where which who why with should would could may might will than that "
    "this these those there their they into during about after before over under "
    "if not no any all each per used use using".split()
)
_stem = PorterStemmer().stem
_index = None


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [_stem(w) for w in words if w not in STOPWORDS and len(w) > 1]


def _load():
    global _index
    if _index is None:
        chunks = [json.loads(line) for line in CHUNKS.open(encoding="utf-8")]
        bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])
        _index = (chunks, bm25)
    return _index


def keyword_search(query, k=5):
    chunks, bm25 = _load()
    scores = bm25.get_scores(tokenize(query))
    order = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)[:k]
    return [
        {
            "chunk_id": chunks[i]["chunk_id"],
            "doc": chunks[i]["doc"],
            "page": chunks[i]["page"],
            "text": chunks[i]["text"],
            "score": float(scores[i]),
        }
        for i in order
    ]