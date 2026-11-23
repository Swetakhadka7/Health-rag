import json
import os
import random
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

CHUNKS = Path("data/processed/chunks_fixed.jsonl")
OUT = Path("data/processed/drafts.jsonl")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10

PROMPT = """You are helping build a test set for a dengue question-answering system.
Read the passage below and write ONE question that a nurse or doctor might ask,
which this passage clearly answers.
Rules:
- Do not mention "the passage", "the document" or any document name.
- Use natural wording; do not copy long phrases from the passage.
- Return only the question, nothing else.

Passage:
{text}
"""


def usable(chunk):
    text = chunk["text"]
    if len(text) < 500:
        return False
    if re.search(r"\.{5,}", text):  # table-of-contents lines
        return False
    letters = sum(c.isalpha() for c in text)
    return letters / len(text) > 0.7


def ask_with_retry(client, model, prompt, tries=5):
    """Retry on temporary server errors (503, 429), waiting longer each time."""
    wait = 5
    for attempt in range(1, tries + 1):
        try:
            return client.models.generate_content(model=model, contents=prompt).text.strip()
        except Exception as e:
            print(f"      attempt {attempt}/{tries} failed: {str(e)[:80]}")
            if attempt == tries:
                return None
            time.sleep(wait)
            wait *= 2


def main():
    load_dotenv()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.environ["GEMINI_MODEL"]

    # resume: remember which chunks already have a draft
    done = []
    if OUT.exists():
        done = [json.loads(line) for line in OUT.open(encoding="utf-8")]
    used = {d["chunk_id"] for d in done if "chunk_id" in d}

    chunks = [json.loads(line) for line in CHUNKS.open(encoding="utf-8")]
    chunks = [c for c in chunks if usable(c) and c["chunk_id"] not in used]
    random.seed(42)
    sample = random.sample(chunks, N)

    with OUT.open("a", encoding="utf-8") as f:
        for c in sample:
            question = ask_with_retry(client, model, PROMPT.format(text=c["text"]))
            if question is None:
                print("Giving up on one chunk, moving on.")
                continue
            done.append({})
            record = {
                "id": f"d{len(done):03d}",
                "chunk_id": c["chunk_id"],
                "question": question,
                "expected": [{"doc": c["doc"], "page": c["page"]}],
                "snippet": c["text"][:250].replace("\n", " "),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{record['id']}  {question}")
            print(f"      from {c['doc']} page {c['page']}")
            time.sleep(4)  # stay under free-tier rate limits

    print("\nDone. Drafts so far:", len(done), "->", OUT)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()