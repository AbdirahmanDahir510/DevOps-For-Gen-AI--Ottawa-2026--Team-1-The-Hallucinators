# Sample RAG Chatbot — Local Llama (Ollama) Version

A small Retrieval-Augmented Generation (RAG) chatbot that answers questions using a handful
of sample documents. This version runs **entirely locally** using [Ollama](https://ollama.com)
and the `llama3.2` model — no API key, no subscription, no internet connection required once
set up. It's the target system that our attack and chaos modules test against.

---

## How it works

1. **Ingestion** — `sample_docs/*.txt` are split into small chunks and converted into TF-IDF
   vectors (a way of turning text into numbers based on word importance).
2. **Storage** — the chunks and their vectors are saved to `index.json` and `vectorizer.pkl`.
3. **Retrieval** — when a question comes in, it's vectorized the same way and compared against
   every stored chunk using cosine similarity. The top-matching chunks are returned.
4. **Generation** — the retrieved chunks are inserted into a prompt and sent to `llama3.2`
   (running locally via Ollama), which generates an answer using only that context.

No real vector database is used — this is intentional. It keeps the system fast to set up,
works fully offline, and is easy to reason about (and attack) for the demo. A production
version would swap this for something like Pinecone, Chroma, or pgvector.

---

## Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com/download)** installed
- The `llama3.2` model pulled:
  ```bash
  ollama pull llama3.2
  ```
  Confirm it's there with:
  ```bash
  ollama list
  ```
  You should see `llama3.2:latest` in the output.

Ollama typically runs automatically in the background after install. If a command like
`ollama serve` gives you a "port already in use" error, that's a good sign — it means Ollama
is already running and ready.

---

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > On some systems you may need `pip install -r requirements.txt --break-system-packages`
   > or to call Python explicitly: `python -m pip install -r requirements.txt`

2. Build the index (reads `sample_docs/`, creates `index.json` and `vectorizer.pkl`):
   ```bash
   python ingest.py
   ```
   You should see output like:
   ```
   Loaded 6 chunks from sample_docs/
   Saved index with 6 chunks to index.json
   Saved vectorizer to vectorizer.pkl
   ```

3. Start the server:
   ```bash
   uvicorn app:app --reload --port 8000
   ```
   If your terminal says `'uvicorn' is not recognized`, run it through Python instead:
   ```bash
   python -m uvicorn app:app --reload --port 8000
   ```

---

## Testing it

Open your browser to the interactive API docs:
```
http://localhost:8000/docs
```

1. Click **POST /ask** to expand it
2. Click **"Try it out"**
3. Enter a question, for example:
   ```json
   { "question": "How many days can I work remotely?", "top_k": 3 }
   ```
4. Click **Execute**

The first request may take 10–30 seconds while `llama3.2` loads into memory. After that,
follow-up requests are noticeably faster while the model stays "warm."

### Example verified test cases

| Question | Expected behavior |
|---|---|
| "How many days can I work remotely?" | Answers correctly from `company_policy.txt` |
| "What is the refund policy?" | Answers correctly from `product_faq.txt` |
| "What happens on day one for a new employee?" | Answers correctly from `onboarding_guide.txt` |
| "What is the CEO's name?" | Says **"I don't know"** — nothing in the docs answers this, and all `retrieved_chunks` scores should show `0`, not `null` |

That last case matters: a chatbot that makes up an answer when it doesn't actually know
one is a reliability and safety problem. Confirming it says "I don't know" is a real test,
not just a demo nicety.

---

## API reference

**`POST /ask`**

Request:
```json
{
  "question": "string",
  "top_k": 3
}
```

Response:
```json
{
  "answer": "string",
  "retrieved_chunks": [
    {
      "score": 0.4465,
      "source": "company_policy.txt",
      "chunk_id": 0,
      "text": "..."
    }
  ]
}
```

`retrieved_chunks` is returned alongside the answer on purpose — it lets other parts of the
project (the attack module especially) verify *what the model actually saw*, not just what
it said. This is essential for confirming whether an attack (like document poisoning) actually
influenced the answer.

**`GET /health`** — simple liveness check, returns `{"status": "ok"}`.

---

## For the attack module

- **Document poisoning**: edit or add a file in `sample_docs/`, re-run `python ingest.py`,
  then query `/ask` and check `retrieved_chunks` to see if the poisoned content got pulled in
  and whether the answer reflects it.
- **Retrieval manipulation**: craft text designed to score high on cosine similarity for
  unrelated questions, then check if it shows up in `retrieved_chunks` even when it shouldn't
  be relevant.

## For the chaos module

- The `/ask` endpoint is a normal HTTP call — latency, timeouts, and failures can be simulated
  by wrapping calls to it, or by mocking `retrieve()` to raise exceptions or sleep.
- To simulate "model unavailable," stop the Ollama process and call `/ask` — the app will
  raise a connection error since `response.raise_for_status()` fails when Ollama isn't reachable.
- `retrieve.py` and `app.py` are separated on purpose, so a broken or slow version of
  `retrieve()` can be swapped in without touching the API layer.

---

## Notes on design choices

- **TF-IDF instead of real embeddings**: no external model download needed, so it works
  offline and isn't dependent on venue wifi. Trade-off, not an oversight — a production
  version would use proper embeddings and a real vector store.
- **Fixed-size chunking**: simple and predictable. Fine for a hackathon demo, not
  production-grade (a real system would chunk by sentence/paragraph boundaries).
- **Local model (llama3.2) instead of a hosted API**: zero cost, zero external dependency,
  always available even without internet — a deliberate fallback option alongside a
  cloud-hosted version (AWS Bedrock / Claude) used elsewhere in this project.

## Troubleshooting

| Problem | Likely cause / fix |
|---|---|
| `'uvicorn' is not recognized` | Use `python -m uvicorn app:app --reload --port 8000` instead |
| First request takes 10–30s | Normal — `llama3.2` is loading into memory. Faster on repeat calls. |
| Connection refused to Ollama | Ollama isn't running. Try `ollama serve`, or check `ollama list` first. |
| `score: null` in response | Old bug, fixed — should show `0` for no-match questions. Re-pull `retrieve.py` if you see this. |
