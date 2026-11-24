import json
import sys
from pathlib import Path

QUESTIONS = Path("eval/questions.jsonl")
K = 5


def get_search(method):
    if method == "vector":
        from search import search
        return search
    if method == "keyword":
        from bm25_search import keyword_search
        return keyword_search
    if method == "hybrid":
        from hybrid import hybrid_search
        return hybrid_search
    if method == "rerank":
        from rerank import rerank_search
        return rerank_search
    raise SystemExit("Method must be: vector, keyword, rerank, or hybrid")


def main():
    method = sys.argv[1] if len(sys.argv) > 1 else "vector"
    run_search = get_search(method)
    print("Method:", method)

    questions = [json.loads(line) for line in QUESTIONS.open(encoding="utf-8")]
    recalls, hits = [], []

    for q in questions:
        results = run_search(q["question"], k=K)
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



