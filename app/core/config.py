import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_store")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

if not GROQ_API_KEY:
    print(
        "[WARNING] GROQ_API_KEY is not set. Get a free key at https://console.groq.com "
        "and add it to a .env file (see .env.example)."
    )
