import os
import re
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from rerank import rerank_search

REFUSAL = "I can't answer this from the documents I have."

PROMPT = """You answer questions about dengue using ONLY the numbered passages below.

Rules:
1. Use only information in the passages. Do not use outside knowledge.
2. After each statement, cite the passage number(s) it came from, like [1] or [2][3].
3. Name the source document for each statement, for example "According to the Bhutan guideline ...". Do not present one document's guidance as universal.
4. If passages from different documents disagree, say so and cite each one.
5. If the passages do not contain the answer, reply with exactly: {refusal}
6. Keep the answer under 150 words. Do not give personal medical advice.

Passages:
{passages}

Question: {question}
"""


def build_passages(chunks):
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(f"[{i}] (source: {c['doc']}, page {c['page']})\n{c['text']}")
    return "\n\n".join(parts)


def ask_llm(prompt, tries=4):
    load_dotenv()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.environ["GEMINI_MODEL"]
    wait = 5
    for attempt in range(1, tries + 1):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.0),
            )
            return resp.text.strip()
        except Exception as e:
            print(f"(attempt {attempt}/{tries} failed: {str(e)[:70]})")
            if attempt == tries:
                return None
            time.sleep(wait)
            wait *= 2


def answer(question, k=8):
    chunks = rerank_search(question, k=k)
    prompt = PROMPT.format(
        refusal=REFUSAL, passages=build_passages(chunks), question=question
    )
    text = ask_llm(prompt)
    if text is None:
        return None, [], chunks
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 1 <= int(n) <= len(chunks)})
    return text, [chunks[n - 1] | {"n": n} for n in cited], chunks


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    question = " ".join(sys.argv[1:]) or "Can I give ibuprofen to a child with dengue fever?"
    text, sources, chunks = answer(question)

    print("\nQUESTION:", question)
    if text is None:
        print("\nThe language model is unavailable right now. Try again in a few minutes.")
    else:
        print("\nANSWER:\n" + text)
        if sources:
            print("\nSOURCES:")
            for s in sources:
                print(f"  [{s['n']}] {s['doc']}, page {s['page']}")
        elif REFUSAL not in text:
            print("\nWARNING: the answer has no citations, so do not trust it.")