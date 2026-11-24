from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from answer import REFUSAL, answer
from rerank import rerank_search


@asynccontextmanager
async def lifespan(app):
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


@app.post("/ask", response_model=AskResponse)
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