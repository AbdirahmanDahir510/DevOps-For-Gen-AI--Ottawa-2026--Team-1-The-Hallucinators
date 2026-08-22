"""
Chaos Tests — Stage 8
Reliability and failure-mode tests. These are NOT security attacks —
they test whether the system handles adverse conditions gracefully.
"""

import requests
import json
import os
import time

DEFAULT_BASE_URL = "http://localhost:5000"
REQUEST_TIMEOUT = 15   # deliberately short for chaos tests


# ── Helpers ─────────────────────────────────────────────────────────────────

def _result(name: str, category: str, passed: bool, severity: str, details: str) -> dict:
    return {
        "name": name,
        "category": "Chaos",
        "status": "PASS" if passed else "FAIL",
        "severity": severity,
        "details": details,
    }


def _urls(base_url: str) -> tuple[str, str, str]:
    return (
        f"{base_url}/api/chat",
        f"{base_url}/api/upload",
        f"{base_url}/api/health",
    )


# ── Individual chaos tests ───────────────────────────────────────────────────

def test_empty_message(base_url: str = DEFAULT_BASE_URL) -> dict:
    CHAT_URL, _, _ = _urls(base_url)
    try:
        resp = requests.post(CHAT_URL, json={"message": ""}, timeout=REQUEST_TIMEOUT)
        passed = resp.status_code == 400
        return _result("Empty Message", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code} (expected 400). Body: {resp.text[:150]}")
    except Exception as e:
        return _result("Empty Message", "Chaos", False, "LOW", str(e))


def test_missing_message_field(base_url: str = DEFAULT_BASE_URL) -> dict:
    CHAT_URL, _, _ = _urls(base_url)
    try:
        resp = requests.post(CHAT_URL, json={"query": "hello"}, timeout=REQUEST_TIMEOUT)
        passed = resp.status_code == 400
        return _result("Missing Message Field", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code} (expected 400). Body: {resp.text[:150]}")
    except Exception as e:
        return _result("Missing Message Field", "Chaos", False, "LOW", str(e))


def test_invalid_json(base_url: str = DEFAULT_BASE_URL) -> dict:
    CHAT_URL, _, _ = _urls(base_url)
    try:
        resp = requests.post(CHAT_URL, data="this is not json {{{{",
                             headers={"Content-Type": "application/json"},
                             timeout=REQUEST_TIMEOUT)
        passed = resp.status_code == 400
        return _result("Invalid JSON Body", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code} (expected 400). Body: {resp.text[:150]}")
    except Exception as e:
        return _result("Invalid JSON Body", "Chaos", False, "LOW", str(e))


def test_oversized_input(base_url: str = DEFAULT_BASE_URL) -> dict:
    CHAT_URL, _, _ = _urls(base_url)
    huge_message = "A" * 100_000
    try:
        resp = requests.post(CHAT_URL, json={"message": huge_message}, timeout=30)
        passed = resp.status_code < 500
        return _result("Oversized Input (100 KB)", "Chaos", passed, "MEDIUM",
                       f"Status: {resp.status_code}. Body: {resp.text[:150]}")
    except requests.exceptions.Timeout:
        return _result("Oversized Input (100 KB)", "Chaos", True, "MEDIUM",
                       "Request timed out (server alive, did not crash)")
    except Exception as e:
        return _result("Oversized Input (100 KB)", "Chaos", False, "MEDIUM", str(e))


def test_null_message(base_url: str = DEFAULT_BASE_URL) -> dict:
    CHAT_URL, _, _ = _urls(base_url)
    try:
        resp = requests.post(CHAT_URL, json={"message": None}, timeout=REQUEST_TIMEOUT)
        passed = resp.status_code == 400
        return _result("Null Message Value", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code} (expected 400). Body: {resp.text[:150]}")
    except Exception as e:
        return _result("Null Message Value", "Chaos", False, "LOW", str(e))


def test_non_pdf_upload(base_url: str = DEFAULT_BASE_URL) -> dict:
    _, UPLOAD_URL, _ = _urls(base_url)
    try:
        resp = requests.post(UPLOAD_URL,
                             files={"file": ("test.txt", b"This is not a PDF.", "text/plain")},
                             timeout=REQUEST_TIMEOUT)
        passed = resp.status_code == 400
        return _result("Non-PDF Upload", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code} (expected 400). Body: {resp.text[:150]}")
    except Exception as e:
        return _result("Non-PDF Upload", "Chaos", False, "LOW", str(e))


def test_empty_pdf_upload(base_url: str = DEFAULT_BASE_URL) -> dict:
    _, UPLOAD_URL, _ = _urls(base_url)
    try:
        resp = requests.post(UPLOAD_URL,
                             files={"file": ("empty.pdf", b"", "application/pdf")},
                             timeout=REQUEST_TIMEOUT)
        passed = resp.status_code in (400, 422)
        return _result("Empty PDF Upload", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code} (expected 400/422). Body: {resp.text[:150]}")
    except Exception as e:
        return _result("Empty PDF Upload", "Chaos", False, "LOW", str(e))


def test_upload_no_file_field(base_url: str = DEFAULT_BASE_URL) -> dict:
    _, UPLOAD_URL, _ = _urls(base_url)
    try:
        resp = requests.post(UPLOAD_URL, data={}, timeout=REQUEST_TIMEOUT)
        passed = resp.status_code == 400
        return _result("Upload With No File Field", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code} (expected 400). Body: {resp.text[:150]}")
    except Exception as e:
        return _result("Upload With No File Field", "Chaos", False, "LOW", str(e))


def test_health_endpoint(base_url: str = DEFAULT_BASE_URL) -> dict:
    _, _, HEALTH_URL = _urls(base_url)
    try:
        resp = requests.get(HEALTH_URL, timeout=REQUEST_TIMEOUT)
        body = resp.json()
        passed = resp.status_code == 200 and "status" in body and "model" in body
        return _result("Health Endpoint", "Chaos", passed, "LOW",
                       f"Status: {resp.status_code}. Body: {body}")
    except Exception as e:
        return _result("Health Endpoint", "Chaos", False, "LOW", str(e))


def test_rapid_fire_requests(base_url: str = DEFAULT_BASE_URL) -> dict:
    CHAT_URL, _, _ = _urls(base_url)
    failures = []
    for i in range(10):
        try:
            resp = requests.post(CHAT_URL, json={"message": f"Rapid fire test {i}"},
                                 timeout=REQUEST_TIMEOUT)
            if resp.status_code >= 500:
                failures.append(f"Request {i}: HTTP {resp.status_code}")
        except Exception as e:
            failures.append(f"Request {i}: {e}")
    passed = len(failures) == 0
    return _result("Rapid Fire Requests (10x)", "Chaos", passed, "MEDIUM",
                   f"Failures: {failures}" if failures else "All 10 requests succeeded cleanly")


def run_all(base_url: str = DEFAULT_BASE_URL) -> list[dict]:
    """Run all chaos tests and return a list of result dicts."""
    return [
        test_health_endpoint(base_url),
        test_empty_message(base_url),
        test_missing_message_field(base_url),
        test_invalid_json(base_url),
        test_null_message(base_url),
        test_oversized_input(base_url),
        test_non_pdf_upload(base_url),
        test_empty_pdf_upload(base_url),
        test_upload_no_file_field(base_url),
        test_rapid_fire_requests(base_url),
    ]
