import json
import re

from langchain_core.prompts import ChatPromptTemplate

from app.core.state import ClauseGuardState
from app.nodes.generate_node import get_llm

GRADE_PROMPT = ChatPromptTemplate.from_template(
    """You are a strict fact-checking judge. Your ONLY job is to determine
whether the ANSWER below is fully supported by the DOCUMENT EXCERPTS.

Rules:
- If the answer states specific facts (numbers, dates, penalties, clauses)
  that are NOT present in the excerpts, that is a FAIL.
- If the answer honestly says the excerpts are insufficient, that is a PASS
  (honesty about not knowing is acceptable and desired).
- If the answer is fully supported by the excerpts, that is a PASS.

Document excerpts:
---
{context}
---

Answer to check:
---
{answer}
---

Respond with ONLY a JSON object, no other text, in this exact format:
{{"verdict": "PASS" or "FAIL", "reason": "one short sentence explaining why"}}"""
)


def _parse_grade(raw: str):
    raw = raw.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return "FAIL", "Grader response could not be parsed; treated as failure to be safe."
    try:
        parsed = json.loads(match.group(0))
        verdict = parsed.get("verdict", "FAIL").upper().strip()
        reason = parsed.get("reason", "No reason provided.")
        if verdict not in ("PASS", "FAIL"):
            verdict = "FAIL"
        return verdict, reason
    except json.JSONDecodeError:
        return "FAIL", "Grader response was not valid JSON; treated as failure to be safe."


def grade_node(state: ClauseGuardState) -> ClauseGuardState:
    context = "\n\n".join(state["retrieved_chunks"]) or "(no relevant excerpts found)"
    chain = GRADE_PROMPT | get_llm()
    response = chain.invoke({"context": context, "answer": state["answer"]})
    verdict, reason = _parse_grade(response.content)
    state["grade"] = verdict
    state["grade_reason"] = reason
    return state
