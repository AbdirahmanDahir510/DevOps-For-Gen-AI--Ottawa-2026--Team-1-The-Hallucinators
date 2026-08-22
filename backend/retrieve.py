"""
Retrieval step for the sample RAG chatbot.

Loads the index built by ingest.py, embeds an incoming question,
and returns the top-k most similar chunks using cosine similarity.

This is intentionally simple (no real vector database) so it's easy
for the attack module to reason about and target.
"""

import json
import pickle
import numpy as np

INDEX_PATH = "index.json"
VECTORIZER_PATH = "vectorizer.pkl"


def load_index():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_vectorizer():
    with open(VECTORIZER_PATH, "rb") as f:
        return pickle.load(f)


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        # No overlapping words between query and chunk, similarity is 0
        # (avoids dividing by zero, which would produce NaN -> null in JSON)
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def retrieve(query: str, top_k: int = 3):
    records = load_index()
    vectorizer = load_vectorizer()
    query_embedding = vectorizer.transform([query]).toarray()[0]

    scored = []
    for record in records:
        score = cosine_similarity(query_embedding, record["embedding"])
        scored.append((score, record))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_matches = scored[:top_k]

    return [
        {
            "score": round(score, 4),
            "source": record["source"],
            "chunk_id": record["chunk_id"],
            "text": record["text"],
        }
        for score, record in top_matches
    ]


if __name__ == "__main__":
    # quick manual test
    results = retrieve("How many days can I work remotely?")
    for r in results:
        print(f"[{r['score']}] {r['source']} #{r['chunk_id']}: {r['text'][:80]}...")