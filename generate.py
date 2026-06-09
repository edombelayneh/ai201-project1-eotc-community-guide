"""
generate.py
EOTC Unofficial Guide — Milestone 5: Grounded Generation

Takes a user question, retrieves the top-k chunks (retrieve.py), builds a
grounded prompt, and asks Groq's llama-3.3-70b-versatile to answer ONLY from
the retrieved context with source attribution.

Usage:
    python generate.py "How many days is the Great Lent?"
    python generate.py                 # runs the 5 evaluation questions

Requires GROQ_API_KEY in .env (see .env.example).
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve, get_collection, TOP_K, EVAL_QUESTIONS

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"   # planning.md generation choice


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────────────────────────────────────

# The grounding contract. Answers come ONLY from retrieved context; if the
# context doesn't contain the answer, the model must say so rather than guess.
SYSTEM_PROMPT = """You are the Ethiopian Orthodox Tewahedo Church (EOTC) Community Guide.
You answer questions about EOTC theology, fasting, worship, sacraments, and saints
using ONLY the numbered source passages provided to you in each question.

Rules:
1. Use ONLY information found in the provided sources. Do not use outside knowledge.
2. If the sources do not contain the answer, reply exactly:
   "I don't have that information in the provided sources."
   Do not guess, infer beyond the text, or fill gaps from general knowledge.
3. Cite the source name in square brackets after each claim, e.g. [Mystery of Baptism].
   If two sources disagree, say so and cite both rather than blending them.
4. Be concise and factual. Do not add commentary, opinions, or invented detail.
"""


def build_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into source-labeled passages. Each passage is headed
    by exactly the bracketed citation token the model should reproduce, e.g.
    "[Mystery of Baptism]", so citations come back clean and consistent.
    """
    blocks = []
    for c in chunks:
        blocks.append(f"[{c['source']}]\n{c['text'].strip()}")
    return "\n\n".join(blocks)


def build_user_prompt(question: str, context: str) -> str:
    return (
        f"Sources:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the sources above. Cite by copying the exact bracketed "
        f"label shown above each passage (e.g. [Mystery of Baptism]) — do not invent "
        f"or renumber labels."
    )


# ─────────────────────────────────────────────────────────────────────────────
# GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate(question: str, k: int = TOP_K, collection=None) -> dict:
    """
    Retrieve context for `question` and generate a grounded answer.

    Returns:
        {
          "question": the question,
          "answer":   the model's grounded answer (with inline [Source] citations),
          "sources":  unique source document names used as context,
          "chunks":   the raw retrieved chunks (for inspection / the UI),
        }
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set — copy .env.example to .env and add your key.")

    chunks = retrieve(question, k=k, collection=collection)
    context = build_context(chunks)

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(question, context)},
        ],
        temperature=0.1,   # low: stick to the sources, minimal creativity
        max_tokens=600,
    )
    answer = response.choices[0].message.content.strip()

    # Deduplicate source names, preserving retrieval order, for the source list.
    sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {"question": question, "answer": answer, "sources": sources, "chunks": chunks}


def format_answer(result: dict) -> str:
    """Render an answer + source list for the terminal (output format: answer + sources)."""
    lines = [result["answer"], "", "Sources:"]
    lines += [f"  - {s}" for s in result["sources"]]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    collection = get_collection()
    questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else EVAL_QUESTIONS
    for q in questions:
        print("\n" + "=" * 70)
        print(f"Q: {q}")
        print("=" * 70)
        print(format_answer(generate(q, collection=collection)))


if __name__ == "__main__":
    main()
