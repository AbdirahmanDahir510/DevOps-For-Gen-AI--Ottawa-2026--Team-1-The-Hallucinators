"""
Quick runner for RAG attack tests.
Run from the backend folder with the venv active and Flask running:
    python run_rag_tests.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))
from security.rag_attacks import run_all

print("=" * 55)
print("  RAG Attack Tests")
print("=" * 55)
print()

start = time.time()
results = run_all()
duration = round(time.time() - start, 1)

for r in results:
    icon = "✅ PASS" if r["status"] == "PASS" else ("❌ FAIL" if r["status"] == "FAIL" else "⚠️  ERROR")
    print(f"{icon}  [{r['severity']}]  {r['name']}")
    print(f"       {r['details'][:120]}")
    print()

passed = sum(1 for r in results if r["status"] == "PASS")
failed = len(results) - passed

print("=" * 55)
print(f"  Results : {passed} passed / {failed} failed  ({duration}s)")
print("=" * 55)
