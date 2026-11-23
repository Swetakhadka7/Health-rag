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