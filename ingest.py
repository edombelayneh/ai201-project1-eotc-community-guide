"""
ingest.py
EOTC Unofficial Guide — Milestone 3: Document Ingestion + Chunking

Loads all 17 documents (local PDFs), cleans them,
and splits them into chunks of 400-500 characters with 50-character overlap.

Usage:
    python ingest.py

Output:
    Prints a summary of chunks produced and saves chunks to chunks.json
"""

import os
import json
import re

# ── PDF support ───────────────────────────────────────────────────────────────
try:
    import pdfplumber
except ImportError:
    raise ImportError("Run: pip install pdfplumber")

# ── LangChain chunker ─────────────────────────────────────────────────────────
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    raise ImportError("Run: pip install langchain-text-splitters")


# ─────────────────────────────────────────────────────────────────────────────
# 1. SOURCE REGISTRY
#    Every entry is a local PDF saved under docs/. Each has an id, name,
#    type ("pdf"), and a path.
# ─────────────────────────────────────────────────────────────────────────────

SOURCES = [
    {
        "id": 1,
        "name": "Fasting and Abstinence in the EOTC",
        "type": "pdf",
        "location": "docs/Fasting and abstinence in the Ethiopian Orthodox Tewahedo Church.pdf",
    },
    {
        "id": 2,
        "name": "The Great Lent",
        "type": "pdf",
        "location": "docs/The Great Lent.pdf",
    },
    {
        "id": 3,
        "name": "The Fast of the Apostles",
        "type": "pdf",
        "location": "docs/The Fast of the Apostles.pdf",
    },
    {
        "id": 4,
        "name": "Nineveh's Fast",
        "type": "pdf",
        "location": "docs/Nineveh’s Fast.pdf",
    },
    {
        "id": 5,
        "name": "The Nativity Fast",
        "type": "pdf",
        "location": "docs/The Nativity Fast.pdf",
    },
    {
        "id": 6,
        "name": "Why Did Prophets Fast?",
        "type": "pdf",
        "location": "docs/Why did Prophets fast?.pdf",
    },
    {
        "id": 7,
        "name": "History of the Ethiopian Orthodox Tewahedo Church",
        "type": "pdf",
        "location": "docs/History of the Ethiopian Orthodox Tewahedo Church.pdf",
    },
    {
        "id": 8,
        "name": "Worship in the Ethiopian Orthodox Church",
        "type": "pdf",
        "location": "docs/WORSHIP IN THE ETHIOPIAN ORTHODX CHURCH.pdf",
    },
    {
        "id": 9,
        "name": "The Role of the EOTC in Literature and Art",
        "type": "pdf",
        "location": "docs/THE ROLE OF THE ETHIOPIAN ORTHODOX CHURCH IN LITERATURE AND ART.pdf",
    },
    {
        "id": 10,
        "name": "Introduction to Church Sacraments",
        "type": "pdf",
        "location": "docs/Introduction to Church Sacraments.pdf",
    },
    {
        "id": 11,
        "name": "The Bible (EOTC Canon)",
        "type": "pdf",
        "location": "docs/The Bible.pdf",
    },
    {
        "id": 12,
        "name": "Mystery of the Holy Trinity",
        "type": "pdf",
        "location": "docs/04_1st_Year_Dogmatic Theology_Mystery of the Holy Trinity.pdf",
    },
    {
        "id": 13,
        "name": "Mystery of Incarnation",
        "type": "pdf",
        "location": "docs/05_1st_Year_Dogmatic Theology_Mystery of Incarnation.pdf",
    },
    {
        "id": 14,
        "name": "Mystery of Baptism",
        "type": "pdf",
        "location": "docs/06_1st_Year_Dogmatic Theology_Mystery of Baptism.pdf",
    },
    {
        "id": 15,
        "name": "Mystery of Resurrection",
        "type": "pdf",
        "location": "docs/08_1st_Year_Dogmatic Theology_Mystery of Resurrection.pdf",
    },
    {
        "id": 16,
        "name": "Saint of the Day — St. Philotheus",
        "type": "pdf",
        "location": "docs/Saints.pdf",
    },
    {
        "id": 17,
        "name": "Mystery of the Holy Eucharist",
        "type": "pdf",
        "location": "docs/07_1st_Year_Dogmatic Theology_Mystery of Holy Communion.pdf",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. LOADER
# ─────────────────────────────────────────────────────────────────────────────

# Slide-deck pages that carry no teaching content: the cover slide and the
# shared "Course Content" table of contents. The TOC is identical across all
# five Mystery decks and lists every mystery, so leaving it in pollutes each
# deck with the others' topics. Detected on the page's opening text.
_SKIP_PAGE_MARKERS = [
    re.compile(r"Sunday School Department", re.IGNORECASE),  # deck cover slide
    re.compile(r"^\s*Course Content", re.IGNORECASE),        # deck table of contents
]


def _is_boilerplate_page(text: str) -> bool:
    """True if a PDF page is a cover/TOC slide with no substantive content."""
    head = text.strip()[:200]
    return any(p.search(head) for p in _SKIP_PAGE_MARKERS)


def load_pdf(path: str) -> str:
    """
    Extract text from a digitally-created PDF using pdfplumber,
    dropping cover and table-of-contents pages that hold no real content.
    """
    if not os.path.exists(path):
        print(f"  ⚠️  PDF not found: {path} — skipping")
        return ""
    with pdfplumber.open(path) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text and not _is_boilerplate_page(text):
                pages.append(text)
    return "\n\n".join(pages)


# ─────────────────────────────────────────────────────────────────────────────
# 3. CLEANER
# ─────────────────────────────────────────────────────────────────────────────

# Noise that appears mid-text or as a fragment — removed wherever it occurs.
_NOISE_PATTERNS = [
    r"https?://\S+",                                   # any bare URL (incl. eotcmk.org footer)
    r"From Wikipedia, the free encyclopedia",          # Wikipedia header
    r"Jump to navigation\s+Jump to search",            # Wikipedia nav
    r"Ethiopian Orthodox Tewahedo Church\s*Sunday School Department",  # deck header
    r"In the name of the Father, the Son, and the Holy Spirit\s*\.?\s*One God, Amen!",  # deck header prayer
    r"\[\d+\]",                                        # Wikipedia citation markers, e.g. [12]
    r"Retrieved \d+ \w+ \d{4}\.",                      # Wikipedia retrieval dates
    r"©\s*\d{4}.*",                                     # copyright lines
]

_NOISE_RE = re.compile("|".join(_NOISE_PATTERNS), re.IGNORECASE)

# Lines dropped on an exact (case-insensitive) match: site navigation links and
# repeated slide-deck title/footer furniture that appear on every page.
_BOILERPLATE_LINES = {
    # ethiopianorthodox.org site navigation
    "home", "amharic", "franćais", "francais", "français", "deutsch", "oriental",
    "church music", "photo gallery", "video", "links", "calendar",
    # MKVCM Dogmatic Theology slide-deck title block + per-page footer
    "campus ministry", "mahibere kidusan north america center",
    "dogmatic theology", "2020-21", "semester 2", "course content",
    "eotc mk us campus ministry",
    "tinsae",   # stray publisher watermark on ethiopianorthodox.org pages
}


def clean_text(text: str) -> str:
    """
    Strip site navigation, slide-deck headers/footers, divider lines, and other
    boilerplate, then collapse excess whitespace — leaving only substantive text.
    """
    # Remove inline/fragment noise (URLs, citation markers, repeated headers)
    text = _NOISE_RE.sub(" ", text)

    # Collapse multiple spaces into one
    text = re.sub(r" {2,}", " ", text)

    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()

        # Drop very short fragments and bare page numbers
        if len(line) <= 2 or line.isdigit():
            continue

        # Drop exact-match navigation / header / footer lines
        if line.lower() in _BOILERPLATE_LINES:
            continue

        # Drop divider lines made entirely of punctuation (e.g. "_____", "----")
        if re.fullmatch(r"[\W_]+", line):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


# ─────────────────────────────────────────────────────────────────────────────
# 4. CHUNKER
# ─────────────────────────────────────────────────────────────────────────────

CHUNK_SIZE    = 450   # characters  (target midpoint of 400–500)
CHUNK_OVERLAP = 50    # characters

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],  # paragraph → sentence → word
    length_function=len,
)


def chunk_document(text: str, source_name: str, source_id: int) -> list[dict]:
    """
    Split cleaned text into chunks and attach source metadata to each.
    Returns a list of dicts with keys: chunk_id, source_id, source, text, char_count
    """
    raw_chunks = splitter.split_text(text)
    chunks = []
    for i, chunk_text in enumerate(raw_chunks):
        chunks.append({
            "chunk_id":   f"src{source_id:02d}_chunk{i:04d}",
            "source_id":  source_id,
            "source":     source_name,
            "text":       chunk_text.strip(),
            "char_count": len(chunk_text.strip()),
        })
    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# 5. MAIN PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def load_documents() -> list[dict]:
    """Load and clean all documents. Returns list of {source, text} dicts."""
    documents = []
    for source in SOURCES:
        print(f"Loading [{source['id']:02d}] {source['name']} ...")
        raw = load_pdf(source["location"])

        if not raw:
            continue

        cleaned = clean_text(raw)
        documents.append({
            "source_id": source["id"],
            "source":    source["name"],
            "text":      cleaned,
        })
        print(f"  ✓ {len(cleaned):,} characters after cleaning")

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chunk all loaded documents. Returns flat list of chunk dicts."""
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc["text"], doc["source"], doc["source_id"])
        all_chunks.extend(chunks)
        print(f"  → {doc['source']}: {len(chunks)} chunks")
    return all_chunks


def print_sample_chunks(chunks: list[dict], n: int = 3) -> None:
    """Print n sample chunks from different sources for manual inspection."""
    print("\n" + "=" * 60)
    print("SAMPLE CHUNKS (for manual verification)")
    print("=" * 60)
    seen_sources = set()
    printed = 0
    for chunk in chunks:
        if chunk["source"] not in seen_sources and printed < n:
            seen_sources.add(chunk["source"])
            print(f"\nSource : {chunk['source']}")
            print(f"Chunk  : {chunk['chunk_id']}")
            print(f"Length : {chunk['char_count']} characters")
            print(f"Text   :\n{chunk['text'][:300]}...")
            print("-" * 60)
            printed += 1


def main():
    print("\n🔵 EOTC Guide — Document Ingestion + Chunking")
    print("=" * 60)

    # Step 1: Load and clean
    print("\n📄 LOADING DOCUMENTS\n")
    documents = load_documents()
    print(f"\n✓ Loaded {len(documents)} documents")

    # Step 2: Chunk
    print("\n✂️  CHUNKING DOCUMENTS\n")
    chunks = chunk_documents(documents)

    # Step 3: Summary
    char_counts = [c["char_count"] for c in chunks]
    print(f"\n✓ Total chunks : {len(chunks)}")
    print(f"  Avg length   : {sum(char_counts) // len(char_counts)} characters")
    print(f"  Min length   : {min(char_counts)} characters")
    print(f"  Max length   : {max(char_counts)} characters")

    # Step 4: Sample inspection
    print_sample_chunks(chunks, n=3)

    # Step 5: Save to disk for next milestone
    output_path = "chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Chunks saved to {output_path}")
    print("\nNext step: run embed.py to embed and store chunks in ChromaDB\n")


if __name__ == "__main__":
    main()