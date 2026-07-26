"""
Evaluation script for ClauseGuard's self-healing loop.

Runs two kinds of tests against the sample documents:

1. GROUNDED tests — the taxonomy probe questions (things the documents
   genuinely address). Measures: first-try pass rate, retries needed,
   and give-up rate (should be low/zero — these ARE answerable).

2. ADVERSARIAL tests — questions the documents do NOT address. Measures:
   how often the system correctly admits it can't verify the answer
   (GAVE_UP or an honest "insufficient information" reply) instead of
   fabricating a confident-sounding but ungrounded answer. This is the
   headline "hallucination resistance rate" number for your portfolio/
   resume — it's a much stronger claim than "it answers questions."

Usage:
    export GROQ_API_KEY=your_key_here
    python -m scripts.evaluate

Outputs:
    eval_results/eval_report.md   — human-readable report
    eval_results/eval_raw.json    — raw per-question results
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.ingestion import ingest_document
from app.core.graph import run_clauseguard
from app.taxonomies.risk_taxonomies import TAXONOMIES, DOC_TYPE_LABELS
from scripts.adversarial_questions import ADVERSARIAL_QUESTIONS

SAMPLE_DOCS = {
    "rental": "data/sample_docs/sample_rental_agreement.txt",
    "loan": "data/sample_docs/sample_loan_agreement.txt",
    "nda_employment": "data/sample_docs/sample_employment_agreement.txt",
}

# Phrases that indicate an honest "can't verify" response even when the
# graph's final_status came back ANSWERED (e.g. the model itself hedged
# inside a passing grade rather than the retry-limit kicking in).
HONEST_ABSTENTION_MARKERS = [
    "cannot verify", "can't verify", "does not mention", "doesn't mention",
    "not specified", "not stated", "no information", "not addressed",
    "does not address", "doesn't address", "not covered", "unable to find",
    "insufficient information", "not mentioned", "no mention",
    "not enough information", "do not contain enough information",
    "does not contain enough information", "not enough info",
    "unclear if", "unclear whether", "it is unclear",
    "cannot be determined", "can't be determined", "cannot determine",
    "does not specify", "doesn't specify", "not clear from",
    "not provided in", "not include", "does not include",
]


def _is_honest_abstention(answer: str, final_status: str) -> bool:
    if final_status == "GAVE_UP":
        return True
    lowered = answer.lower()
    return any(marker in lowered for marker in HONEST_ABSTENTION_MARKERS)


def run_grounded_tests(doc_id: str, doc_type: str) -> list[dict]:
    results = []
    for category in TAXONOMIES[doc_type]:
        t0 = time.time()
        state = run_clauseguard(doc_id, category["probe_question"])
        elapsed = round(time.time() - t0, 2)
        results.append({
            "doc_type": doc_type,
            "test_kind": "grounded",
            "category": category["key"],
            "question": category["probe_question"],
            "answer": state["answer"],
            "final_status": state["final_status"],
            "retries_used": state["retry_count"],
            "seconds": elapsed,
        })
    return results


def run_adversarial_tests(doc_id: str, doc_type: str) -> list[dict]:
    results = []
    for question in ADVERSARIAL_QUESTIONS[doc_type]:
        t0 = time.time()
        state = run_clauseguard(doc_id, question)
        elapsed = round(time.time() - t0, 2)
        honest = _is_honest_abstention(state["answer"], state["final_status"])
        results.append({
            "doc_type": doc_type,
            "test_kind": "adversarial",
            "category": None,
            "question": question,
            "answer": state["answer"],
            "final_status": state["final_status"],
            "retries_used": state["retry_count"],
            "correctly_abstained": honest,
            "seconds": elapsed,
        })
    return results


def summarize(all_results: list[dict]) -> dict:
    grounded = [r for r in all_results if r["test_kind"] == "grounded"]
    adversarial = [r for r in all_results if r["test_kind"] == "adversarial"]

    grounded_first_try = sum(1 for r in grounded if r["retries_used"] == 0 and r["final_status"] == "ANSWERED")
    grounded_answered_after_retry = sum(1 for r in grounded if r["retries_used"] > 0 and r["final_status"] == "ANSWERED")
    grounded_gave_up = sum(1 for r in grounded if r["final_status"] == "GAVE_UP")

    adversarial_correct = sum(1 for r in adversarial if r["correctly_abstained"])
    adversarial_total = len(adversarial)

    avg_retries_grounded = (
        sum(r["retries_used"] for r in grounded) / len(grounded) if grounded else 0
    )

    return {
        "grounded_total": len(grounded),
        "grounded_first_try_pass_rate": round(grounded_first_try / len(grounded), 3) if grounded else None,
        "grounded_answered_after_retry": grounded_answered_after_retry,
        "grounded_gave_up": grounded_gave_up,
        "avg_retries_per_grounded_question": round(avg_retries_grounded, 2),
        "adversarial_total": adversarial_total,
        "hallucination_resistance_rate": round(adversarial_correct / adversarial_total, 3) if adversarial_total else None,
        "adversarial_correctly_abstained": adversarial_correct,
        "adversarial_flagged_for_review": adversarial_total - adversarial_correct,
    }


def write_markdown_report(all_results: list[dict], summary: dict, path: str):
    lines = []
    lines.append("# ClauseGuard Evaluation Report\n")
    lines.append(f"_Generated: {datetime.now(timezone.utc).isoformat()}_\n")

    lines.append("## Headline metrics\n")
    lines.append(f"- **Grounded question first-try pass rate:** {summary['grounded_first_try_pass_rate']} "
                 f"({summary['grounded_total']} questions tested)")
    lines.append(f"- **Answered after 1-2 retries:** {summary['grounded_answered_after_retry']}")
    lines.append(f"- **Gave up (grounded, answerable) questions:** {summary['grounded_gave_up']}")
    lines.append(f"- **Average retries per grounded question:** {summary['avg_retries_per_grounded_question']}")
    lines.append(f"- **Hallucination resistance rate (adversarial):** "
                 f"{summary['hallucination_resistance_rate']} "
                 f"({summary['adversarial_correctly_abstained']}/{summary['adversarial_total']} correctly abstained)")
    if summary["adversarial_flagged_for_review"]:
        lines.append(f"- ⚠️ **{summary['adversarial_flagged_for_review']} adversarial responses flagged for "
                     f"manual review** — see below, these need a human check for actual hallucination vs. "
                     f"legitimate partial matches.")
    lines.append("")

    lines.append("## Grounded questions (per document type)\n")
    for doc_type in TAXONOMIES:
        lines.append(f"### {DOC_TYPE_LABELS[doc_type]}\n")
        lines.append("| Category | Status | Retries | Answer (truncated) |")
        lines.append("|---|---|---|---|")
        for r in all_results:
            if r["test_kind"] == "grounded" and r["doc_type"] == doc_type:
                truncated = (r["answer"][:100] + "…") if len(r["answer"]) > 100 else r["answer"]
                truncated = truncated.replace("\n", " ").replace("|", "/")
                lines.append(f"| {r['category']} | {r['final_status']} | {r['retries_used']} | {truncated} |")
        lines.append("")

    lines.append("## Adversarial questions (per document type)\n")
    lines.append("_These questions are NOT answerable from the sample documents. "
                 "A correct system should abstain rather than fabricate an answer._\n")
    for doc_type in TAXONOMIES:
        lines.append(f"### {DOC_TYPE_LABELS[doc_type]}\n")
        lines.append("| Question | Correctly abstained? | Status | Retries |")
        lines.append("|---|---|---|---|")
        for r in all_results:
            if r["test_kind"] == "adversarial" and r["doc_type"] == doc_type:
                mark = "✅" if r["correctly_abstained"] else "⚠️ review"
                lines.append(f"| {r['question']} | {mark} | {r['final_status']} | {r['retries_used']} |")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    print("=" * 60)
    print("ClauseGuard Evaluation — self-healing RAG metrics")
    print("=" * 60)

    if not os.getenv("GROQ_API_KEY"):
        print("\n[ERROR] GROQ_API_KEY is not set. Add it to your .env or export it, then rerun.")
        sys.exit(1)

    os.makedirs("eval_results", exist_ok=True)
    all_results = []

    for doc_type, path in SAMPLE_DOCS.items():
        print(f"\nIndexing {DOC_TYPE_LABELS[doc_type]} ({path})...")
        doc_id = ingest_document(path, doc_type)

        print(f"Running {len(TAXONOMIES[doc_type])} grounded taxonomy questions...")
        all_results.extend(run_grounded_tests(doc_id, doc_type))

        print(f"Running {len(ADVERSARIAL_QUESTIONS[doc_type])} adversarial questions...")
        all_results.extend(run_adversarial_tests(doc_id, doc_type))

    summary = summarize(all_results)

    with open("eval_results/eval_raw.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": all_results}, f, indent=2)

    write_markdown_report(all_results, summary, "eval_results/eval_report.md")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("\nFull report: eval_results/eval_report.md")
    print("Raw data:    eval_results/eval_raw.json")


if __name__ == "__main__":
    main()
