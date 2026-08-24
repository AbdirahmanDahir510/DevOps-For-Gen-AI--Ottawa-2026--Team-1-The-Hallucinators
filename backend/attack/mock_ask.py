"""
Mock /ask server for the Break My AI attack module.

Purpose: let the attack runner test its full poison -> ingest -> ask -> judge
loop against the REAL TF-IDF index, without needing AWS Bedrock credentials
or a running LLM. It reuses the teammate's real retrieve.py, so retrieval and
poisoning attacks are genuinely exercised. Only the model answer is faked.

It returns the SAME response shape the real app should use:
    { "answer": "...", "retrieved_chunks": [...] }

so when the real /ask is ready, the attack runner points at it with ZERO
code changes.

RUN (from inside backend/):
    uvicorn attack.mock_ask:app --reload --port 8000

NOTE on judging:
  * retrieval_hit  -> REAL and meaningful (real index, real chunks).
  * manipulation_hit -> will read False here, because a mock can't be
    "manipulated" by a payload. That's expected. Those light up only once
    you point the runner at the real LLM-backed /ask.
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

# Import the teammate's REAL retrieval so attacks hit the actual index.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # add backend/ to path
from retrieve import retrieve  # noqa: E402  -- his function

app = FastAPI()

TOP_K = 3  # match whatever his app uses if it differs


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: AskRequest):
    # Call his real retriever. If his signature differs (e.g. retrieve(q, k)),
    # adjust this one line to match.
    chunks = retrieve(req.question, TOP_K)

    # Fake the model step: just echo the retrieved context back as the "answer".
    # A real LLM would synthesise these; the mock only proves the pipeline works.
    context = "\n".join(str(c) for c in chunks)
    answer = f"[MOCK ANSWER — no LLM] Based on retrieved context:\n{context}"

    return {"answer": answer, "retrieved_chunks": chunks}


@app.get("/")
def health():
    return {"status": "mock /ask running"}
