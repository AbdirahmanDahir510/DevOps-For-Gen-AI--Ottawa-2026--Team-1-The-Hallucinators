"""
Embeddings — Stage 4
Creates and stores sentence embeddings in ChromaDB.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

# ── Constants ───────────────────────────────────────────────────────────────
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # fast, small, good quality
# ───────────────────────────────────────────────────────────────────────────

# Module-level singletons — loaded once, reused across requests
_model: SentenceTransformer | None = None
_client: chromadb.PersistentClient | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _client, _collection
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
    if _collection is None:
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_chunks(doc_id: str, filename: str, chunks: list[str]) -> int:
    """
    Embed a list of text chunks and store them in ChromaDB.

    Parameters
    ----------
    doc_id   : unique identifier for this document (e.g. UUID)
    filename : original filename, stored as metadata
    chunks   : list of text strings to embed

    Returns the number of chunks stored.
    """
    if not chunks:
        return 0

    model = _get_model()
    collection = _get_collection()

    embeddings = model.encode(chunks, show_progress_bar=False).tolist()

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "filename": filename, "chunk_index": i}
                 for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)


def delete_document(doc_id: str) -> int:
    """Remove all chunks belonging to a document from ChromaDB."""
    collection = _get_collection()

    results = collection.get(where={"doc_id": doc_id})
    ids_to_delete = results.get("ids", [])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)

    return len(ids_to_delete)


def list_documents() -> list[dict]:
    """
    Return one entry per unique document stored in ChromaDB.
    Each entry: { doc_id, filename, chunk_count }
    """
    collection = _get_collection()
    results = collection.get(include=["metadatas"])

    seen: dict[str, dict] = {}
    for meta in results.get("metadatas", []):
        doc_id = meta["doc_id"]
        if doc_id not in seen:
            seen[doc_id] = {"doc_id": doc_id, "filename": meta["filename"], "chunk_count": 0}
        seen[doc_id]["chunk_count"] += 1

    return list(seen.values())


def get_collection_count() -> int:
    """Return the total number of chunks stored."""
    return _get_collection().count()
