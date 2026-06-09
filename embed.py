"""
embed.py
EOTC Unofficial Guide — Milestone 4: Embedding + Vector Store

Loads chunks.json (produced by ingest.py), embeds each chunk with
all-MiniLM-L6-v2 via sentence-transformers, and stores them in a local
persistent ChromaDB collection with source metadata attached.

Usage:
    python embed.py

Output:
    A persistent ChromaDB collection at chroma_db/, plus a sanity-check query
    ("Abiy Tsom") confirming retrieval returns the right source.
"""

import os
import json

import chromadb
from chromadb.utils import embedding_functions


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

CHUNKS_PATH     = "chunks.json"
CHROMA_PATH     = "chroma_db"          # persistent store (gitignored)
COLLECTION_NAME = "eotc_guide"
EMBED_MODEL     = "all-MiniLM-L6-v2"   # sentence-transformers, per planning.md


# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD CHUNKS
# ─────────────────────────────────────────────────────────────────────────────

def load_chunks(path: str = CHUNKS_PATH) -> list[dict]:
    """Load the chunk list written by ingest.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found — run ingest.py first.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. EMBED + STORE
# ─────────────────────────────────────────────────────────────────────────────

def embed_and_store(chunks: list[dict]):
    """
    Embed every chunk with all-MiniLM-L6-v2 and load it into a fresh local
    ChromaDB collection. Source metadata (source name + id) travels with each
    embedding so retrieved chunks can be cited.

    The collection's embedding function is the same model, so queries at
    retrieval time are embedded identically — no model mismatch.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Recreate from scratch so re-runs don't stack duplicate / stale vectors.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},  # MiniLM vectors compare best by cosine
    )

    ids       = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source":      c["source"],       # document name — for citation
            "source_id":   c["source_id"],
            "chunk_index": c["chunk_index"],   # position within that document
            "char_count":  c["char_count"],
        }
        for c in chunks
    ]

    # Embed + add in batches (keeps memory low and shows progress).
    BATCH = 100
    total = len(chunks)
    for i in range(0, total, BATCH):
        collection.add(
            ids=ids[i:i + BATCH],
            documents=documents[i:i + BATCH],
            metadatas=metadatas[i:i + BATCH],
        )
        print(f"  embedded {min(i + BATCH, total)}/{total} chunks")

    return collection


# ─────────────────────────────────────────────────────────────────────────────
# 3. SANITY CHECK
# ─────────────────────────────────────────────────────────────────────────────

def sanity_check(collection, query: str = "Abiy Tsom", k: int = 4) -> None:
    """
    Query the collection for a known phrase and print the top-k hits with their
    source labels and distances — confirms embeddings landed and retrieval works.
    """
    print("\n" + "=" * 60)
    print(f'SANITY CHECK — query: "{query}"  (top {k})')
    print("=" * 60)
    res = collection.query(query_texts=[query], n_results=k)
    for rank, (doc, meta, dist) in enumerate(
        zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), start=1
    ):
        print(f"\n#{rank}  [{meta['source']}]  cosine distance={dist:.4f}")
        print(f"     {doc[:220].strip()}...")


# ─────────────────────────────────────────────────────────────────────────────
# 4. MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n🔵 EOTC Guide — Embedding + Vector Store")
    print("=" * 60)

    chunks = load_chunks()
    print(f"\n📦 Loaded {len(chunks)} chunks from {CHUNKS_PATH}")

    print(f"\n🧠 Embedding with {EMBED_MODEL} and storing in ChromaDB ({CHROMA_PATH}/)\n")
    collection = embed_and_store(chunks)

    print(f"\n✓ Collection '{COLLECTION_NAME}' now holds {collection.count()} vectors")

    sanity_check(collection)

    print("\n💾 Vector store persisted to", f"{CHROMA_PATH}/")
    print("\nNext step: run retrieve.py to fetch top-k chunks for a query\n")


if __name__ == "__main__":
    main()
