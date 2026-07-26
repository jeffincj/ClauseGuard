from typing import List, Optional, Literal
from pydantic import BaseModel

DocType = Literal["rental", "loan", "nda_employment"]


class UploadResponse(BaseModel):
    document_id: str
    doc_type: DocType
    message: str


class ChatRequest(BaseModel):
    document_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    status: str
    retries_used: int
    grade_reason: Optional[str] = None


class RiskScanRequest(BaseModel):
    document_id: str
    doc_type: DocType


class RiskCategoryResult(BaseModel):
    key: str
    label: str
    why_it_matters: str
    answer: str
    status: str
    retries_used: int
    severity: str


class RiskScanResponse(BaseModel):
    document_id: str
    doc_type: DocType
    results: List[RiskCategoryResult]
