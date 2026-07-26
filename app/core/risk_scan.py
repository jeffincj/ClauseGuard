import json
import re

from langchain_core.prompts import ChatPromptTemplate

from app.core.graph import run_clauseguard
from app.nodes.generate_node import get_llm
from app.taxonomies.risk_taxonomies import TAXONOMIES

SEVERITY_PROMPT = ChatPromptTemplate.from_template(
    """You are assessing risk severity for a clause found in a legal/policy
document, from the perspective of the person signing it (tenant, borrower,
or employee — not the party who drafted it).

Clause category: {label}
Why this category matters: {why_it_matters}
What the document actually says (per our grounded analysis): {answer}

Classify the severity as one of: "red" (high risk / unfavorable to signer),
"amber" (worth negotiating / ambiguous), "green" (standard / low risk), or
"unknown" (could not be verified from the document).

Respond with ONLY a JSON object: {{"severity": "red"|"amber"|"green"|"unknown"}}"""
)


def _classify_severity(label: str, why_it_matters: str, answer: str) -> str:
    chain = SEVERITY_PROMPT | get_llm()
    response = chain.invoke(
        {"label": label, "why_it_matters": why_it_matters, "answer": answer}
    )
    match = re.search(r"\{.*\}", response.content, re.DOTALL)
    if not match:
        return "unknown"
    try:
        return json.loads(match.group(0)).get("severity", "unknown")
    except json.JSONDecodeError:
        return "unknown"


def run_full_risk_scan(document_id: str, doc_type: str) -> list[dict]:
    """
    Runs the self-healing RAG pipeline once per risk category in the
    document type's taxonomy, then adds a severity classification.
    Returns a list of per-category result dicts ready for the UI/report.
    """
    if doc_type not in TAXONOMIES:
        raise ValueError(f"Unknown document type: {doc_type}")

    results = []
    for category in TAXONOMIES[doc_type]:
        state = run_clauseguard(document_id, category["probe_question"])

        severity = "unknown"
        if state["final_status"] == "ANSWERED":
            severity = _classify_severity(
                category["label"], category["why_it_matters"], state["answer"]
            )

        results.append(
            {
                "key": category["key"],
                "label": category["label"],
                "why_it_matters": category["why_it_matters"],
                "answer": state["answer"],
                "status": state["final_status"],
                "retries_used": state["retry_count"],
                "severity": severity,
            }
        )
    return results
