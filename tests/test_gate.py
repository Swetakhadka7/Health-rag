import pytest

import gate

BASE = {"method": "rerank", "mean_recall": 0.61, "hit_rate": 1.00}
ANS = {"answerable_min": 9, "refuse_min": 4}

RETRIEVAL_OUTPUT = """Method: rerank
q001  recall@5=0.67  How much paracetamol can an adult take per day?

Questions: 19
Mean recall@5: 0.61
Hit rate@5 (at least one right page): 1.00
"""

ANSWER_OUTPUT = """PASS  [answer]  How much paracetamol can an adult take per day?

Answerable questions passed: 10/10
Should-refuse questions passed: 4/4
"""


def test_parses_retrieval_summary():
    assert gate.parse_retrieval(RETRIEVAL_OUTPUT) == (0.61, 1.0)


def test_parses_answer_summary():
    assert gate.parse_answers(ANSWER_OUTPUT) == (10, 4)


def test_unreadable_output_is_an_error_not_a_pass():
    with pytest.raises(ValueError):
        gate.parse_retrieval("Traceback (most recent call last): ...")
    with pytest.raises(ValueError):
        gate.parse_answers("")


def test_retrieval_at_baseline_passes_and_a_drop_fails():
    assert gate.check_retrieval(0.61, 1.0, BASE) == []
    assert gate.check_retrieval(0.60, 1.0, BASE) == []          # rounding noise is allowed
    assert len(gate.check_retrieval(0.55, 1.0, BASE)) == 1       # real drop in recall
    assert len(gate.check_retrieval(0.61, 0.95, BASE)) == 1      # one question lost its hit


def test_answers_allow_one_flaky_answer_but_no_missed_refusal():
    assert gate.check_answers(10, 4, ANS) == []
    assert gate.check_answers(9, 4, ANS) == []
    assert len(gate.check_answers(8, 4, ANS)) == 1
    assert len(gate.check_answers(10, 3, ANS)) == 1