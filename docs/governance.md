# Governance

## Purpose

This document describes the policies governing the use, operation, and maintenance of the AI Security Chatbot.

---

## Acceptable Use

- The chatbot is intended for internal security research and document Q&A.
- Users may upload PDF documents related to security policies, reports, and guidelines.
- The system must not be used to generate harmful, illegal, or deceptive content.
- Users must not attempt to extract system prompts, bypass safety controls, or test the system with actual production credentials.

---

## Document Upload Policy

| Rule | Detail |
|---|---|
| Accepted formats | PDF only |
| Maximum file size | 20 MB |
| Prohibited content | Documents containing real credentials, PII, or classified material |
| Retention | Documents are stored locally in ChromaDB and the `uploads/` directory |
| Deletion | Any user may delete any uploaded document via the dashboard or `DELETE /api/documents/<id>` |

---

## Data Handling

- All data (documents, embeddings, chat messages) is processed and stored locally.
- No data is transmitted to external services. Ollama runs entirely on the local machine.
- The `.env` file (if used) must never be committed to version control.
- The `uploads/` and `chroma_db/` directories must be added to `.gitignore`.

---

## Security Testing

- Security and chaos tests should be run before any deployment or major code change.
- A passing score of 80% or above across all categories is the target threshold.
- Failed HIGH severity tests must be investigated before the system is considered production-ready.

---

## Failure Handling

| Failure | Expected Behaviour |
|---|---|
| Ollama unavailable | API returns HTTP 503 with a descriptive message |
| PDF has no text | API returns HTTP 422 with a descriptive message |
| Invalid JSON | API returns HTTP 400 |
| Oversized input | API returns HTTP 413 |
| Test runner error | API returns HTTP 500 with a log entry |

---

## Maintenance

- Dependencies should be pinned in `requirements.txt` and updated regularly.
- The `sentence-transformers` model (`all-MiniLM-L6-v2`) is downloaded on first run and cached locally.
- ChromaDB persists to `backend/chroma_db/`. Back up this directory if document continuity matters.
