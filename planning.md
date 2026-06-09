# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

My domain is going to be on the Ethiopian Orthodox Christian teachings and belief.

The Ethiopian Orthodox Tewahedo Community Guide makes English-language knowledge about EOTC theology, fasting practices, worship traditions, and saints searchable and conversational for diaspora communities. This knowledge is hard to find otherwise because most authoritative sources exist in Amharic or Ge'ez, and what little exists in English is scattered across official church websites, diaspora parish pages, and community education materials with no single place to search across all of them. A diaspora student trying to understand the Five Pillars of Mystery or the rules of Abiy Tsom currently has to piece together answers from multiple disconnected sources — this system consolidates and cites them in one place.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

All sources are saved as local PDFs under `docs/` and ingested offline — no live web fetching. The "Original source" column records where each PDF was sourced from for citation purposes.

| #   | Source                                            | Description                                                                                                      | Local file (`docs/`)                                                       | Original source                                                                                |
| --- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | Fasting and Abstinence in the EOTC                | Wikipedia article covering all seven canonical fasts, fasting rules, and optional fasts                          | Fasting and abstinence in the Ethiopian Orthodox Tewahedo Church.pdf       | https://en.wikipedia.org/wiki/Fasting_and_abstinence_in_the_Ethiopian_Orthodox_Tewahedo_Church |
| 2   | The Great Lent                                    | MKVCM article explaining the 55-day fast, its eight weeks, and spiritual significance                            | The Great Lent.pdf                                                         | https://eotcmk.org/e/the-great-lent/                                                           |
| 3   | The Fast of the Apostles                          | MKVCM article covering the meaning, biblical basis, and blessings of the Apostles' Fast                          | The Fast of the Apostles.pdf                                               | https://eotcmk.org/e/the-fast-of-the-apostles-2/                                               |
| 4   | Nineveh's Fast                                    | MKVCM article on the three-day fast commemorating Jonah's preaching to Nineveh                                   | Nineveh's Fast.pdf                                                         | https://eotcmk.org/e/tsome-nenewe/                                                             |
| 5   | The Nativity Fast                                 | MKVCM article on the 43-day Prophets' Fast and its theological meaning                                           | The Nativity Fast.pdf                                                      | https://eotcmk.org/e/the-nativity-fast/                                                        |
| 6   | Why Did Prophets Fast?                            | MKVCM devotional piece on the spiritual purpose behind the Prophets' Fast                                        | Why did Prophets fast?.pdf                                                 | https://eotcmk.org/e/why-did-prophets-fast/                                                    |
| 7   | History of the Ethiopian Orthodox Tewahedo Church | Document covering apostolic origins, the Nine Saints, autocephaly, and diaspora growth                           | History of the Ethiopian Orthodox Tewahedo Church.pdf                      | Local PDF                                                                                      |
| 8   | Worship in the Ethiopian Orthodox Church          | ethiopianorthodox.org article covering church architecture, liturgy, prayer, and feast days                      | WORSHIP IN THE ETHIOPIAN ORTHODX CHURCH.pdf                                | https://www.ethiopianorthodox.org/english/ethiopian/worship.html                               |
| 9   | The Role of the EOTC in Literature and Art        | ethiopianorthodox.org article on Ge'ez literature, the 14 Anaphoras, and Ethiopian iconography                   | THE ROLE OF THE ETHIOPIAN ORTHODOX CHURCH IN LITERATURE AND ART.pdf        | https://www.ethiopianorthodox.org/english/ethiopian/literature.html                            |
| 10  | Introduction to Church Sacraments                 | ethiopianorthodox.org document on the definition and administration of the seven sacraments                      | Introduction to Church Sacraments.pdf                                      | https://www.ethiopianorthodox.org/english/dogma/sacramentintro.html                            |
| 11  | The Bible (EOTC Canon)                            | ethiopianorthodox.org document listing all 81 canonical books and explaining the Sinodos and Didascalia          | The Bible.pdf                                                              | https://www.ethiopianorthodox.org/english/canonical/books.html                                 |
| 12  | Mystery of the Holy Trinity                       | MKVCM Dogmatic Theology 2020-21 slide deck covering the Trinity, Holy Spirit, and related heresies               | 04_1st_Year_Dogmatic Theology_Mystery of the Holy Trinity.pdf             | Local PDF                                                                                      |
| 13  | Mystery of Incarnation                            | MKVCM Dogmatic Theology slide deck covering Christology and the miaphysite one-nature teaching                   | 05_1st_Year_Dogmatic Theology_Mystery of Incarnation.pdf                  | Local PDF                                                                                      |
| 14  | Mystery of Baptism                                | MKVCM Dogmatic Theology slide deck covering baptism as sacrament, infant baptism, and symbols                    | 06_1st_Year_Dogmatic Theology_Mystery of Baptism.pdf                      | Local PDF                                                                                      |
| 15  | Mystery of Resurrection                           | MKVCM Dogmatic Theology slide deck covering resurrection of the dead, St. Paul's teaching, and the second coming | 08_1st_Year_Dogmatic Theology_Mystery of Resurrection.pdf                 | Local PDF                                                                                      |
| 16  | Saint of the Day — St. Philotheus                 | MKVCM Synaxarium entry for January 24, illustrating the format of daily saint commemorations                     | Saints.pdf                                                                 | https://eotcmk.org/e/saint-of-the-day/                                                         |
| 17  | Mystery of the Holy Eucharist                     | MKVCM Dogmatic Theology slide deck covering the Eucharist/Holy Communion as sacrament — the fifth pillar of mystery | 07_1st_Year_Dogmatic Theology_Mystery of Holy Communion.pdf               | Local PDF                                                                                      |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 - 500 characters (target 450)

**Overlap:** 50 characters

**Splitter:** LangChain `RecursiveCharacterTextSplitter`

**How the split works:**

The splitter is given a priority list of separators and cuts at the most natural
boundary available, only falling back to the next when a piece is still over the
size limit: `["\n\n", "\n", ". ", " ", ""]` — i.e. page break → line break →
sentence → word → mid-word as a last resort.

Note on the source documents: all 17 are extracted from PDFs with pdfplumber,
which returns text line-by-line joined by single newlines (`\n`). True blank-line
paragraph breaks do not survive extraction — the only `\n\n` present are the page
boundaries inserted when joining pages. So in practice the splitter works from the
line break (`\n`) level downward, preferring to cut at line, then sentence, then
word boundaries. The first separator (`\n\n`) only matters at page edges.

**Why 450 characters fits the documents:**

The documents fall into three types:

**Slide decks (Mysteries series):** Each slide covers one idea with a few bullet
points and scripture references. A ~450 character chunk fits one full slide —
small enough to stay focused, big enough to keep a teaching and its evidence
together.

**Fasting articles (MKVCM blog posts):** Short paragraphs, one fast per document.
This chunk size groups 2–3 related paragraphs together, like a definition plus its
biblical basis.

**Longer documents (History, Worship, Literature & Art):** These have clear section
headings, and a chunk stays roughly within one section.

**Why 50-character overlap:** Because sentences here often run 150–300 characters
while chunks target 450, a chunk usually holds 2–3 sentences and will sometimes cut
mid-sentence at a size boundary. The 50-character overlap repeats the tail of the
previous chunk at the start of the next, so a thought split across a boundary is
recoverable — the overlap, combined with top-k = 4 retrieval, is what compensates
for unavoidable mid-sentence cuts at this chunk size.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

- all-MiniLM-L6-v2 via sentence-transformers

**Top-k:**

- I'll be retrieving k=4 chunks per query. Most of my resources are focused and narrow enough that the chunks are more likely to be related and correct.

**Production tradeoff reflection:**

- The biggest limitation is the 256 token limit, which will be truncated if longer than that. However it is free and local which also helps with the privacy aspect.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                             | Expected answer                                                                                                                                                                                                            |
| --- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | What are the five pillars of mystery in the Ethiopian Orthodox Church?               | The Mystery of the Holy Trinity, the Mystery of the Incarnation, the Mystery of Baptism, the Mystery of the Holy Eucharist, and the Mystery of the Resurrection of the Dead.                                               |
| 2   | How many days is the Great Lent (Abiy Tsom) and how is it structured?                | 55 days, divided into three periods: Tsome Hirkal (8 days), Tsome Arba (40 days), and Tsome Himamat (7 days of Holy Week).                                                                                                 |
| 3   | When are boys and girls baptized in the Ethiopian Orthodox Church?                   | Boys are baptized 40 days after birth and girls 80 days after birth, following the biblical cleansing period in Leviticus 12:1-8.                                                                                          |
| 4   | What foods are allowed during EOTC fasting periods?                                  | Meat, dairy, and eggs are prohibited. Allowed foods include lentils, split peas, potatoes, carrots, and shiro wat. No food or drink is taken before 3:00 pm.                                                               |
| 5   | What are the three sections of an Ethiopian Orthodox church and who can access each? | The Maqdas (Holy of Holies) for priests and deacons only; the Keddist for baptized communicants; and the Qene Mahelet (outer ambulatory) for the general congregation, divided into sections for men, women, and Debteras. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Chunks from the slide decks may split a scripture reference from the teaching point it supports, causing the LLM to retrieve a verse without its theological explanation.

2. Language barrier (some of the information provided mught not contain the amharic version of a work). For example difference in answer between:
   - 'How long is Great Lent?' and 'How long is Abiy Tsome?'
   - Which mean the exact same thing

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

![alt text](<Screenshot 2026-06-08 at 9.02.46 PM.png>)

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

### 1. Document Ingestion

- **Tool:** Claude
- **Input:** My sources table (17 documents, all local PDFs under `docs/`), the spec
  requirement to clean raw text, and my document type (PDFs extracted via pdfplumber)
- **Expected output:** A `load_documents()` function that reads each PDF,
  strips leftover navigation text and repeated footers, and returns clean strings with
  a source label attached to each
- **Verification:** Print the first 500 characters of each loaded document and
  confirm no menu text, slide numbers, or URL artifacts remain

### 2. Chunking

- **Tool:** Claude
- **Input:** My chunking strategy section (400–500 characters, 50 character overlap,
  RecursiveCharacterTextSplitter, separators page break → line → sentence → word)
- **Expected output:** A `chunk_documents()` function that takes the cleaned documents
  and returns a list of chunks, each with its source label preserved as metadata
- **Verification:** Print chunk count, average chunk length, and 3 sample chunks
  from different documents — confirm chunks are coherent and keep their source
  label, and that any mid-sentence cuts at size boundaries are covered by the
  50-character overlap

### 3. Embedding + Vector Store

- **Tool:** Claude
- **Input:** My embedding model section (all-MiniLM-L6-v2, sentence-transformers)
  and vector store choice (ChromaDB), plus my chunk metadata structure
- **Expected output:** An `embed_and_store()` function that embeds each chunk and
  loads it into a local ChromaDB collection with source metadata attached
- **Verification:** Query ChromaDB for a known phrase ("Abiy Tsom") and confirm
  the top result comes from the correct document with the correct source label

### 4. Retrieval

- **Tool:** Claude
- **Input:** My retrieval decisions (top-k = 4, semantic similarity search)
  and the ChromaDB collection structure from step 3
- **Expected output:** A `retrieve()` function that takes a user query, embeds it,
  and returns the top 4 chunks with their source labels
- **Verification:** Run each of my 5 test questions through retrieve() and manually
  check that the returned chunks actually contain the expected answer

### 5. Generation

- **Tool:** Claude
- **Input:** The spec requirement for grounded responses and source citations,
  my Groq model choice (llama-3.3-70b-versatile), and the output of retrieve()
- **Expected output:** A `generate()` function that builds a prompt from the
  retrieved chunks and instructs the LLM to answer only from provided context
  and cite its sources
- **Verification:** Run all 5 test questions end-to-end and check that every answer
  matches the expected answer in my evaluation table and includes at least one
  source citation — flag any response that introduces information not in the chunks
