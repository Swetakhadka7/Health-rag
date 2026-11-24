import os
import secrets
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from answer import REFUSAL, answer
from rerank import rerank_search

load_dotenv()

RATE_LIMIT = 2   # requests allowed ...
RATE_WINDOW = 60  # ... per this many seconds, per API key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_hits = defaultdict(deque)
_lock = threading.Lock()


def check_access(key: str = Security(api_key_header)):
    """Reject missing/wrong API keys (401), then limit requests per key (429)."""
    expected = os.environ.get("API_KEY", "")
    if not key or not expected or not secrets.compare_digest(key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Missing or invalid API key.")

    now = time.monotonic()
    with _lock:
        recent = _hits[key]
        while recent and now - recent[0] > RATE_WINDOW:
            recent.popleft()
        if len(recent) >= RATE_LIMIT:
            wait = int(RATE_WINDOW - (now - recent[0])) + 1
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please slow down.",
                headers={"Retry-After": str(wait)},
            )
        recent.append(now)


@asynccontextmanager
async def lifespan(app):
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY is not set. Add a line API_KEY=... to your .env file.")
    # Load the search models and check the database once, at startup,
    # so the first real request is not slow.
    try:
        rerank_search("dengue", k=1)
        print("Startup check passed: models loaded, database reachable.")
    except Exception as e:
        print("WARNING: startup check failed:", e)
    yield


app = FastAPI(title="Dengue guidelines Q&A", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Source(BaseModel):
    n: int
    doc: str
    page: int


class AskResponse(BaseModel):
    answer: str
    refused: bool
    sources: list[Source]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse, dependencies=[Depends(check_access)])
def ask(req: AskRequest):
    text, sources, _ = answer(req.question.strip())
    if text is None:
        raise HTTPException(
            status_code=503,
            detail="The language model is unavailable right now. Please try again shortly.",
        )
    return {
        "answer": text,
        "refused": REFUSAL in text,
        "sources": [{"n": s["n"], "doc": s["doc"], "page": s["page"]} for s in sources],
    }