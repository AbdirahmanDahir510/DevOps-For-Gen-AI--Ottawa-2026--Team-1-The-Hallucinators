# AI Usage Disclosure

## What AI is used in this system?

This system uses **Llama 3.2**, a large language model developed by Meta, run locally via **Ollama**.

No external AI API (OpenAI, Anthropic, Google, etc.) is used. All inference happens on the local machine.

---

## What does the AI do?

- Answers user questions in natural language.
- When PDF documents have been uploaded, answers are grounded in the retrieved document context (RAG).
- The AI does not take any external actions, send data anywhere, or make autonomous decisions.

---

## What data is sent to the AI?

Each request to the AI consists of:
1. A system prompt (internal instructions, not user-visible).
2. Optionally, retrieved document context (chunks from uploaded PDFs).
3. The user's message.

No persistent memory is maintained between sessions. Each request is stateless.

---

## What are the AI's known limitations?

- It can generate plausible but incorrect information (hallucination).
- It may not follow safety instructions under adversarial prompt conditions.
- It has a knowledge cutoff and may not know about recent events.
- Responses are non-deterministic and may vary between runs.

---

## How is the AI tested for safety?

An automated test suite runs 20 tests across four categories:

- **Prompt Injection** — tests whether the model follows malicious instructions embedded in user input.
- **Data Leakage** — tests whether the model reveals system prompt contents.
- **RAG Security** — tests whether the model treats injected document content as instructions.
- **Chaos** — tests whether the API handles adverse conditions gracefully.

Results are visible in the Security Dashboard.

---

## Who is responsible for this system?

This system was built by Team 1 — The Hallucinators as part of the DevOps for Gen AI course, Ottawa 2026.
