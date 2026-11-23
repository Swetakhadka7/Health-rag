import json
from pathlib import Path

OUT = Path("eval/questions.jsonl")

W = "who_2009_dengue_guidelines.pdf"
N = "nepal_edcd_2019_dengue_guidelines.pdf"
B = "bhutan_2020_dengue_clinical.pdf"
M = "maldives_2022_dengue_children.pdf"

# Questions written independently of the search system. Each "pages" list was
# checked by reading the page text in the four PDFs (PDF page numbers).
NEW = [
    ("Can I give ibuprofen to a child with dengue fever?",
     [(B, 16), (M, 12), (M, 21), (N, 44), (W, 46), (W, 60)]),
    ("How do I do a tourniquet test?",
     [(B, 14), (M, 7)]),
    ("How often should vital signs be checked in a patient with dengue warning signs?",
     [(M, 14), (B, 16), (B, 17), (N, 46), (W, 47)]),
    ("Which dengue patients should be admitted to hospital instead of sent home?",
     [(B, 16), (N, 45), (N, 46), (W, 59), (M, 14)]),
    ("How should NS1, IgM and IgG results be interpreted?",
     [(B, 11), (M, 11), (N, 36)]),
    ("Do dengue patients with a low platelet count need a platelet transfusion?",
     [(M, 14), (M, 21), (B, 21), (W, 52)]),
    ("What are the early signs that a dengue patient is going into shock?",
     [(M, 6), (M, 8), (B, 17), (W, 40), (N, 27)]),
    ("When can intravenous fluids be stopped in a dengue patient?",
     [(B, 21), (N, 48), (W, 47), (M, 14)]),
    ("What can households do to stop mosquitoes from breeding around their home?",
     [(B, 26), (N, 68), (N, 69), (M, 4)]),
    ("How is dengue managed in pregnant women?",
     [(B, 25), (N, 49), (N, 51)]),
]


def main():
    text = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    existing = [json.loads(line) for line in text.splitlines() if line.strip()]
    have = {q["question"] for q in existing}
    next_num = len(existing) + 1

    with OUT.open("a", encoding="utf-8") as f:
        if text and not text.endswith("\n"):
            f.write("\n")
        for question, pages in NEW:
            if question in have:
                print("already there:", question)
                continue
            q = {
                "id": f"q{next_num:03d}",
                "question": question,
                "expected": [{"doc": d, "page": p} for d, p in pages],
            }
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
            print(f"{q['id']}  ({len(pages)} pages)  {question}")
            next_num += 1


if __name__ == "__main__":
    main()
    