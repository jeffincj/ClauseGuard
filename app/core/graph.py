from langgraph.graph import StateGraph, END

from app.core.state import ClauseGuardState
from app.core.config import MAX_RETRIES
from app.nodes.retrieve_node import retrieve_node
from app.nodes.generate_node import generate_node
from app.nodes.grade_node import grade_node
from app.nodes.rewrite_node import rewrite_node


def _route_after_grade(state: ClauseGuardState) -> str:
    if state["grade"] == "PASS":
        return "pass"
    if state["retry_count"] >= state["max_retries"]:
        return "give_up"
    return "retry"


def _give_up_node(state: ClauseGuardState) -> ClauseGuardState:
    state["final_status"] = "GAVE_UP"
    state["answer"] = (
        "I can't verify this from the document with confidence after "
        f"{state['retry_count']} rephrased attempts. Rather than guess, "
        "I'm flagging this as something a human should review directly in "
        "the source document."
    )
    return state


def _finalize_node(state: ClauseGuardState) -> ClauseGuardState:
    if state.get("final_status") is None:
        state["final_status"] = "ANSWERED"
    return state


def build_graph():
    graph = StateGraph(ClauseGuardState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("grade_answer", grade_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("give_up", _give_up_node)
    graph.add_node("finalize", _finalize_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "grade_answer")

    graph.add_conditional_edges(
        "grade_answer",
        _route_after_grade,
        {
            "pass": "finalize",
            "retry": "rewrite",
            "give_up": "give_up",
        },
    )

    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("give_up", END)
    graph.add_edge("finalize", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_clauseguard(document_id: str, question: str) -> ClauseGuardState:
    initial_state: ClauseGuardState = {
        "document_id": document_id,
        "original_question": question,
        "current_question": question,
        "retrieved_chunks": [],
        "answer": "",
        "grade": None,
        "grade_reason": "",
        "retry_count": 0,
        "max_retries": MAX_RETRIES,
        "final_status": None,
    }
    result = get_graph().invoke(initial_state)
    return result