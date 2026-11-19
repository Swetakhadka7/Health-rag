import json
from pathlib import Path

import pymupdf

RAW = Path("data/raw")
OUT = Path("data/processed/pages.jsonl")

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8") as f:
    for pdf in sorted(RAW.glob("*.pdf")):
        doc = pymupdf.open(pdf)
        kept = 0
        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if len(text) < 50:
                continue
            record = {"doc": pdf.name, "page": i, "text": text}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            kept += 1
        print(pdf.name, "->", kept, "pages")