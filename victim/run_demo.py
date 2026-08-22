"""
Hackathon Demo — Security Test Runner
======================================
Runs all tests against BOTH the vulnerable victim app (port 5001)
and your hardened app (port 5000), then prints a side-by-side comparison.

Usage (with both Flask apps running):
    python victim/run_demo.py

For chaos-only (fastest, no Ollama needed):
    python victim/run_demo.py --chaos-only
"""

import sys
import os
import time
import argparse

# Allow imports from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from security import prompt_injection, leakage_tests, rag_attacks
from chaos import chaos_tests

VICTIM_URL  = "http://localhost:5001"
HARDENED_URL = "http://localhost:5000"

# ANSI colours
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def status_icon(status: str) -> str:
    if status == "PASS":  return f"{GREEN}✓ PASS{RESET}"
    if status == "FAIL":  return f"{RED}✗ FAIL{RESET}"
    return f"{YELLOW}⚠ {status}{RESET}"


def severity_label(sev: str) -> str:
    if sev == "HIGH":   return f"{RED}[HIGH]{RESET}  "
    if sev == "MEDIUM": return f"{YELLOW}[MED] {RESET}"
    return f"{DIM}[LOW]  {RESET}"


def section(title: str):
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}")


def run_suite(label: str, url: str, chaos_only: bool) -> list[dict]:
    """Run all (or chaos-only) tests against a target URL."""
    results = []
    if chaos_only:
        results += chaos_tests.run_all(url)
    else:
        results += prompt_injection.run_all(url)
        results += leakage_tests.run_all(url)
        results += rag_attacks.run_all(url)
        results += chaos_tests.run_all(url)
    return results


def score(results: list[dict]) -> float:
    if not results:
        return 0.0
    passed = sum(1 for r in results if r["status"] == "PASS")
    return round((passed / len(results)) * 100, 1)


def print_results(results: list[dict]):
    for r in results:
        print(f"  {severity_label(r['severity'])}  "
              f"{status_icon(r['status'])}  "
              f"{r['name']:<32}"
              f"{DIM}  {r['details'][:60]}{RESET}")


def print_comparison(victim_results: list[dict], hardened_results: list[dict]):
    section("SIDE-BY-SIDE COMPARISON")

    header = f"  {'Test':<32}  {'Vulnerable App':^16}  {'Hardened App':^16}"
    print(f"\n{BOLD}{header}{RESET}")
    print(f"  {'─'*32}  {'─'*16}  {'─'*16}")

    names = {r["name"] for r in victim_results + hardened_results}
    victim_map   = {r["name"]: r for r in victim_results}
    hardened_map = {r["name"]: r for r in hardened_results}

    for name in sorted(names):
        v = victim_map.get(name, {}).get("status", "N/A")
        h = hardened_map.get(name, {}).get("status", "N/A")

        v_str = f"{RED}✗ FAIL{RESET}" if v == "FAIL" else (f"{GREEN}✓ PASS{RESET}" if v == "PASS" else f"{YELLOW}{v}{RESET}")
        h_str = f"{RED}✗ FAIL{RESET}" if h == "FAIL" else (f"{GREEN}✓ PASS{RESET}" if h == "PASS" else f"{YELLOW}{h}{RESET}")

        print(f"  {name:<32}  {v_str:^25}  {h_str:^25}")


def main():
    parser = argparse.ArgumentParser(description="Hackathon security demo runner")
    parser.add_argument("--chaos-only", action="store_true",
                        help="Run only chaos tests (no Ollama required)")
    parser.add_argument("--victim-only", action="store_true",
                        help="Only attack the victim app, skip hardened")
    args = parser.parse_args()

    mode = "CHAOS ONLY" if args.chaos_only else "FULL SUITE"

    print(f"\n{BOLD}{'=' * 60}")
    print(f"  🔴  HACKATHON SECURITY DEMO — {mode}")
    print(f"{'=' * 60}{RESET}")
    print(f"  Victim app   : {RED}{VICTIM_URL}{RESET}  (deliberately vulnerable)")
    print(f"  Hardened app : {GREEN}{HARDENED_URL}{RESET}  (your app)")
    print()

    # ── Phase 1: Attack the victim ──────────────────────────────────────────
    section(f"PHASE 1 — Attacking Victim App ({VICTIM_URL})")
    print(f"  {YELLOW}Running {'chaos' if args.chaos_only else 'all'} tests…{RESET}\n")

    t0 = time.time()
    victim_results = run_suite("Victim", VICTIM_URL, args.chaos_only)
    victim_time = round(time.time() - t0, 1)
    victim_score = score(victim_results)

    print_results(victim_results)

    v_passed = sum(1 for r in victim_results if r["status"] == "PASS")
    v_failed = len(victim_results) - v_passed
    print(f"\n  Score: {RED}{BOLD}{victim_score}%{RESET}  "
          f"({v_passed} passed / {RED}{v_failed} failed{RESET})  [{victim_time}s]")

    if args.victim_only:
        print(f"\n{BOLD}{'=' * 60}{RESET}")
        return

    # ── Phase 2: Test the hardened app ──────────────────────────────────────
    section(f"PHASE 2 — Testing Hardened App ({HARDENED_URL})")
    print(f"  {GREEN}Running same tests against your app…{RESET}\n")

    t0 = time.time()
    hardened_results = run_suite("Hardened", HARDENED_URL, args.chaos_only)
    hardened_time = round(time.time() - t0, 1)
    hardened_score = score(hardened_results)

    print_results(hardened_results)

    h_passed = sum(1 for r in hardened_results if r["status"] == "PASS")
    h_failed = len(hardened_results) - h_passed
    print(f"\n  Score: {GREEN}{BOLD}{hardened_score}%{RESET}  "
          f"({h_passed} passed / {h_failed} failed)  [{hardened_time}s]")

    # ── Phase 3: Comparison ──────────────────────────────────────────────────
    print_comparison(victim_results, hardened_results)

    # ── Final scorecard ──────────────────────────────────────────────────────
    section("FINAL SCORECARD")
    improvement = round(hardened_score - victim_score, 1)
    print(f"\n  {'Vulnerable App':<20}  {RED}{BOLD}{victim_score:>6}%{RESET}")
    print(f"  {'Hardened App':<20}  {GREEN}{BOLD}{hardened_score:>6}%{RESET}")
    print(f"  {'Improvement':<20}  {CYAN}{BOLD}{'+' if improvement >= 0 else ''}{improvement:>5}%{RESET}")
    print()

    if hardened_score >= 80:
        print(f"  {GREEN}{BOLD}✅  Your app is well-hardened against these attacks.{RESET}")
    elif hardened_score >= 60:
        print(f"  {YELLOW}{BOLD}⚠️   Your app has some protections but needs work.{RESET}")
    else:
        print(f"  {RED}{BOLD}❌  Your app needs more security controls.{RESET}")

    print(f"\n{BOLD}{'=' * 60}{RESET}\n")


if __name__ == "__main__":
    main()
