# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers the teachings and practices of the **Ethiopian Orthodox Tewahedo Church (EOTC)** — its theology (the five pillars of mystery: Trinity, Incarnation, Baptism, Eucharist, Resurrection), the seven canonical fasts, worship and liturgy, the seven sacraments, the 81-book biblical canon, and the lives of saints.

This knowledge is genuinely hard to find through official channels because most authoritative EOTC sources exist only in **Amharic or Ge'ez**, and the limited English material is scattered across official church websites, diaspora parish pages, Wikipedia, and community Sunday-school course decks — with no single place to search across all of them. A diaspora student trying to understand the Five Pillars of Mystery or the rules of Abiy Tsom currently has to stitch together answers from disconnected sources. This guide consolidates 17 English-language documents into one searchable, citation-backed system aimed at diaspora communities.

---

## Document Sources

All 17 sources are ingested as **local PDFs under `docs/`** (see Spec Reflection for why). The "Origin" column records where each PDF was sourced for citation provenance.

| #   | Source | Type | Origin |
| --- | ------ | ---- | ------ |
| 1   | Fasting and Abstinence in the EOTC | PDF | Wikipedia |
| 2   | The Great Lent | PDF | eotcmk.org |
| 3   | The Fast of the Apostles | PDF | eotcmk.org |
| 4   | Nineveh's Fast | PDF | eotcmk.org |
| 5   | The Nativity Fast | PDF | eotcmk.org |
| 6   | Why Did Prophets Fast? | PDF | eotcmk.org |
| 7   | History of the Ethiopian Orthodox Tewahedo Church | PDF | Course material (native PDF) |
| 8   | Worship in the Ethiopian Orthodox Church | PDF | ethiopianorthodox.org |
| 9   | The Role of the EOTC in Literature and Art | PDF | ethiopianorthodox.org |
| 10  | Introduction to Church Sacraments | PDF | ethiopianorthodox.org |
| 11  | The Bible (EOTC Canon) | PDF | ethiopianorthodox.org |
| 12  | Mystery of the Holy Trinity | PDF | MKVCM Dogmatic Theology deck (native PDF) |
| 13  | Mystery of Incarnation | PDF | MKVCM Dogmatic Theology deck (native PDF) |
| 14  | Mystery of Baptism | PDF | MKVCM Dogmatic Theology deck (native PDF) |
| 15  | Mystery of Resurrection | PDF | MKVCM Dogmatic Theology deck (native PDF) |
| 16  | Saint of the Day — St. Philotheus | PDF | eotcmk.org (Synaxarium) |
| 17  | Mystery of the Holy Eucharist | PDF | MKVCM Dogmatic Theology deck (native PDF) |

Full file paths and original URLs are recorded in `planning.md` and in the `SOURCES` registry in `ingest.py`.

---

## Chunking Strategy

**Chunk size:** 400–500 characters (target 450), via LangChain `RecursiveCharacterTextSplitter` with separators `["\n\n", "\n", ". ", " ", ""]` (page break → line → sentence → word → mid-word as last resort).

**Overlap:** 50 characters.

**Preprocessing before chunking:** Text is extracted from PDFs with `pdfplumber`, then cleaned in `ingest.py`:
- Slide-deck **cover slides and the shared "Course Content" table-of-contents pages are dropped entirely** (they carried no teaching content and the TOC listed every mystery, polluting each deck with the others' topics).
- Site **navigation** (`Home / Amharic / Franćais / Deutsch / Oriental`), **per-page footers** (`EOTC MK US Campus Ministry`, `https://eotcmk.org`), **divider lines** (`____`), bare URLs, Wikipedia citation markers (`[12]`) and the "From Wikipedia…" header are stripped.
- Source **attribution lines are deliberately kept** (e.g. "Written by Professor Sergew Hable Sellassie…") as citation context.

**Why these choices fit your documents:** A ~450-char chunk fits one full slide in the Mystery decks (one teaching + its scripture reference), groups 2–3 related paragraphs in the short fasting articles, and stays roughly within one section of the longer documents. The 50-char overlap matters because sentences here run ~150–300 characters while chunks target 450 — so a chunk usually holds 2–3 sentences and will sometimes cut mid-sentence at a size boundary; the overlap repeats the tail of the previous chunk so a split thought is recoverable, and top-k = 4 retrieval reinforces this. (Note: because pdfplumber returns line-by-line text with no blank-line breaks, true paragraph splitting doesn't occur — the splitter effectively works at the line → sentence level.)

**Final chunk count:** **340 chunks** across 17 documents (avg ~394 characters; range 22–449).

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, stored in a local persistent **ChromaDB** collection using **cosine** distance. It runs locally with no API key, no rate limits, and keeps the corpus private. The same model is attached to the Chroma collection so user queries are embedded identically to the stored chunks at retrieval time.

**Production tradeoff reflection:** The biggest limitation is the model's **256-token input cap** — longer chunks get silently truncated — and its **English-centric training**, which directly caused a failure here: the planning verification query "Abiy Tsom" (romanized Amharic for Great Lent) scored a weak 0.69 cosine distance and matched a bibliography chunk, while the English "Great Lent" scored 0.32. If cost weren't a constraint and I were deploying for real diaspora users (who mix English, transliterated Amharic, and Ge'ez terms), I would weigh a **multilingual model** such as `BGE-M3` or Cohere `embed-multilingual-v3` for cross-lingual matching, and a **longer context window** (e.g. OpenAI `text-embedding-3-large`) so a whole slide or section fits without truncation. The tradeoffs against the current choice are **cost and latency** (API calls vs. free local inference) and **privacy** (sending church/community text to a third party vs. keeping it local) — for a community-facing tool, multilingual accuracy would likely justify those costs.

---

## Grounded Generation

**System prompt grounding instruction:** Generation uses Groq `llama-3.3-70b-versatile` at `temperature=0.1` with this system prompt (in `generate.py`):

> You answer questions about EOTC theology, fasting, worship, sacraments, and saints using ONLY the numbered source passages provided to you in each question.
>
> 1. Use ONLY information found in the provided sources. Do not use outside knowledge.
> 2. If the sources do not contain the answer, reply exactly: "I don't have that information in the provided sources." Do not guess, infer beyond the text, or fill gaps from general knowledge.
> 3. Cite the source name in square brackets after each claim, e.g. [Mystery of Baptism]. If two sources disagree, say so and cite both rather than blending them.
> 4. Be concise and factual. Do not add commentary, opinions, or invented detail.

**Structural choices that enforce grounding (beyond the prompt):**
- Only the **top-4 retrieved chunks** are ever placed in the prompt — the model physically cannot see the rest of the corpus.
- Each context passage is **headed by exactly the bracketed citation token** the model should reproduce (`[Mystery of Baptism]`), so citations come back clean and verifiable rather than invented.
- `temperature=0.1` minimizes creative drift away from the source text.
- This grounding was **verified, not assumed**: on the two questions where retrieval missed (Q1, Q5), the model produced the exact refusal phrase instead of answering from its training data — even though llama-3.3-70b demonstrably knows those answers.

**How source attribution is surfaced in the response:** Three layers. (1) **Inline** `[Source Name]` citations after each claim in the answer text. (2) A deduplicated **"Sources used"** list rendered beneath every answer. (3) In the Gradio UI, a **"View retrieved context"** button under each answer opens a modal showing the exact chunks used, each labeled with its source document, position, and cosine-distance score — so a user can audit precisely what the answer was grounded in.

---

## Evaluation Report

| #   | Question                                                                             | Expected answer                                                                                              | System response (summarized)                                                                                                                                                    | Retrieval quality  | Response accuracy                                                        |
| --- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------ |
| 1   | What are the five pillars of mystery in the EOTC?                                    | Mystery of the Holy Trinity, the Incarnation, Baptism, the Holy Eucharist, and the Resurrection of the Dead. | "I don't have that information in the provided sources." Retrieval pulled Literature/Art and Bible chunks, not the Mystery decks.                                               | Off-target         | Inaccurate (but correctly refused instead of hallucinating)              |
| 2   | How many days is the Great Lent (Abiy Tsom) and how is it structured?                | 55 days, in three periods: Tsome Hirkal (8 days), Tsome Arba (40 days), Tsome Himamat (7 days of Holy Week). | Correctly stated 55 days, cited two sources, named Tsome Hirkal (8 days) — but the full three-period breakdown was not in the retrieved chunks, and it said so.                 | Partially relevant | Partially accurate (correct on 55 days; structure incomplete)            |
| 3   | When are boys and girls baptized in the EOTC?                                        | Boys 40 days after birth, girls 80 days, per the Leviticus 12:1-8 cleansing period.                          | "Boys are baptized 40 days after birth and girls 80 days after birth… [Mystery of Baptism]." Exact match, top retrieved chunk.                                                  | Relevant           | Accurate                                                                 |
| 4   | What foods are allowed during EOTC fasting periods?                                  | No meat, dairy, or eggs; allowed: lentils, split peas, potatoes, carrots, shiro wat; nothing before 3:00 pm. | Correctly listed allowed foods (lentils, split peas, potatoes, carrots, chard, shiro wat) with citations; omitted the explicit meat/dairy/egg prohibition and the 3:00 pm rule. | Relevant           | Partially accurate (allowed foods correct; missing prohibition + timing) |
| 5   | What are the three sections of an Ethiopian Orthodox church and who can access each? | Maqdas (priests/deacons only), Keddist (baptized communicants), Qene Mahelet (general congregation).         | "I don't have that information in the provided sources." The answer exists in the corpus (Worship chunks 11-14) but those chunks did not rank in the top 4.                     | Off-target         | Inaccurate (but correctly refused instead of hallucinating)              |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** 2 of 5 fully grounded and accurate (Q3, Q4 mostly), 1 partial (Q2), 2 misses (Q1, Q5).
Notably, both misses produced the correct grounded refusal rather than a fabricated answer — the
system never hallucinated, even on questions the underlying LLM could answer from general knowledge.
The two failures stem from earlier pipeline stages (cleaning removed the chunk that enumerated the
five pillars; the church-sections answer was split across chunk boundaries and out-ranked by a
generic "church" chunk), not from generation. See Failure Case Analysis below.

---

## Failure Case Analysis

**Question that failed:** Q5 — "What are the three sections of an Ethiopian Orthodox church and who can access each?" (Expected: Maqdas for priests/deacons, Keddist for baptized communicants, Qene Mahelet for the general congregation.)

**What the system returned:** "I don't have that information in the provided sources." The top-4 retrieved chunks were a Literature & Art chunk about church symbols (distance 0.307), a Worship chunk about *service times* (0.364), a bibliography line (0.375), and a Wikipedia taxonomy fragment (0.396) — none of which describe the three sections.

**Root cause (tied to a specific pipeline stage):** This is a **two-stage retrieval failure**, and critically *the answer is in the corpus* — it just wasn't retrievable from the user's phrasing.

1. **Chunking boundary.** The answer lives in the *Worship* document, but the description of the three sections (Maqdes/Sanctuary → Keddist → Qene Mahelet, each with its access rule) is spread across **consecutive chunks 11–14** at the 450-character boundaries. No single chunk holds the full three-part structure, so even a perfect retrieval of one chunk would return only a third of the answer.

2. **Embedding semantic gap.** The query says "three sections … who can access each," but the source chunks never use the words "three sections" — they use the Ge'ez proper nouns ("Maqdes," "Qeddusa Queddusan," "Qene Mahelet") and describe access prose-style. So the query embeds *far* from the right chunks. Meanwhile a generic chunk dense with concrete church nouns (Cross, Censer, Chalice, vestments) scored the **lowest distance of any result in the whole eval (0.307)** and out-ranked the real answer, pushing it outside the top 4. I confirmed the data is indexed by re-querying with the proper nouns ("Maqdas Keddist Qene Mahelet who can enter") — that surfaces Worship chunk 11 at rank 1. This also shows **distance is not a reliable relevance signal**: the most confident result here was the most wrong.

The generation stage then behaved correctly, refusing rather than hallucinating.

**What you would change to fix it:** The root issue is the chunk-boundary split, so I would start with **section-aware chunking** — keeping the full "internal structure of the church" passage in one chunk (or prepending its section heading to each sub-chunk so the structural context travels with it). Secondarily, I'd add a **hybrid lexical + semantic retriever** (BM25 alongside the embeddings) so proper-noun and keyword matches aren't lost when the query phrasing diverges from the source wording, and/or a **multilingual embedding model** so the Ge'ez terms align better. Raising top-k would be a weaker patch since the answer is still fragmented across chunks.

---

## Spec Reflection

**One way the spec helped you during implementation:** The planning.md Chunking Strategy and Retrieval Approach sections gave me **concrete, committed numbers** — 450-character chunks, 50-character overlap, `RecursiveCharacterTextSplitter`, `all-MiniLM-L6-v2`, ChromaDB, top-k = 4 — before I wrote any code. That meant when I used AI to generate `ingest.py`, `embed.py`, and `retrieve.py`, I could hand it the exact spec instead of vague intent, so the generated code matched my design rather than the model's defaults. The sources table also kept all 17 documents tracked end to end, which is how I caught that the five-pillars question needed a source I hadn't ingested yet.

**One way your implementation diverged from the spec, and why:** The spec listed **11 sources as live web pages** (fetched with requests/BeautifulSoup) and said chunking would "split on paragraph breaks first." I diverged on both. First, I switched to ingesting **local PDF copies of every source** for reproducibility — the pipeline shouldn't break if a parish website goes down or changes its markup, and keeping everything local preserves privacy. Second, while implementing that, I discovered `pdfplumber` returns text **line-by-line with no blank-line paragraph breaks**, so "split on paragraph breaks first" was impossible in practice — the splitter actually operates at the line → sentence level. I updated planning.md to document both changes rather than leave the spec inaccurate. I also **added a 17th source** (Mystery of the Holy Eucharist) after realizing the five-pillars evaluation question couldn't be answered without it.

---

## AI Usage

**Instance 1 — Ingestion + cleaning (`ingest.py`)**

- _What I gave the AI:_ My planning.md sources table (17 documents) and Chunking Strategy section (450/50, `RecursiveCharacterTextSplitter`, split on paragraph breaks first), and asked it to build `load_documents()` + chunking.
- _What it produced:_ A loader handling **both web (requests/BeautifulSoup) and PDF** sources, plus the splitter configured to my numbers, with a generic noise-stripping `clean_text()`.
- _What I changed or overrode:_ I directed it to go **PDF-only** (my reproducibility decision), then fixed PDF **filename mismatches** it had guessed wrong (underscores vs. spaces, so every PDF was being silently skipped). After inspecting the *actual* extracted text, I had it add corpus-specific cleaning the generic version missed — **dropping slide-deck cover/TOC pages** (the TOC was contaminating every Mystery deck with the other mysteries' topics) and stripping the ethiopianorthodox.org nav block, which its first regex hadn't matched because of a special character (`Franćais`).

**Instance 2 — Embedding, retrieval, and honest evaluation (`embed.py`, `retrieve.py`)**

- _What I gave the AI:_ My Retrieval Approach section (`all-MiniLM-L6-v2`, ChromaDB, top-k = 4) and asked for an `embed_and_store()` function and a `retrieve()` function, plus the planning verification step ("query for 'Abiy Tsom' and confirm the top result is correct").
- _What it produced:_ Code that attaches the embedding model to the Chroma collection via `SentenceTransformerEmbeddingFunction` (so queries embed identically to stored chunks), batched embedding, and a top-4 retriever returning source metadata.
- _What I changed or overrode:_ When the "Abiy Tsom" verification **failed** (it matched a bibliography chunk), I directed the AI to **characterize the failure honestly instead of tuning the corpus to pass it** — that analysis became my Failure Case material and Embedding tradeoff reflection. I also added an explicit `chunk_index` position field to the metadata (it had only encoded position in the chunk ID), and later **overrode the citation format**: the model was emitting `[Source 1: Mystery of Baptism]`, so I had the context passages re-labeled with just `[Mystery of Baptism]` as the header token so citations came back clean.
