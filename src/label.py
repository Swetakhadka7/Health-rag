import json
import sys
from pathlib import Path

QUESTIONS = Path("eval/questions.jsonl")


def main():
    args = sys.argv[1:]
    if len(args) < 3 or len(args) % 2 == 0:
        raise SystemExit("Usage: python src\\label.py q013 who 47 nepal 48")

    qid, pairs = args[0], args[1:]
    questions = [json.loads(l) for l in QUESTIONS.open(encoding="utf-8") if l.strip()]
    docs = sorted({e["doc"] for q in questions for e in q["expected"]})

    target = next((q for q in questions if q["id"] == qid), None)
    if target is None:
        raise SystemExit(f"No question with id {qid}")

    for prefix, page in zip(pairs[::2], pairs[1::2]):
        matches = [d for d in docs if d.startswith(prefix.lower())]
        if len(matches) != 1:
            raise SystemExit(f"'{prefix}' must match exactly one document: {docs}")
        entry = {"doc": matches[0], "page": int(page)}
        if entry in target["expected"]:
            print("already listed:", entry["doc"], entry["page"])
        else:
            target["expected"].append(entry)
            print("added:", entry["doc"], "page", entry["page"])

    with QUESTIONS.open("w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()