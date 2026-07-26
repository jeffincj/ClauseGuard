from typing import TypedDict, List, Optional


class ClauseGuardState(TypedDict):
    document_id: str
    original_question: str      # the user's question, or a risk-taxonomy probe question
    current_question: str       # may be rewritten by the Rewrite Node on retry
    retrieved_chunks: List[str]
    answer: str
    grade: Optional[str]        # "PASS" or "FAIL"
    grade_reason: str
    retry_count: int
    max_retries: int
    final_status: Optional[str]  # "ANSWERED" or "GAVE_UP"
