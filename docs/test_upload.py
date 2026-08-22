"""
Directly tests the /api/upload endpoint with the sample PDF.
Run from the repo root while Flask is running:
    python docs/test_upload.py
"""

import requests
import os
import sys

PDF_PATH = os.path.join(os.path.dirname(__file__), "sample-security-policy.pdf")
UPLOAD_URL = "http://localhost:5000/api/upload"


def main():
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)

    print(f"File size on disk : {os.path.getsize(PDF_PATH):,} bytes")
    print(f"Uploading to      : {UPLOAD_URL}")
    print()

    with open(PDF_PATH, "rb") as f:
        response = requests.post(
            UPLOAD_URL,
            files={"file": ("sample-security-policy.pdf", f, "application/pdf")},
            timeout=30,
        )

    print(f"HTTP status : {response.status_code}")
    print(f"Response    : {response.json()}")

    if response.status_code == 200:
        data = response.json()
        print()
        print("SUCCESS")
        print(f"  Pages  : {data['page_count']}")
        print(f"  Chunks : {data['chunk_count']}")
    else:
        print()
        print("FAILED — check the Flask terminal for the full traceback")


if __name__ == "__main__":
    main()
