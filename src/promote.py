import json
import sys
from pathlib import Path

DRAFTS = Path("data/processed/drafts.jsonl")
OUT = Path("eval/questions.jsonl")

# Extra pages that also answer a question (I verified these by reading them).
EXTRA = {
    "d001": [("bhutan_2020_dengue_clinical.pdf", 26)],
    "d002": [("maldives_2022_dengue_children.pdf", 4), ("bhutan_2020_dengue_clinical.pdf", 7)],
}


def main():
    wanted = sys.argv[1:]
    drafts = {}
    for line in DRAFTS.open(encoding="utf-8"):
        d = json.loads(line)
        drafts[d["id"]] = d

    existing = []
    needs_newline = False
    if OUT.exists():
        text = OUT.read_text(encoding="utf-8")
        existing = [json.loads(line) for line in text.splitlines() if line.strip()]
        needs_newline = bool(text) and not text.endswith("\n")
    already = {q.get("source") for q in existing}
    next_num = len(existing) + 1

    with OUT.open("a", encoding="utf-8") as f:
        if needs_newline:
            f.write("\n")
        for did in wanted:
            if did not in drafts:
                print("not found:", did)
                continue
            if did in already:
                print("already promoted:", did)
                continue
            d = drafts[did]
            expected = list(d["expected"])
            for doc, page in EXTRA.get(did, []):
                expected.append({"doc": doc, "page": page})
            q = {
                "id": f"q{next_num:03d}",
                "question": d["question"],
                "expected": expected,
                "source": did,
            }
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
            print(f"{q['id']}  ({len(expected)} pages)  {q['question']}")
            next_num += 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()