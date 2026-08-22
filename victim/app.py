"""
Victim App — Deliberately Vulnerable AI Chatbot
================================================
Runs on port 5001.  DO NOT use in production.

Every security control that exists in the real app (backend/app.py)
has been intentionally removed here so the test suite catches real failures.

Vulnerabilities built in:
  1.  No input validation  — empty, null, huge messages all accepted
  2.  No system prompt     — model gets zero instructions, obeys anything
  3.  No message length cap
  4.  /api/upload accepts any file type, any size
  5.  /api/health leaks internal config (port, paths, model details)
  6.  Prompt injections passed straight to Ollama with no guardrails
  7.  No CORS restrictions (accepts from any origin)
  8.  Errors expose full stack traces in the response body
"""

import os, sys, traceback, uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests as http

app = Flask(__name__)
CORS(app)   # allow everything — no origin restriction

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

# Use same uploads dir as the real app for simplicity
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "uploads", "_victim")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── VULNERABILITY 5: health leaks internal paths and config ──────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "model": MODEL_NAME,
        "ollama_url": OLLAMA_URL,          # leaks internal URL
        "upload_dir": UPLOAD_DIR,          # leaks filesystem path
        "python": sys.version,             # leaks runtime version
        "pid": os.getpid(),                # leaks process ID
    })


# ── VULNERABILITY 1, 2, 3, 6: no validation, no system prompt ───────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    # VULNERABILITY 1: no validation — accept anything including null/empty
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    # VULNERABILITY 2: no system prompt — the model gets no safety instructions
    # VULNERABILITY 6: user input passed directly to Ollama as the full prompt
    try:
        resp = http.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    # No system message at all — attacker controls everything
                    {"role": "user", "content": str(message)},
                ],
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        answer = resp.json()["message"]["content"]
        return jsonify({
            "response": answer,
            # VULNERABILITY 5: leaks internal config in every response
            "model": MODEL_NAME,
            "ollama": OLLAMA_URL,
        })

    except http.exceptions.ConnectionError:
        # VULNERABILITY 8: full traceback in response
        return jsonify({"error": "Ollama unreachable", "trace": traceback.format_exc()}), 503
    except Exception as exc:
        # VULNERABILITY 8: exposes internal error details
        return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500


# ── VULNERABILITY 4: upload accepts any file, any size, no validation ────────
@app.route("/api/upload", methods=["POST"])
def upload():
    # VULNERABILITY 4a: no check that 'file' field exists
    file = request.files.get("file")
    if not file:
        # Still returns 200 — no error
        return jsonify({"message": "No file received", "chunks": 0})

    # VULNERABILITY 4b: accepts any file type — .exe, .txt, .js, anything
    # VULNERABILITY 4c: no size limit
    filename = file.filename or f"upload_{uuid.uuid4().hex}"
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    return jsonify({
        "message": f"Saved {filename}",
        "path": save_path,   # VULNERABILITY 5: leaks full filesystem path
        "size": os.path.getsize(save_path),
    })


# ── VULNERABILITY 4d: /api/documents just lists the upload dir contents ──────
@app.route("/api/documents", methods=["GET"])
def documents():
    files = []
    try:
        for f in os.listdir(UPLOAD_DIR):
            full = os.path.join(UPLOAD_DIR, f)
            files.append({"filename": f, "path": full, "size": os.path.getsize(full)})
    except Exception:
        pass
    return jsonify({"documents": files, "total": len(files)})


if __name__ == "__main__":
    print("=" * 50)
    print("  ⚠️   VICTIM APP — DELIBERATELY VULNERABLE")
    print("  ⚠️   DO NOT USE IN PRODUCTION")
    print("=" * 50)
    print(f"  Port   : 5001")
    print(f"  Model  : {MODEL_NAME}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=True)
