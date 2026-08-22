"""
Retriever — Stage 4
Queries ChromaDB for chunks relevant to a user question,
then builds a context string for Ollama.
"""

from sentence_transformers import SentenceTransformer
from rag.embeddings import _get_model, _get_collection

# ── Constants ───────────────────────────────────────────────────────────────
TOP_K = 5               # number of chunks to retrieve
MIN_RELEVANCE = 0.25    # cosine distance threshold (lower = more similar)
# ───────────────────────────────────────────────────────────────────────────


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Retrieve the most relevant document chunks for a query.

    Returns a list of dicts:
      { text, filename, doc_id, chunk_index, distance }
    Sorted by ascending distance (most relevant first).
    """
    model = _get_model()
    collection = _get_collection()

    if collection.count() == 0:
        return []

    query_embedding = model.encode([query], show_progress_bar=False).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for text, meta, dist in zip(documents, metadatas, distances):
        if dist <= (1.0 - MIN_RELEVANCE):   # cosine distance: 0=identical, 1=opposite
            chunks.append({
                "text": text,
                "filename": meta.get("filename", "unknown"),
                "doc_id": meta.get("doc_id", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "distance": round(dist, 4),
            })

    return chunks


def build_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a context block for the LLM prompt.
    Each chunk is labelled with its source filename.
    """
    if not chunks:
        return ""

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Source: {chunk['filename']}, chunk {chunk['chunk_index']}]\n{chunk['text']}")

    return "\n\n---\n\n".join(parts)


def has_documents() -> bool:
    """Return True if any documents are stored in ChromaDB."""
    try:
        return _get_collection().count() > 0
    except Exception:
        return False
