# Sample RAG chatbot — starter kit

This is the target app that the attack and chaos modules will test against.

## What it does

1. `sample_docs/` holds a few plain-text documents (company policy, FAQ, onboarding guide).
2. `ingest.py` chunks those docs, builds a TF-IDF index, and saves it plus the fitted vectorizer to disk.
3. `retrieve.py` loads that index and, given a question, returns the top-k most similar chunks.
4. `app.py` exposes a `/ask` API: it retrieves chunks for a question, builds a prompt with them as context, and asks a locally running LLM (via Ollama) to answer using only that context.

## Two versions of the API

- **`app.py`** — uses your local `llama3.2` model via Ollama. No API key or subscription needed. Use this now.
- **`app_hosted.py`** — same logic, but calls a hosted model (Anthropic API) instead. Use this later once the team has real API access (AWS Bedrock credits or an Anthropic key). Needs extra packages: `pip install -r requirements-hosted.txt`, plus a `.env` file with `ANTHROPIC_API_KEY=your_key_here`.

To switch, just run the other file:
```bash
# local, now
uvicorn app:app --reload --port 8000

# hosted, later
uvicorn app_hosted:app --reload --port 8000
```

Both expose the same `/ask` endpoint with the same request/response shape, so nothing else in the project (attack module, chaos module, scorecard) needs to change when you switch.

## Setup

```bash
pip install -r requirements.txt
```

You also need Ollama installed with the `llama3.2` model pulled (already done if `ollama list` shows `llama3.2:latest`). No API key or subscription needed, everything runs locally.

Make sure Ollama is running in the background before starting the API (on Windows it usually runs automatically after install, or you can start it with `ollama serve`).

## Run

```bash
# 1. Build the index (run this first, and again any time sample_docs/ changes)
python ingest.py

# 2. Start the API
uvicorn app:app --reload --port 8000
```

## Test it

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"How many days can I work remotely?\"}"
```

(On Windows PowerShell, curl syntax may need adjusting, or just use Postman/Insomnia if curl gives you trouble.)

The response includes both the generated answer and the exact chunks that were
retrieved, so anyone testing attacks or chaos scenarios can see precisely what
context the model was working from.

## For the attack module

- To test document poisoning: add or edit a file in `sample_docs/`, re-run `python ingest.py`, then query `/ask` and check `retrieved_chunks` to see if the poisoned content got pulled in and whether the answer reflects it.
- To test retrieval manipulation: craft chunks designed to score high on cosine similarity for unrelated questions, then check if they show up in `retrieved_chunks` even when they shouldn't be relevant.

## For the chaos module

- The `/ask` endpoint is a normal HTTP call, so latency, timeouts, and failures can be simulated by wrapping calls to it (e.g. with a proxy, or by mocking `retrieve()` to raise exceptions or sleep).
- You can also simulate "model unavailable" by stopping the Ollama process and hitting `/ask`, which should surface as a connection error since `response.raise_for_status()` will raise if Ollama isn't reachable.
- `retrieve.py` and `app.py` are separated on purpose, so you can swap in a broken or slow version of `retrieve()` without touching the API layer.

## Notes

- Retrieval uses TF-IDF + cosine similarity, no external model download needed, kept this way so it's easy to reason about, works offline, and is easy to attack for the demo.
- Answers come from `llama3.2` running locally via Ollama, no subscription or API key needed, and it works even without venue wifi. Answers will be lower quality than a hosted large model, that's an expected tradeoff for zero-cost, zero-dependency setup.
- Chunking is naive fixed-size splitting. Fine for a hackathon demo, not production-grade.
- Tested end to end: `python ingest.py` then `python retrieve.py` correctly returns the remote work policy chunk as the top match for "How many days can I work remotely?"
