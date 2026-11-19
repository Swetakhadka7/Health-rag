import json
import re
from collections import Counter, defaultdict
from pathlib import Path

IN = Path("data/processed/pages.jsonl")
OUT = Path("data/processed/pages_clean.jsonl")

page_no = re.compile(r"^\d{1,3}$|^[ivxlc]{1,6}$", re.IGNORECASE)
page_label = re.compile(r"^Page \d+$", re.IGNORECASE)


def norm(line):
    return re.sub(r"\s+", " ", line).strip()


def find_repeated_lines(pages_of_one_doc):
    """Lines that appear on more than 30% of a document's pages are headers/footers."""
    counts = Counter()
    for p in pages_of_one_doc:
        for line in set(norm(l) for l in p["text"].splitlines() if norm(l)):
            counts[line] += 1
    limit = 0.3 * len(pages_of_one_doc)
    return {line for line, c in counts.items() if c >= limit}


def clean_page(text, repeated):
    out = []
    for line in text.splitlines():
        n = norm(line)
        if not n or n in repeated:
            continue
        if page_no.match(n) or page_label.match(n):
            continue
        out.append(n)
    return "\n".join(out)


def main():
    pages = [json.loads(line) for line in IN.open(encoding="utf-8")]

    by_doc = defaultdict(list)
    for p in pages:
        by_doc[p["doc"]].append(p)
    repeated = {doc: find_repeated_lines(ps) for doc, ps in by_doc.items()}

    with OUT.open("w", encoding="utf-8") as f:
        for p in pages:
            p["text"] = clean_page(p["text"], repeated[p["doc"]])
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print("Wrote", len(pages), "pages to", OUT)


if __name__ == "__main__":
    main()