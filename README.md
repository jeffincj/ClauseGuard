# ClauseGuard — Self-Healing Legal & Policy Document Risk Analyzer

ClauseGuard is a RAG system that doesn't blindly trust its own output. It reads
rental agreements, loan contracts, and NDA/employment agreements, and for every
answer it generates, it **grades that answer against the retrieved clauses
before showing it to you**. If the answer isn't actually grounded in the
document, it rewrites the question and retries — up to 2 times — before
honestly saying "I can't verify this" instead of hallucinating a risky clause
that isn't really there.

## Why this exists

Generic "chat with your PDF" tools will confidently answer a question about a
contract even when the retrieved chunks don't actually support the answer.
In a legal/financial context, a confidently wrong answer about a penalty
clause or interest rate is worse than no answer at all. ClauseGuard's
retrieve → generate → grade → rewrite loop, orchestrated as a LangGraph state
machine, is built specifically to catch and correct that failure mode.

## Architecture

```
                ┌────────────┐
   question ──▶ │  Retrieve  │  (ChromaDB semantic search)
                └─────┬──────┘
                      ▼
                ┌────────────┐
                │  Generate  │  (Groq Llama 3.3 — answers ONLY from retrieved text)
                └─────┬──────┘
                      ▼
                ┌────────────┐
                │   Grade    │  (LLM-as-judge: is the answer grounded?)
                └─────┬──────┘
              PASS ◀──┴──▶ FAIL
                │           │
                ▼           ▼
             Return    retries < max?
             answer      │        │
                        yes       no
                         │        │
                         ▼        ▼
                    ┌─────────┐  Honest
                    │ Rewrite │  "can't verify"
                    │ question│  fallback
                    └────┬────┘
                         │
                         └──▶ back to Retrieve
```

On top of this core loop, `risk_scan.py` runs the whole pipeline once per
clause category in a document-type-specific **risk taxonomy** (see
`app/taxonomies/risk_taxonomies.py`) — e.g. for a rental agreement: security
deposit terms, lock-in penalties, maintenance responsibility, rent escalation,
notice period, landlord entry rights — and adds a red/amber/green severity
score to each grounded result.

## Supported document types (v1)

- **Rental agreements** — deposit terms, lock-in penalties, maintenance,
  rent escalation, notice period, landlord entry rights
- **Loan agreements** — interest rate type, prepayment penalty, late payment
  compounding, collateral/default terms, hidden charges, guarantor liability
- **NDA / Employment agreements** — non-compete scope, IP assignment,
  confidentiality duration, termination notice, training bonds, dispute
  resolution/jurisdiction

Adding a new document type is just adding a new list of `{key, label,
probe_question, why_it_matters}` entries to `risk_taxonomies.py` — no other
code changes needed.

## Tech stack

| Layer | Choice |
|---|---|
| API | FastAPI |
| Orchestration | LangGraph |
| LLM | Groq-hosted Llama 3.3 70B (`langchain-groq`) |
| Vector store | ChromaDB (local, persisted per document) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (free, local, no API cost) |
| Frontend | Vanilla HTML/CSS/JS served via Jinja2 templates |

## Local setup

```bash
git clone <your-repo-url>
cd clauseguard
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your free Groq API key from https://console.groq.com

uvicorn main:app --reload
```

Open http://localhost:8000, pick a document type tab, upload one of the
sample documents in `data/sample_docs/` (or your own PDF/TXT), then either
run the **Full Risk Scan** or ask a question directly in the **Ask a
Question** tab.

## Testing it yourself

Three synthetic sample documents are included in `data/sample_docs/` —
a rental agreement, a loan agreement, and an employment agreement — each
deliberately written with a mix of standard and unfavorable-to-signer clauses
so you can see the severity scoring do something meaningful. None of these
are real documents or reference real people/companies.

## Evaluating it (the numbers for your resume/portfolio)

```bash
python -m scripts.evaluate
```

This runs two test suites against all three sample documents:

1. **Grounded questions** — the actual taxonomy probe questions (things the
   documents genuinely address). Reports first-try pass rate, retries
   needed, and give-up rate.
2. **Adversarial questions** (`scripts/adversarial_questions.py`) — questions
   deliberately NOT answerable from the sample documents (e.g. "what's the
   pet policy?" for a rental agreement that never mentions pets). A correct
   system abstains ("I can't verify this") instead of fabricating an answer.
   The resulting **hallucination resistance rate** is the strongest single
   number to put on a resume — it's a direct, falsifiable claim about
   reliability, not just "it works."

Output: `eval_results/eval_report.md` (readable table) and
`eval_results/eval_raw.json` (raw data, useful if you want to chart it).

Resume-ready phrasing once you've run it:
> Evaluated the self-healing loop against grounded and adversarial test
> sets, measuring first-try grounding pass rate and hallucination
> resistance rate on out-of-scope questions.

## Deployment

Deploy like any FastAPI app (Render, Railway, Fly.io):
1. Build command: `pip install -r requirements.txt`
2. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Set `GROQ_API_KEY` as an environment variable in your host's dashboard
   (never commit `.env`)
4. Note: ChromaDB persists to local disk — on free-tier hosts with ephemeral
   filesystems, uploaded document indexes won't survive a redeploy/restart.
   For a portfolio demo this is fine; for production, swap `CHROMA_PERSIST_DIR`
   for a hosted vector DB.

## Project structure

```
clauseguard/
├── main.py                        # FastAPI app entrypoint
├── app/
│   ├── core/
│   │   ├── config.py               # env/config loading
│   │   ├── state.py                # LangGraph state schema
│   │   ├── ingestion.py            # PDF/text loading, chunking, embedding
│   │   ├── graph.py                # the self-healing state machine
│   │   └── risk_scan.py            # runs the pipeline across a full taxonomy
│   ├── nodes/
│   │   ├── retrieve_node.py
│   │   ├── generate_node.py
│   │   ├── grade_node.py           # the groundedness judge
│   │   └── rewrite_node.py
│   ├── api/
│   │   ├── routes.py                # /upload, /chat, /risk-scan
│   │   └── schemas.py
│   └── taxonomies/
│       └── risk_taxonomies.py       # domain knowledge: what to check per doc type
├── frontend/
│   ├── templates/index.html
│   └── static/{style.css, app.js}
└── data/sample_docs/                # synthetic test documents
```

## What "self-healing" means here, concretely

It's not a marketing term — it's the `grade` → `rewrite` → retry edge in
`app/core/graph.py`. Every answer is checked by a second LLM call whose only
job is to compare the answer against the retrieved text and flag
unsupported claims. If it fails, the question is rephrased (not just
re-asked) to improve retrieval on the next attempt, capped at
`MAX_RETRIES` (default 2) before an honest fallback.
