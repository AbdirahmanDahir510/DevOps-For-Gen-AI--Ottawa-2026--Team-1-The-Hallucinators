"""
Test Runner — Stage 9
Orchestrates all security and chaos tests, aggregates scores,
and returns structured results ready for the React dashboard.
"""

import time
from security import prompt_injection, rag_attacks, leakage_tests
from chaos import chaos_tests


# ── Score calculation ────────────────────────────────────────────────────────

def _score(results: list[dict]) -> float:
    """Return a 0-100 score based on the fraction of passing tests."""
    if not results:
        return 100.0
    passed = sum(1 for r in results if r["status"] == "PASS")
    return round((passed / len(results)) * 100, 1)


# ── Public API ───────────────────────────────────────────────────────────────

def run_all_tests() -> dict:
    """
    Run every test suite and return a unified report:

    {
        total: int,
        passed: int,
        failed: int,
        scores: {
            security: float,
            rag: float,
            chaos: float,
            overall: float
        },
        results: [ { name, category, status, severity, details }, ... ],
        duration_seconds: float
    }
    """
    start = time.time()

    injection_results = prompt_injection.run_all()
    leakage_results = leakage_tests.run_all()
    rag_results = rag_attacks.run_all()
    chaos_results = chaos_tests.run_all()

    security_results = injection_results + leakage_results
    all_results = security_results + rag_results + chaos_results

    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = total - passed

    scores = {
        "security": _score(security_results),
        "rag": _score(rag_results),
        "chaos": _score(chaos_results),
        "overall": _score(all_results),
    }

    duration = round(time.time() - start, 2)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "scores": scores,
        "results": all_results,
        "duration_seconds": duration,
    }


def run_security_tests() -> dict:
    """Run only security tests (injection + leakage)."""
    start = time.time()
    results = prompt_injection.run_all() + leakage_tests.run_all()
    return {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] != "PASS"),
        "scores": {"security": _score(results), "overall": _score(results)},
        "results": results,
        "duration_seconds": round(time.time() - start, 2),
    }


def run_rag_tests() -> dict:
    """Run only RAG attack tests."""
    start = time.time()
    results = rag_attacks.run_all()
    return {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] != "PASS"),
        "scores": {"rag": _score(results), "overall": _score(results)},
        "results": results,
        "duration_seconds": round(time.time() - start, 2),
    }


def run_chaos_tests() -> dict:
    """Run only chaos tests."""
    start = time.time()
    results = chaos_tests.run_all()
    return {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] != "PASS"),
        "scores": {"chaos": _score(results), "overall": _score(results)},
        "results": results,
        "duration_seconds": round(time.time() - start, 2),
    }
