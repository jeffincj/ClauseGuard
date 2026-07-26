from langchain_core.prompts import ChatPromptTemplate

from app.core.state import ClauseGuardState
from app.nodes.generate_node import get_llm

REWRITE_PROMPT = ChatPromptTemplate.from_template(
    """The following question failed to retrieve a well-grounded answer from a
legal/policy document. Rephrase it to be more specific and more likely to
match the exact wording a contract would use (e.g. use terms like "clause",
"penalty", "liability", "notice period" where relevant).

Original question: {question}
Why it failed: {reason}

Respond with ONLY the rewritten question, nothing else."""
)


def rewrite_node(state: ClauseGuardState) -> ClauseGuardState:
    chain = REWRITE_PROMPT | get_llm()
    response = chain.invoke(
        {"question": state["current_question"], "reason": state["grade_reason"]}
    )
    state["current_question"] = response.content.strip()
    state["retry_count"] += 1
    return state
