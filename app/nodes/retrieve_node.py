from app.core.ingestion import get_retriever
from app.core.state import ClauseGuardState


def retrieve_node(state: ClauseGuardState) -> ClauseGuardState:
    retriever = get_retriever(state["document_id"])
    docs = retriever.invoke(state["current_question"])
    state["retrieved_chunks"] = [d.page_content for d in docs]
    return state
