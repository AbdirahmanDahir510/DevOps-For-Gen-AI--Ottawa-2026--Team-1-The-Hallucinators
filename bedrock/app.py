"""
Sample RAG chatbot API — LOCAL OLLAMA VERSION.

Use this while AWS Bedrock account verification is pending (can take
up to 2 hours for new accounts). Once verification clears, switch back
to app.py (Bedrock version) for the real demo/deployment.

Requires Ollama running locally with the llama3.2 model pulled.
No API key or subscription needed.

Run with: uvicorn app_ollama:app --reload --port 8000
(or, since PATH may not recognize uvicorn directly:
 python -m uvicorn app_ollama:app --reload --port 8000)
"""

import requests
from fastapi import FastAPI
from pydantic import BaseModel

from retrieve import retrieve

app = FastAPI(title="Sample RAG Chatbot (Local Ollama)")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


class Question(BaseModel):
    question: str
    top_k: int = 3


class Answer(BaseModel):
    answer: str
    retrieved_chunks: list


@app.post("/ask", response_model=Answer)
def ask(payload: Question):
    chunks = retrieve(payload.question, top_k=payload.top_k)

    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    prompt = f"""You are a helpful assistant. Answer the question using ONLY
the context below. If the answer is not in the context, say you don't know.

Context:
{context}

Question: {payload.question}

Answer:"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    answer_text = response.json()["response"].strip()

    return Answer(answer=answer_text, retrieved_chunks=chunks)


@app.get("/health")
def health():
    return {"status": "ok"}
