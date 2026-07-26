import os
import shutil
import tempfile
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.api.schemas import (
    UploadResponse,
    ChatRequest,
    ChatResponse,
    RiskScanRequest,
    RiskScanResponse,
)
from app.core.ingestion import ingest_multiple_documents
from app.core.graph import run_clauseguard
from app.core.risk_scan import run_full_risk_scan
from app.taxonomies.risk_taxonomies import DOC_TYPE_LABELS

router = APIRouter()

ALLOWED_EXTENSIONS = (".pdf", ".txt", ".jpg", ".jpeg", ".png")


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    files: List[UploadFile] = File(...),
    doc_type: str = Form(...),
):
    if doc_type not in DOC_TYPE_LABELS:
        raise HTTPException(400, f"Unsupported doc_type: {doc_type}")

    for f in files:
        if not f.filename.lower().endswith(ALLOWED_EXTENSIONS):
            raise HTTPException(
                400,
                f"'{f.filename}' is not supported. Only .pdf, .txt, .jpg, .jpeg, and .png files are supported.",
            )

    tmp_paths = []
    try:
        for f in files:
            suffix = os.path.splitext(f.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(f.file, tmp)
                tmp_paths.append(tmp.name)

        document_id = ingest_multiple_documents(tmp_paths, doc_type)
    except Exception as e:
        raise HTTPException(500, f"Failed to process document(s): {e}")
    finally:
        for p in tmp_paths:
            os.unlink(p)

    page_word = "page" if len(files) == 1 else "pages"
    return UploadResponse(
        document_id=document_id,
        doc_type=doc_type,
        message=f"Indexed successfully as {DOC_TYPE_LABELS[doc_type]} ({len(files)} {page_word}).",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        state = run_clauseguard(req.document_id, req.question)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Pipeline error: {e}")

    return ChatResponse(
        answer=state["answer"],
        status=state["final_status"],
        retries_used=state["retry_count"],
        grade_reason=state.get("grade_reason"),
    )


@router.post("/risk-scan", response_model=RiskScanResponse)
async def risk_scan(req: RiskScanRequest):
    try:
        results = run_full_risk_scan(req.document_id, req.doc_type)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Pipeline error: {e}")

    return RiskScanResponse(
        document_id=req.document_id, doc_type=req.doc_type, results=results
    )