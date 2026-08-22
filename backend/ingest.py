"""
Ingestion step for the sample RAG chatbot.

Reads every .txt file in sample_docs/, splits it into small chunks,
embeds each chunk, and saves everything to disk as a simple JSON index.

Run this once before starting the API, and again any time the attack
module wants to test document poisoning (just drop a new/edited .txt
file into sample_docs/ and re-run).
"""

import os
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_DIR = "sample_docs"
INDEX_PATH = "index.json"
VECTORIZER_PATH = "vectorizer.pkl"
CHUNK_SIZE = 300  # characters per chunk, kept small and simple on purpose


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE):
    """Naive fixed-size chunking. Good enough for a hackathon demo."""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def build_index():
    records = []
    for filename in os.listdir(DOCS_DIR):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(DOCS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        for chunk_id, chunk in enumerate(chunk_text(text)):
            records.append({
                "source": filename,
                "chunk_id": chunk_id,
                "text": chunk,
            })

    print(f"Loaded {len(records)} chunks from {DOCS_DIR}/")

    texts = [r["text"] for r in records]
    vectorizer = TfidfVectorizer(stop_words="english")
    embeddings = vectorizer.fit_transform(texts).toarray().tolist()

    for record, embedding in zip(records, embeddings):
        record["embedding"] = embedding

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"Saved index with {len(records)} chunks to {INDEX_PATH}")
    print(f"Saved vectorizer to {VECTORIZER_PATH}")


if __name__ == "__main__":
    build_index()
