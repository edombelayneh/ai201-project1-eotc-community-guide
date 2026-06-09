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

| #   | Source                                            | Description                                                                                                      | URL or location                                                                                |
| --- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | Fasting and Abstinence in the EOTC                | Wikipedia article covering all seven canonical fasts, fasting rules, and optional fasts                          | https://en.wikipedia.org/wiki/Fasting_and_abstinence_in_the_Ethiopian_Orthodox_Tewahedo_Church |
| 2   | The Great Lent                                    | MKVCM article explaining the 55-day fast, its eight weeks, and spiritual significance                            | https://eotcmk.org/e/the-great-lent/                                                           |
| 3   | The Fast of the Apostles                          | MKVCM article covering the meaning, biblical basis, and blessings of the Apostles' Fast                          | https://eotcmk.org/e/the-fast-of-the-apostles-2/                                               |
| 4   | Nineveh's Fast                                    | MKVCM article on the three-day fast commemorating Jonah's preaching to Nineveh                                   | https://eotcmk.org/e/tsome-nenewe/                                                             |
| 5   | The Nativity Fast                                 | MKVCM article on the 43-day Prophets' Fast and its theological meaning                                           | https://eotcmk.org/e/the-nativity-fast/                                                        |
| 6   | Why Did Prophets Fast?                            | MKVCM devotional piece on the spiritual purpose behind the Prophets' Fast                                        | https://eotcmk.org/e/why-did-prophets-fast/                                                    |
| 7   | History of the Ethiopian Orthodox Tewahedo Church | Document covering apostolic origins, the Nine Saints, autocephaly, and diaspora growth                           | Local PDF                                                                                      |
| 8   | Worship in the Ethiopian Orthodox Church          | ethiopianorthodox.org article covering church architecture, liturgy, prayer, and feast days                      | https://www.ethiopianorthodox.org/english/ethiopian/worship.html                               |
| 9   | The Role of the EOTC in Literature and Art        | ethiopianorthodox.org article on Ge'ez literature, the 14 Anaphoras, and Ethiopian iconography                   | https://www.ethiopianorthodox.org/english/ethiopian/literature.html                            |
| 10  | Introduction to Church Sacraments                 | ethiopianorthodox.org document on the definition and administration of the seven sacraments                      | https://www.ethiopianorthodox.org/english/dogma/sacramentintro.html                            |
| 11  | The Bible (EOTC Canon)                            | ethiopianorthodox.org document listing all 81 canonical books and explaining the Sinodos and Didascalia          | https://www.ethiopianorthodox.org/english/canonical/books.html                                 |
| 12  | Mystery of the Holy Trinity                       | MKVCM Dogmatic Theology 2020-21 slide deck covering the Trinity, Holy Spirit, and related heresies               | Local PDF                                                                                      |
| 13  | Mystery of Incarnation                            | MKVCM Dogmatic Theology slide deck covering Christology and the miaphysite one-nature teaching                   | Local PDF                                                                                      |
| 14  | Mystery of Baptism                                | MKVCM Dogmatic Theology slide deck covering baptism as sacrament, infant baptism, and symbols                    | Local PDF                                                                                      |
| 15  | Mystery of Resurrection                           | MKVCM Dogmatic Theology slide deck covering resurrection of the dead, St. Paul's teaching, and the second coming | Local PDF                                                                                      |
| 16  | Saint of the Day — St. Philotheus                 | MKVCM Synaxarium entry for January 24, illustrating the format of daily saint commemorations                     | https://eotcmk.org/e/saint-of-the-day/                                                         |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question | Expected answer |
| --- | -------- | --------------- |
| 1   |          |                 |
| 2   |          |                 |
| 3   |          |                 |
| 4   |          |                 |
| 5   |          |                 |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
