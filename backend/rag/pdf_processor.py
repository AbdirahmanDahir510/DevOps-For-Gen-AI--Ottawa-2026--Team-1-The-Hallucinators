"""
PDF Processor — Stage 3
Extracts text from a PDF and splits it into chunks suitable for embedding.
"""

import os
from pypdf import PdfReader


# ── Tuneable constants ──────────────────────────────────────────────────────
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 100     # characters shared between adjacent chunks
# ───────────────────────────────────────────────────────────────────────────


def extract_text(pdf_path: str) -> str:
    """Read every page of a PDF and return the full text as a single string."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            # extract_text() can return None on some pypdf versions
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append(text)

    if not pages:
        raise ValueError("PDF contains no extractable text.")

    return "\n\n".join(pages)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks.

    Overlap ensures that context spanning a chunk boundary is not lost.
    """
    if not text or not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Advance by (chunk_size - overlap) so adjacent chunks share `overlap` chars
        start += chunk_size - overlap

    return chunks


def process_pdf(pdf_path: str) -> dict:
    """
    Full pipeline: PDF → text → chunks.

    Returns a dict with:
      - text:       full extracted text
      - chunks:     list of text chunks
      - page_count: number of pages in the PDF
      - chunk_count: number of chunks produced
    """
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        page_count = len(reader.pages)

    text = extract_text(pdf_path)
    chunks = chunk_text(text)

    return {
        "text": text,
        "chunks": chunks,
        "page_count": page_count,
        "chunk_count": len(chunks),
    }
