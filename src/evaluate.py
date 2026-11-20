import json
from pathlib import Path

from search import search

QUESTIONS = Path("eval/questions.jsonl")
K = 5


def main():
    questions = [json.loads(line) for line in QUESTIONS.open(encoding="utf-8")]
    recalls, hits = [], []

    for q in questions:
        results = search(q["question"], k=K)
        found = {(r["doc"], r["page"]) for r in results}
        expected = {(e["doc"], e["page"]) for e in q["expected"]}
        matched = expected & found

        recall = len(matched) / len(expected)
        recalls.append(recall)
        hits.append(1 if matched else 0)

        print(f"{q['id']}  recall@{K}={recall:.2f}  {q['question']}")
        for doc, page in sorted(expected - found):
            print(f"      missed: {doc} page {page}")

    n = len(questions)
    print()
    print(f"Questions: {n}")
    print(f"Mean recall@{K}: {sum(recalls) / n:.2f}")
    print(f"Hit rate@{K} (at least one right page): {sum(hits) / n:.2f}")


if __name__ == "__main__":
    main()