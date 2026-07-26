from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import GROQ_API_KEY, GROQ_MODEL
from app.core.state import ClauseGuardState

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0.1)
    return _llm


GENERATE_PROMPT = ChatPromptTemplate.from_template(
    """You are ClauseGuard, a careful legal-document risk assistant.
Answer the question using ONLY the document excerpts below. Do not use
outside knowledge or assume anything not stated in the excerpts.

Two different situations require different responses:

1. If the question asks what the document SAYS about something, and the
   excerpts don't address it: state plainly that the document does not
   appear to address that topic. This is a factual observation about the
   document, not advice, so say it directly and clearly (e.g. "This
   document does not contain any clause about X.").

2. If the question asks for ADVICE — what should be added, changed,
   negotiated, or how to fix/improve the document — do not draft new
   clause wording or give legal strategy. Instead: (a) state clearly
   whether the document currently addresses that topic at all, based on
   the excerpts, and (b) if it's genuinely missing, say plainly that
   you can't draft legal wording or give legal advice, and suggest the
   person raise it directly with the other party or consult a lawyer for
   specific wording. Do not soften this into a vague "not enough
   information" non-answer — be direct about what's missing AND direct
   about why you can't go further.

Document excerpts:
---
{context}
---

Question: {question}

Answer (be specific, cite relevant clause content where it exists, keep it concise):"""
)


def generate_node(state: ClauseGuardState) -> ClauseGuardState:
    context = "\n\n".join(state["retrieved_chunks"]) or "(no relevant excerpts found)"
    chain = GENERATE_PROMPT | get_llm()
    response = chain.invoke({"context": context, "question": state["current_question"]})
    state["answer"] = response.content.strip()
    return state
