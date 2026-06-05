# HDFC Mutual Fund FAQ Assistant
## Facts-Only Q&A — Problem Statement & Build Plan

---

## 1. Problem Statement

Retail investors struggle to find factual information about mutual fund schemes.
Details like expense ratio, exit load, minimum SIP, lock-in period, benchmark index,
riskometer classification, and statement download procedures are scattered across
multiple PDFs and websites.

**Goal:** Build a Facts-Only FAQ Assistant that answers questions from official
public sources only, with one citation link per answer, and zero investment advice.

---

## 2. Target Users

- Retail mutual fund investors comparing schemes
- Customer support teams answering repetitive queries
- Content and operations teams needing quick factual lookups

---

## 3. AMC & Schemes in Scope

**AMC:** HDFC Mutual Fund

| Scheme | Category |
|--------|----------|
| HDFC Flexi Cap Fund | Equity — Flexi Cap |
| HDFC Mid Cap Fund | Equity — Mid Cap |
| HDFC Small Cap Fund | Equity — Small Cap |
| HDFC Defence Fund | Equity — Thematic |
| HDFC Silver ETF Fund of Fund | Fund of Funds — Commodity |

---

## 4. Corpus (21 sources — sources.csv)

### HDFC PDFs (16 files)
For each of the 5 schemes, 3 document types are ingested:

| Document | Purpose |
|----------|---------|
| Fund Facts / FOF Book | Expense ratio, exit load, SIP minimum, benchmark |
| KIM (Key Information Memorandum) | Regulatory disclosures, riskometer |
| SID (Scheme Information Document) | Full legal scheme details |

> Note: HDFC scheme web pages are JavaScript-rendered and skipped.
> All factual data in those pages also exists in the PDFs above.

### AMFI HTML (3 pages)
| Page | Purpose |
|------|---------|
| Risk-o-Meter | Riskometer framework explanation |
| Categorization of MF Schemes | SEBI scheme category definitions |
| Introduction to Mutual Funds | Investor education basics |

### SEBI HTML (3 pages)
| Page | Purpose |
|------|---------|
| Investor Education Portal | Central SEBI education hub |
| Investments: Let's Understand | Investment basics education |
| Securities Market: Let's Learn | Securities market education |

---

## 5. What the Chatbot Must Do

### Answer factual questions like:
- What is the expense ratio of HDFC Mid Cap Fund?
- What is the exit load of HDFC Small Cap Fund?
- What is the minimum SIP amount for HDFC Defence Fund?
- What is the benchmark index of HDFC Flexi Cap Fund?
- What is the riskometer classification of HDFC Silver ETF FoF?
- Is there a lock-in period for HDFC Defence Fund?
- How do I download my capital gains statement?
- How do I download my account statement?

### Every answer must:
- Be maximum 3 sentences
- Include exactly 1 citation link (from the corpus)
- End with: `Last updated from sources: <date>`
- Be grounded ONLY in retrieved corpus content

### Refuse these questions politely:
- Should I invest in HDFC Mid Cap Fund?
- Which fund is best for me?
- Will this fund give good returns?
- Compare HDFC Flexi Cap vs Mid Cap (as a recommendation)

### Refusal response must:
- Be polite and explain facts-only limitation
- Include a relevant AMFI or SEBI educational link

### Never accept or display:
- PAN numbers
- Aadhaar numbers
- Account numbers
- OTPs
- Email addresses
- Phone numbers

---

## 6. Technical Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| PDF Extraction | pypdf |
| HTML Extraction | requests + BeautifulSoup |
| Chunking | Custom (500 tokens, 50 overlap) |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Groq API (llama3) |
| Backend | FastAPI |
| Frontend | HTML + CSS + Vanilla JS |
| Testing | pytest |
| Deployment | Railway (Docker) |

---

## 7. Project Folder Structure

```
hdfc-mf-faq/
├── docs/
│   └── PROBLEM_STATEMENT.md       ← this file
├── ingest/
│   ├── fetcher.py                 ← Phase 2: download files
│   ├── extractor.py               ← Phase 3: extract text
│   ├── chunker.py                 ← Phase 4: split into chunks
│   └── embedder.py                ← Phase 5: store in ChromaDB
├── rag/
│   ├── retriever.py               ← Phase 6: query ChromaDB
│   ├── assembler.py               ← Phase 6: build context
│   └── guards.py                  ← Phase 7: advice + PII filter
├── api/
│   └── main.py                    ← Phase 8: FastAPI endpoints
├── frontend/
│   └── index.html                 ← Phase 9: chat UI
├── data/
│   ├── raw/                       ← downloaded PDFs + HTML
│   ├── extracted/                 ← plain text per source
│   └── chunks/                    ← chunks.jsonl
├── tests/
│   ├── test_fetcher.py
│   ├── test_extractor.py
│   ├── test_chunker.py
│   ├── test_embedder.py
│   └── test_rag.py
├── sources.csv                    ← corpus inventory (DONE ✅)
├── requirements.txt
├── .env                           ← GROQ_API_KEY goes here
├── Dockerfile
└── railway.toml
```

---

## 8. Build Phases

---

### ✅ Phase 1 — Corpus Collection (DONE)

**Goal:** Identify and verify all 21 official source URLs.

**Output:** `sources.csv` with 26 rows (21 active URLs, 5 scheme pages skipped).

**Verified:** All 21 URLs are live and return correct content.

---

### 🔲 Phase 2 — Fetcher

**Goal:** Download all 21 sources and save to `data/raw/`.

**File:** `ingest/fetcher.py`

**Logic:**
- Read `sources.csv`
- Skip rows where URL is empty (the 5 scheme pages)
- Download PDFs as `.pdf` files
- Download HTML pages as `.html` files
- Skip if file already exists (idempotent)
- Log success / failure per file

**Output:** 21 files in `data/raw/`

**Test:** Run `python ingest/fetcher.py` — all 21 files downloaded.

---

### 🔲 Phase 3 — Extractor

**Goal:** Convert each downloaded file into clean plain text.

**File:** `ingest/extractor.py`

**Logic:**
- For `.pdf` files → use `pypdf` to extract text page by page
- For `.html` files → use `BeautifulSoup` to extract visible text, strip nav/footer
- Save each as a `.txt` file in `data/extracted/`
- Store metadata: source, type, scheme, url

**Output:** 21 `.txt` files in `data/extracted/`

**Test:** Open a few `.txt` files and confirm readable text with fund details.

---

### 🔲 Phase 4 — Chunker

**Goal:** Split extracted text into overlapping chunks for retrieval.

**File:** `ingest/chunker.py`

**Logic:**
- Read each `.txt` file from `data/extracted/`
- Split into chunks of ~500 tokens with ~50 token overlap
- Each chunk keeps metadata: source URL, scheme name, document type
- Save all chunks to `data/chunks/chunks.jsonl`
  - One JSON object per line: `{"id": ..., "text": ..., "url": ..., "scheme": ..., "type": ...}`

**Output:** `data/chunks/chunks.jsonl`

**Test:** Count chunks — expect roughly 300–600 total across 21 sources.

---

### 🔲 Phase 5 — Embedder

**Goal:** Embed all chunks and store in ChromaDB vector store.

**File:** `ingest/embedder.py`

**Logic:**
- Load all chunks from `chunks.jsonl`
- Use `sentence-transformers` model `all-MiniLM-L6-v2` to embed each chunk
- Upsert into ChromaDB collection named `hdfc_mf_faq`
- Store metadata (url, scheme, type) alongside each embedding

**Output:** ChromaDB collection populated and ready to query.

**Test:** Query "What is the expense ratio?" — confirm relevant chunks returned.

---

### 🔲 Phase 6 — RAG Pipeline

**Goal:** Given a user question, retrieve relevant chunks and generate an answer.

**Files:** `rag/retriever.py`, `rag/assembler.py`

**Logic:**

`retriever.py`:
- Embed the user question
- Query ChromaDB for top 3–5 closest chunks
- Return chunks + their source URLs

`assembler.py`:
- Combine retrieved chunks into a context string
- Pick the single best citation URL (from top chunk)
- Build the final prompt for the LLM

**Prompt structure:**
```
You are a facts-only mutual fund FAQ assistant for HDFC Mutual Fund.
Answer ONLY from the context below. Max 3 sentences.
End every answer with: Source: <url>
End with: Last updated from sources: May 2026

If the question asks for advice, recommendations, or return predictions,
refuse politely and link to https://www.amfiindia.com/investor-corner/knowledge-center

Context:
{retrieved_chunks}

Question: {user_question}
```

**Output:** Answer text with citation URL.

**Test:** Ask "What is the exit load of HDFC Flexi Cap Fund?" — verify correct answer + citation.

---

### 🔲 Phase 7 — Guardrails

**Goal:** Block advisory questions and PII before they reach the LLM.

**File:** `rag/guards.py`

**Two guards:**

**Advisory guard** — detects advice-seeking questions:
```python
ADVICE_KEYWORDS = [
    "should i", "recommend", "best fund", "which fund",
    "worth investing", "good investment", "better fund",
    "suggest", "buy", "sell", "will it grow", "returns"
]
```
If matched → return polite refusal with AMFI/SEBI link. Skip LLM entirely.

**PII guard** — detects sensitive data in user input:
```python
PII_PATTERNS = [
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",   # PAN
    r"\b[0-9]{12}\b",                 # Aadhaar
    r"\b[0-9]{10}\b",                 # phone number
]
```
If matched → return: "This assistant does not accept personal information."

**Test:** Send "Should I buy HDFC Mid Cap Fund?" — verify refusal. Send a fake PAN — verify blocked.

---

### 🔲 Phase 8 — API

**Goal:** Expose the RAG pipeline as a REST API.

**File:** `api/main.py`

**Endpoints:**

```
POST /ask
  Body:  { "question": "What is the expense ratio of HDFC Mid Cap Fund?" }
  Returns: {
    "status": "answered",
    "answer": "The expense ratio of HDFC Mid Cap Fund (Direct Plan) is 0.73%...",
    "citation_url": "https://files.hdfcfund.com/...",
    "last_updated": "May 2026"
  }

GET /health
  Returns: { "status": "ok" }
```

**Also add:**
- CORS middleware (so your frontend can call it)
- Request size limit (prevent very long inputs)

**Test:** Use curl or Postman to hit `POST /ask` — confirm JSON response.

---

### 🔲 Phase 9 — Frontend

**Goal:** Simple chat UI that calls the API and displays answers.

**File:** `frontend/index.html`

**Must include:**
- Welcome line: "HDFC Mutual Fund FAQ — Facts only. No investment advice."
- 3 example question buttons:
  - "What is the expense ratio of HDFC Mid Cap Fund?"
  - "What is the minimum SIP for HDFC Defence Fund?"
  - "How do I download my capital gains statement?"
- Text input + Send button
- Answer display area showing answer + clickable citation link
- Footer: "Last updated from sources: May 2026"
- Loading spinner while waiting for answer

**Test:** Open in browser, ask all 3 example questions — verify answers appear with links.

---

### 🔲 Phase 10 — Testing

**Goal:** Verify the full system works end-to-end.

**Test cases to cover:**

| Question | Expected |
|----------|---------|
| Expense ratio of HDFC Mid Cap Fund? | 0.73% + citation |
| Minimum SIP for HDFC Flexi Cap Fund? | ₹100 + citation |
| Exit load of HDFC Small Cap Fund? | 1% within 1 year + citation |
| Benchmark of HDFC Defence Fund? | Nifty India Defence TRI + citation |
| Riskometer of HDFC Silver ETF FoF? | Very High + citation |
| Should I invest in HDFC Mid Cap Fund? | Polite refusal + AMFI link |
| Which fund is best? | Polite refusal + AMFI link |
| [fake PAN number] | PII blocked message |

**Success criteria:**
- ✅ All factual questions answered correctly with citation
- ✅ 100% refusal of advisory questions
- ✅ PII inputs blocked
- ✅ No third-party sources cited
- ✅ Every answer ≤ 3 sentences
- ✅ "Last updated from sources" present in every answer

---

## 9. Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free key at: https://console.groq.com/keys

---

## 10. How to Run Locally (end-to-end)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download all sources
python ingest/fetcher.py

# 3. Extract text from PDFs + HTML
python ingest/extractor.py

# 4. Chunk the text
python ingest/chunker.py

# 5. Embed and store in ChromaDB
python ingest/embedder.py

# 6. Start the API
uvicorn api.main:app --reload

# 7. Open frontend
open frontend/index.html
```

---

## 11. Current Status

| Phase | Status |
|-------|--------|
| Phase 1 — Corpus Collection | ✅ Done |
| Phase 2 — Fetcher | 🔲 To build |
| Phase 3 — Extractor | 🔲 To build |
| Phase 4 — Chunker | 🔲 To build |
| Phase 5 — Embedder | 🔲 To build |
| Phase 6 — RAG Pipeline | 🔲 To build |
| Phase 7 — Guardrails | 🔲 To build |
| Phase 8 — API | 🔲 To build |
| Phase 9 — Frontend | 🔲 To build |
| Phase 10 — Testing | 🔲 To build |
