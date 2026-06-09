"""
retrieve.py
EOTC Unofficial Guide — Milestone 4: Retrieval

Embeds a user query with the same model used at indexing time (all-MiniLM-L6-v2)
and returns the top-k most similar chunks from ChromaDB, each with its source
label and position so the generation step can cite them.

Per planning.md Retrieval Approach: top-k = 4, semantic similarity search.

Usage:
    python retrieve.py "How many days is the Great Lent?"
    python retrieve.py                 # runs the 5 evaluation questions
"""

import sys

import chromadb
from chromadb.utils import embedding_functions

# Reuse the same store/model config as the embedding step (single source of truth).
from embed import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL

TOP_K = 4   # planning.md: retrieve 4 chunks per query


# ─────────────────────────────────────────────────────────────────────────────
# COLLECTION HANDLE
# ─────────────────────────────────────────────────────────────────────────────

def get_collection():
    """
    Open the persistent ChromaDB collection built by embed.py.

    The collection is reopened with the SAME embedding function it was created
    with, so query text is embedded by the identical all-MiniLM-L6-v2 model —
    query and stored vectors live in the same space.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    try:
        return client.get_collection(COLLECTION_NAME, embedding_function=embed_fn)
    except Exception as e:
        raise RuntimeError(
            f"Could not open collection '{COLLECTION_NAME}' at {CHROMA_PATH}/ — "
            f"run embed.py first. ({e})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# RETRIEVAL
# ─────────────────────────────────────────────────────────────────────────────

def retrieve(query: str, k: int = TOP_K, collection=None) -> list[dict]:
    """
    Return the top-k chunks most semantically similar to `query`.

    Each result is a dict:
        {
          "rank":        1-based rank,
          "text":        chunk text,
          "source":      source document name (for citation),
          "source_id":   source id,
          "chunk_index": position of the chunk within its document,
          "distance":    cosine distance (lower = more similar),
        }
    """
    collection = collection or get_collection()
    res = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    for rank, (doc, meta, dist) in enumerate(
        zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), start=1
    ):
        results.append({
            "rank":        rank,
            "text":        doc,
            "source":      meta["source"],
            "source_id":   meta["source_id"],
            "chunk_index": meta["chunk_index"],
            "distance":    dist,
        })
    return results


def format_results(query: str, results: list[dict]) -> str:
    """Render retrieval results for human inspection."""
    lines = [f'\nQuery: "{query}"', "=" * 60]
    for r in results:
        lines.append(
            f"#{r['rank']}  [{r['source']} · chunk {r['chunk_index']}]  "
            f"distance={r['distance']:.3f}"
        )
        lines.append(f"    {r['text'][:240].strip()}...")
        lines.append("-" * 60)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

# The 5 evaluation questions from planning.md
EVAL_QUESTIONS = [
    "What are the five pillars of mystery in the Ethiopian Orthodox Church?",
    "How many days is the Great Lent (Abiy Tsom) and how is it structured?",
    "When are boys and girls baptized in the Ethiopian Orthodox Church?",
    "What foods are allowed during EOTC fasting periods?",
    "What are the three sections of an Ethiopian Orthodox church and who can access each?",
]


def main():
    collection = get_collection()
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(format_results(query, retrieve(query, collection=collection)))
    else:
        print(f"No query given — running the {len(EVAL_QUESTIONS)} evaluation questions:\n")
        for q in EVAL_QUESTIONS:
            print(format_results(q, retrieve(q, collection=collection)))


if __name__ == "__main__":
    main()
