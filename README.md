# 🤖 AI Security Chatbot — The Hallucinators

> DevOps for GenAI · Ottawa Hackathon Series 2026 · Team 1

**Project Leader:** Abdirahman Dahir

**Team:** Suleiman Amin · Mohamedtaha Souida · Abdimalik Dahir · Alex Vu

---

## What is this?

A fully local, document-aware AI security chatbot built with React, Flask, Ollama, and RAG — with an integrated security and chaos testing dashboard.

```
React Frontend
      │
      ▼
Flask Backend ──► Ollama (Llama 3.2)
      │
      ▼
   RAG Pipeline
      │
 PDF Upload ──► Text Extraction ──► Embeddings ──► ChromaDB
                                                       │
                                                  Retrieval
                                                       │
                                               Context + Llama
                                                       │
                                                    Answer
```

Upload any PDF. Ask questions about it. The chatbot retrieves only the relevant chunks and grounds its answer in your document instead of making things up.

---

## Features

| Feature | Description |
|---|---|
| 💬 Chat | Conversational AI powered by Llama 3.2 running locally via Ollama |
| 📄 RAG | Upload PDFs, index them, chat with their contents |
| 🛡️ Security Tests | 8 automated tests — prompt injection and data leakage |
| 🔴 RAG Security | Tests for injection and poisoning via malicious documents |
| ⚡ Chaos Tests | 10 reliability tests — bad inputs, oversized payloads, missing fields |
| 📊 Dashboard | Live security score ring, category bars, expandable test results |

---

## Project Structure

```
├── backend/
│   ├── app.py                  # Flask API — all endpoints
│   ├── requirements.txt
│   ├── uploads/                # Saved PDF files (gitignored)
│   ├── chroma_db/              # ChromaDB vector store (gitignored)
│   │
│   ├── rag/
│   │   ├── pdf_processor.py    # PDF → text → chunks
│   │   ├── embeddings.py       # ChromaDB + sentence-transformers
│   │   └── retriever.py        # Cosine similarity retrieval
│   │
│   ├── security/
│   │   ├── prompt_injection.py # 4 injection tests
│   │   ├── leakage_tests.py    # 4 data leakage tests
│   │   ├── rag_attacks.py      # 2 RAG security tests
│   │   └── test_runner.py      # Orchestrates all suites
│   │
│   └── chaos/
│       └── chaos_tests.py      # 10 reliability tests
│
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── Chatbot.jsx
│       │   ├── DocumentUpload.jsx
│       │   ├── SecurityDashboard.jsx
│       │   ├── SecurityScore.jsx
│       │   └── TestResults.jsx
│
└── docs/
    ├── threat-model.md
    ├── governance.md
    ├── system-card.md
    ├── ai-usage-disclosure.md
    ├── security-scorecard.md
    ├── sample-security-policy.pdf   # Example PDF for testing
    ├── ai-security-faq.pdf          # Example PDF for testing
    └── generate_sample_pdf.py       # Script to regenerate example PDFs
```

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| Llama 3.2 | — | `ollama pull llama3.2` |

---

## Setup

### 1. Clone and enter the repo

```bash
git clone <repo-url>
cd DevOps-For-Gen-AI--Ottawa-2026--Team-1-The-Hallucinators
```

### 2. Start Ollama

```bash
ollama serve
ollama pull llama3.2
```

### 3. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Backend runs at **http://localhost:5000**

> First run downloads the `all-MiniLM-L6-v2` embedding model (~90 MB) and caches it locally.

### 4. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend + Ollama status |
| `POST` | `/api/chat` | Send a message, get an AI response |
| `POST` | `/api/upload` | Upload a PDF for indexing |
| `GET` | `/api/documents` | List all indexed documents |
| `DELETE` | `/api/documents/<id>` | Delete a document and its chunks |
| `GET` | `/api/tests` | List available test suites |
| `POST` | `/api/tests/run` | Run a test suite |
| `GET` | `/api/security/score` | Get the last security score |

**Run tests:**
```bash
curl -X POST http://localhost:5000/api/tests/run \
  -H "Content-Type: application/json" \
  -d '{"suite": "all"}'
```

Suites: `all` · `security` · `rag` · `chaos`

---

## Testing

### Upload the example PDF

```powershell
# With Flask running:
.\backend\venv\Scripts\python.exe docs\test_upload.py
```

### Example questions to ask the chatbot

After uploading `ai-security-faq.pdf`:

- *"What is prompt injection?"*
- *"How should passwords be stored?"*
- *"What is the OWASP Top 10 for LLM applications?"*
- *"What email do I use to report a security incident?"*

---

## Security Test Categories

| Category | Tests | What it checks |
|---|---|---|
| Prompt Injection | 4 | Jailbreaks, role overrides, token manipulation |
| Data Leakage | 4 | System prompt extraction, config disclosure |
| RAG Security | 2 | Injected instructions in PDFs, data poisoning |
| Chaos | 10 | Bad inputs, oversized payloads, empty files, rapid requests |

---

## Documentation

All design and governance documentation is in `docs/`:

- [`threat-model.md`](docs/threat-model.md) — threats, attack vectors, controls, residual risks
- [`system-card.md`](docs/system-card.md) — components, limitations, security controls
- [`governance.md`](docs/governance.md) — acceptable use, data handling, failure policy
- [`ai-usage-disclosure.md`](docs/ai-usage-disclosure.md) — what AI is used and how
- [`security-scorecard.md`](docs/security-scorecard.md) — test definitions and score targets

---

## Notes

- All inference is **100% local** — no data leaves your machine
- The `uploads/` and `chroma_db/` directories are gitignored
- Never commit `.env` files or API keys
- The security tests are designed to run against a **live local instance** of the backend
