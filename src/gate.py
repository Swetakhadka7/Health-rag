"""Release gate: run the evaluations and fail if scores fall below the saved baseline.

Usage (from the project root, Docker running):
    python src/gate.py                 # retrieval + answer checks
    python src/gate.py --skip-answers  # retrieval only (no Gemini calls)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

BASELINE = Path("eval/baseline.json")
TOLERANCE = 0.01  # retrieval is deterministic, so only allow rounding noise


def parse_retrieval(text):
    recall = re.search(r"Mean recall@\d+:\s*([0-9.]+)", text)
    hit = re.search(r"Hit rate@\d+ \(at least one right page\):\s*([0-9.]+)", text)
    if not recall or not hit:
        raise ValueError("could not find the retrieval summary lines")
    return float(recall.group(1)), float(hit.group(1))


def parse_answers(text):
    answerable = re.search(r"Answerable questions passed:\s*(\d+)/(\d+)", text)
    refused = re.search(r"Should-refuse questions passed:\s*(\d+)/(\d+)", text)
    if not answerable or not refused:
        raise ValueError("could not find the answer summary lines")
    return int(answerable.group(1)), int(refused.group(1))


def check_retrieval(recall, hit, base):
    problems = []
    if recall < base["mean_recall"] - TOLERANCE:
        problems.append(f"mean recall {recall:.2f} is below baseline {base['mean_recall']:.2f}")
    if hit < base["hit_rate"] - TOLERANCE:
        problems.append(f"hit rate {hit:.2f} is below baseline {base['hit_rate']:.2f}")
    return problems


def check_answers(answerable, refused, base):
    problems = []
    if answerable < base["answerable_min"]:
        problems.append(f"answerable passed {answerable}, need at least {base['answerable_min']}")
    if refused < base["refuse_min"]:
        problems.append(f"should-refuse passed {refused}, need at least {base['refuse_min']}")
    return problems


def run(args):
    result = subprocess.run(
        [sys.executable, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.stdout + result.stderr


def main():
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    failures = []

    print("Running retrieval evaluation ...")
    out = run(["src/evaluate.py", baseline["retrieval"]["method"]])
    try:
        recall, hit = parse_retrieval(out)
        problems = check_retrieval(recall, hit, baseline["retrieval"])
        print(f"  recall {recall:.2f} (baseline {baseline['retrieval']['mean_recall']:.2f}), "
              f"hit rate {hit:.2f} (baseline {baseline['retrieval']['hit_rate']:.2f})")
    except ValueError as e:
        problems = [f"{e}. Last output: {out[-300:]!r}"]
    failures += problems

    if "--skip-answers" not in sys.argv:
        print("Running answer evaluation (calls Gemini, takes a few minutes) ...")
        out = run(["src/evaluate_answers.py"])
        try:
            answerable, refused = parse_answers(out)
            problems = check_answers(answerable, refused, baseline["answers"])
            print(f"  answerable passed {answerable} (min {baseline['answers']['answerable_min']}), "
                  f"should-refuse passed {refused} (min {baseline['answers']['refuse_min']})")
        except ValueError as e:
            problems = [f"{e}. Last output: {out[-300:]!r}"]
        failures += problems

    print()
    if failures:
        print("GATE FAILED")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("GATE PASSED")


if __name__ == "__main__":
    main()