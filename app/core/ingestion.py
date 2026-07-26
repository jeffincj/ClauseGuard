import os
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from chromadb.utils import embedding_functions
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

from app.core.config import CHROMA_PERSIST_DIR

_embeddings = None

# A PDF page is considered "image-only" (scanned, no real text layer) if its
# extracted text is shorter than this many characters — real contract text
# per page is almost always much longer than this.
MIN_CHARS_PER_PAGE_BEFORE_OCR_FALLBACK = 40

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


class LightweightONNXEmbeddings(Embeddings):
    """
    Thin LangChain-compatible wrapper around ChromaDB's bundled ONNX
    MiniLM embedding function. Deliberately avoids sentence-transformers/
    PyTorch, which are heavy enough to cause out-of-memory crashes on
    free-tier hosts with ~512MB RAM. Same underlying MiniLM model quality,
    much smaller runtime footprint.
    """

    def __init__(self):
        self._ef = embedding_functions.ONNXMiniLM_L6_V2()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [list(vec) for vec in self._ef(texts)]

    def embed_query(self, text: str) -> list[float]:
        return list(self._ef([text])[0])


def get_embeddings():
    """Lazily load the embedding model (kept singleton to avoid reloading per request)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = LightweightONNXEmbeddings()
    return _embeddings
def _ocr_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image)


def _load_pdf_with_ocr_fallback(file_path: str) -> list[Document]:
    """
    Loads a PDF page by page. Any page with little/no extractable text
    (i.e. it's a scanned photo, not real text) is rasterized and OCR'd
    instead, so photographed/scanned agreements work the same as
    text-native PDFs.
    """
    docs = PyPDFLoader(file_path).load()

    needs_ocr = any(
        len(d.page_content.strip()) < MIN_CHARS_PER_PAGE_BEFORE_OCR_FALLBACK
        for d in docs
    )
    if not needs_ocr:
        return docs

    pages = convert_from_path(file_path, dpi=300)
    ocr_docs = []
    for i, page_image in enumerate(pages):
        existing_text = docs[i].page_content.strip() if i < len(docs) else ""
        if len(existing_text) >= MIN_CHARS_PER_PAGE_BEFORE_OCR_FALLBACK:
            ocr_docs.append(docs[i])
        else:
            text = _ocr_image(page_image)
            ocr_docs.append(Document(page_content=text, metadata={"page": i, "source": file_path, "ocr": True}))
    return ocr_docs


def load_document(file_path: str) -> list[Document]:
    """
    Load a document into LangChain Document objects. Handles:
    - .txt          -> plain text load
    - .pdf           -> text extraction, falling back to OCR per-page for
                       scanned/photographed pages
    - .jpg/.jpeg/.png -> OCR directly (a single photographed page)
    """
    lower_path = file_path.lower()

    if lower_path.endswith(".pdf"):
        return _load_pdf_with_ocr_fallback(file_path)

    if lower_path.endswith(IMAGE_EXTENSIONS):
        image = Image.open(file_path)
        text = _ocr_image(image)
        return [Document(page_content=text, metadata={"source": file_path, "ocr": True})]

    return TextLoader(file_path, encoding="utf-8").load()


def chunk_documents(docs, chunk_size: int = 800, chunk_overlap: int = 120):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)


def ingest_document(file_path: str, doc_type: str) -> str:
    """
    Loads, chunks, and embeds a document into its own ChromaDB collection.
    Returns a document_id used to reference this document's collection later.
    """
    return ingest_multiple_documents([file_path], doc_type)


def ingest_multiple_documents(file_paths: list[str], doc_type: str) -> str:
    """
    Loads, chunks, and embeds MULTIPLE files (e.g. three separate page
    photos of one agreement) as a single combined document. Files are
    processed in the given order, so upload page 1, then page 2, then
    page 3, in that order.
    """
    document_id = f"{doc_type}_{uuid.uuid4().hex[:10]}"

    all_docs = []
    for i, file_path in enumerate(file_paths):
        page_docs = load_document(file_path)
        for d in page_docs:
            d.metadata["upload_order"] = i
        all_docs.extend(page_docs)

    chunks = chunk_documents(all_docs)

    if not chunks:
        raise ValueError(
            "No extractable text found in the uploaded document(s), even after OCR. "
            "Try clearer photos/scans with good lighting and straight page alignment."
        )

    collection_dir = os.path.join(CHROMA_PERSIST_DIR, document_id)
    os.makedirs(collection_dir, exist_ok=True)

    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=collection_dir,
        collection_name=document_id,
    )

    return document_id


def get_retriever(document_id: str, k: int = 4):
    collection_dir = os.path.join(CHROMA_PERSIST_DIR, document_id)
    if not os.path.isdir(collection_dir):
        raise ValueError(f"No indexed document found for id: {document_id}")

    vectordb = Chroma(
        persist_directory=collection_dir,
        collection_name=document_id,
        embedding_function=get_embeddings(),
    )
    return vectordb.as_retriever(search_kwargs={"k": k})