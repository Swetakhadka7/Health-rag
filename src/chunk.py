import json
from pathlib import Path

IN = Path("data/processed/pages_clean.jsonl")
OUT = Path("data/processed/chunks_fixed.jsonl")

CHUNK_SIZE = 1000   # characters per chunk
OVERLAP = 200       # characters repeated from the previous chunk
MIN_CHARS = 100     # drop tiny chunks


def mostly_english(text):
    """False for pages written mostly in another script (e.g. the Dhivehi page)."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    ascii_letters = sum(1 for c in letters if c.isascii())
    return ascii_letters / len(letters) > 0.8


def split_text(text):
    chunks, start = [], 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            # try to end on a sentence or line break, not mid-word
            cut = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
            if cut > start + CHUNK_SIZE // 2:
                end = cut + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - OVERLAP
    return chunks


def main():
    pages = [json.loads(line) for line in IN.open(encoding="utf-8")]
    count = skipped = 0
    with OUT.open("w", encoding="utf-8") as f:
        for p in pages:
            if not mostly_english(p["text"]):
                skipped += 1
                continue
            for i, text in enumerate(split_text(p["text"])):
                if len(text) < MIN_CHARS:
                    continue
                record = {
                    "chunk_id": f"{p['doc']}|p{p['page']}|c{i}",
                    "doc": p["doc"],
                    "page": p["page"],
                    "text": text,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
    print(f"Pages skipped (not English): {skipped}")
    print(f"Chunks written: {count} -> {OUT}")


if __name__ == "__main__":
    main()