import answer

CHUNKS = [
    {"doc": "a.pdf", "page": 1, "text": "Paracetamol maximum is 4 g per day."},
    {"doc": "b.pdf", "page": 2, "text": "Avoid NSAIDs such as ibuprofen."},
]


def run(monkeypatch, reply):
    monkeypatch.setattr(answer, "rerank_search", lambda q, k=8: CHUNKS)
    monkeypatch.setattr(answer, "ask_llm", lambda prompt: reply)
    return answer.answer("some question?")


def test_cited_answer_is_kept_with_its_sources(monkeypatch):
    text, sources, _ = run(monkeypatch, "Avoid NSAIDs [2].")
    assert text == "Avoid NSAIDs [2]."
    assert [(s["n"], s["doc"], s["page"]) for s in sources] == [(2, "b.pdf", 2)]


def test_answer_without_citation_becomes_refusal(monkeypatch):
    text, sources, _ = run(monkeypatch, "Why did the mosquito cross the road?")
    assert text == answer.REFUSAL
    assert sources == []


def test_refusal_passes_through(monkeypatch):
    text, sources, _ = run(monkeypatch, answer.REFUSAL)
    assert text == answer.REFUSAL
    assert sources == []


def test_citation_to_a_nonexistent_passage_does_not_count(monkeypatch):
    text, sources, _ = run(monkeypatch, "Something made up [9].")
    assert text == answer.REFUSAL
    assert sources == []


def test_language_model_failure_returns_none(monkeypatch):
    text, sources, _ = run(monkeypatch, None)
    assert text is None
    assert sources == []


def test_prompt_numbers_passages_and_wraps_the_question(monkeypatch):
    seen = {}
    monkeypatch.setattr(answer, "rerank_search", lambda q, k=8: CHUNKS)
    monkeypatch.setattr(answer, "ask_llm", lambda prompt: seen.setdefault("p", prompt) and "x [1]")
    answer.answer("Is it safe?")
    prompt = seen["p"]
    assert "[1] (source: a.pdf, page 1)" in prompt
    assert "[2] (source: b.pdf, page 2)" in prompt
    assert "<question>\nIs it safe?\n</question>" in prompt
    assert answer.REFUSAL in prompt