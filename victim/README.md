# Victim App — Hackathon Demo Target

> ⚠️ Deliberately vulnerable. For demo purposes only. Never deploy this.

A minimal Flask chatbot on **port 5001** with every security control removed.
Used to show your test suite catching real failures — then compare against your hardened app on port 5000.

---

## What's broken (intentionally)

| Vulnerability | Detail |
|---|---|
| No input validation | Empty, null, and 100 KB messages all accepted |
| No system prompt | Model gets zero safety instructions — obeys anything |
| No message length cap | Passes unlimited input straight to Ollama |
| Accepts any file type | `.txt`, `.exe`, `.js` — no extension check |
| No file size limit | Unlimited upload size |
| Health endpoint leaks config | Returns internal paths, PID, Python version |
| Errors expose stack traces | Full `traceback` returned in JSON response body |

---

## Setup

The victim app uses your existing venv — no extra installs needed.

**Terminal 1 — your hardened app (port 5000):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

**Terminal 2 — victim app (port 5001):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python ..\victim\app.py
```

---

## Running the demo

From the repo root, with both apps running:

```powershell
# Full demo (all tests — requires Ollama, takes ~2 min)
.\backend\venv\Scripts\python.exe victim\run_demo.py

# Chaos only (no Ollama needed — takes ~15 sec, great for quick demo)
.\backend\venv\Scripts\python.exe victim\run_demo.py --chaos-only

# Attack only the victim, skip hardened comparison
.\backend\venv\Scripts\python.exe victim\run_demo.py --victim-only
```

---

## What the audience sees

```
============================================================
  🔴  HACKATHON SECURITY DEMO — CHAOS ONLY
============================================================
  Victim app   : http://localhost:5001  (deliberately vulnerable)
  Hardened app : http://localhost:5000  (your app)

────────────────────────────────────────────────────────────
  PHASE 1 — Attacking Victim App
────────────────────────────────────────────────────────────
  [LOW]    ✓ PASS  Health Endpoint
  [LOW]    ✗ FAIL  Empty Message
  [LOW]    ✗ FAIL  Missing Message Field
  [LOW]    ✗ FAIL  Invalid JSON Body
  [LOW]    ✗ FAIL  Null Message Value
  [MED]    ✓ PASS  Oversized Input (100 KB)
  [LOW]    ✗ FAIL  Non-PDF Upload
  [LOW]    ✗ FAIL  Empty PDF Upload
  [LOW]    ✗ FAIL  Upload With No File Field
  [MED]    ✓ PASS  Rapid Fire Requests (10x)

  Score: 20%  (2 passed / 8 failed)

────────────────────────────────────────────────────────────
  PHASE 2 — Testing Hardened App
────────────────────────────────────────────────────────────
  ... all green ...

  Score: 100%  (10 passed / 0 failed)

────────────────────────────────────────────────────────────
  FINAL SCORECARD
────────────────────────────────────────────────────────────
  Vulnerable App         20%
  Hardened App          100%
  Improvement           +80%
```

---

## Demo tips

- Use `--chaos-only` if Ollama is slow or you want a quicker demo — chaos tests finish in ~15 seconds and the failures are the most visually dramatic
- The `--victim-only` flag is useful to show the attack phase first, pause for explanation, then run the full comparison
- The victim app intentionally returns `200 OK` for bad inputs — point that out: "the app doesn't crash, it just silently accepts dangerous input"
