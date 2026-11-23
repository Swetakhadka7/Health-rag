# Retrieval results

Chunking: fixed 1000 chars / 200 overlap. Embeddings: bge-small-en-v1.5. Search: vector only, top 5.

| Experiment | Questions | Mean recall@5 | Hit rate@5 |
|---|---|---|---|
| Baseline | 9 | 0.61 | 0.78 |

| Experiment | Questions | Mean recall@5 | Hit rate@5 |
|---|---|---|---|
| Baseline | 9 | 0.61 | 0.78 |
| + bge query prefix | 9 | 0.61 | 0.78 |

| Experiment | Questions | Mean recall@5 | Hit rate@5 |
|---|---|---|---|
| Baseline (vector only) | 9 | 0.61 | 0.78 |
| + bge query prefix | 9 | 0.61 | 0.78 |
| Keyword only (BM25) | 9 | 0.69 | 0.89 |

| Hybrid (vector + BM25, RRF) | 9 | 0.66 | 0.89 |

# Retrieval results

Chunking: fixed 1000 chars / 200 overlap. Embeddings: bge-small-en-v1.5. Top 5 results per question.

## Evaluation set v1 (9 questions; 7 drafted from the answer text)

| Experiment | Mean recall@5 | Hit rate@5 |
|---|---|---|
| Vector only (baseline) | 0.61 | 0.78 |
| + bge query prefix | 0.61 | 0.78 |
| Keyword only (BM25) | 0.69 | 0.89 |
| Hybrid (vector + BM25, RRF) | 0.66 | 0.89 |

## Evaluation set v2 (19 questions; 10 written independently of the search)

| Experiment | Mean recall@5 | Hit rate@5 |
|---|---|---|
| Vector only (with query prefix) | 0.52 | 0.84 |
| Keyword only (BM25) | 0.55 | 0.89 |
| Hybrid (vector + BM25, RRF) | 0.59 | 0.89 |

## Evaluation set v2 (19 questions; 10 written independently of the search; q013 labels corrected)

| Experiment | Mean recall@5 | Hit rate@5 |
|---|---|---|
| Vector only (with query prefix) | 0.53 | 0.89 |
| Keyword only (BM25) | 0.55 | 0.89 |
| Hybrid (vector + BM25, RRF) | 0.60 | 0.95 |

## Notes

- Small sample: differences of a few hundredths are within noise.
- q013 (admission criteria) scores 0.00 for every method.
- v1 questions q005 to q009 were drafted from the answer text, so they are easier than the others.
- After fixing q013's labels, only vector and hybrid changed (they had found the added pages). Labels have not been re-reviewed for the other 18 questions.