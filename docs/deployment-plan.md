# Deployment Plan

## HDFC Mutual Fund FAQ Assistant
### Backend → Railway · Frontend → Vercel

> **Last updated:** June 2026

---

## Overview

The application has two independently deployed components:

| Component | Platform | What it runs |
|-----------|----------|-------------|
| **Backend API** | [Railway](https://railway.app) | FastAPI + ChromaDB + Groq LLM (Docker container) |
| **Frontend UI** | [Vercel](https://vercel.com) | Static HTML chat UI |

```mermaid
flowchart LR
    U([User]) --> V[Vercel\nfrontend/index.html]
    V -->|HTTPS POST /ask| R[Railway\nFastAPI API]
    R --> G[Groq API\nllama-3.3-70b]
    R --> DB[(ChromaDB\nPersistent Volume)]
```

**Deployment order:**
1. Deploy **Railway** first → get the public URL
2. Update `RAILWAY_URL` in `frontend/index.html` with that URL
3. Deploy **Vercel** second → frontend calls the live API

---

## Prerequisites

| Requirement | Where to get it |
|-------------|----------------|
| GitHub account with repo pushed | [github.com](https://github.com) |
| Railway account | [railway.app](https://railway.app) |
| Vercel account | [vercel.com](https://vercel.com) |
| Groq API key | [console.groq.com/keys](https://console.groq.com/keys) (free) |

---

## Part 1 — Backend: Railway

### Architecture on Railway

```
Railway Service
├── Docker container (python:3.11-slim)
│   ├── FastAPI app (api/main.py)
│   ├── RAG pipeline (rag/)
│   └── Ingest pipeline (ingest/) ← runs once on first boot
└── Persistent Volume mounted at /app/data
    ├── data/raw/          ← downloaded PDFs + HTML
    ├── data/extracted/    ← extracted text
    ├── data/chunks/       ← chunks.jsonl
    └── data/chroma/       ← ChromaDB vector store
```

**First-boot behaviour:** `start.sh` checks for `data/chroma/chroma.sqlite3`. If not found, it runs the full 4-step ingest pipeline (~3–5 min). On all subsequent deploys the check is skipped — the persistent volume already has the data.

---

### Step 1 — Create a New Railway Project

1. Go to [railway.app/new](https://railway.app/new)
2. Click **Deploy from GitHub repo**
3. Authorise Railway to access your GitHub account
4. Select **RAG-based-Mutual-Fund-FAQ-Chatbot**
5. Railway detects `Dockerfile` automatically — click **Deploy**

---

### Step 2 — Add the Groq API Key

1. In your Railway project, click the service tile
2. Go to **Variables** tab
3. Click **New Variable** and add:

```
GROQ_API_KEY = your_groq_api_key_here
```

> Railway injects `PORT` automatically — no need to set it manually.

---

### Step 3 — Attach a Persistent Volume

Without a persistent volume, the `data/` directory is wiped on every redeploy and the ingest pipeline re-runs from scratch (3–5 min cold start each time). A volume solves this.

1. In your Railway project, click **+ New** → **Volume**
2. Set **Mount Path** to `/app/data`
3. Click **Create Volume**
4. Redeploy the service (Railway prompts you)

Now `data/chroma/` persists across deployments and the ingest pipeline runs exactly once.

---

### Step 4 — Monitor First-Boot Logs

The first deployment runs the ingest pipeline. Watch the logs:

```
========================================
  HDFC Mutual Fund FAQ Assistant
========================================

[1/4] Downloading 21 official sources...
Done! Downloaded: 21, Skipped: 0, Failed: 0

[2/4] Extracting text from PDFs and HTML...
Done! Processed 22 files

[3/4] Chunking into 500-word segments...
Done! Created 500 chunks in data/chunks/chunks.jsonl

[4/4] Embedding into ChromaDB (this takes 2-4 minutes)...
Done! Added 500 chunks to ChromaDB

Ingest pipeline complete. ChromaDB ready.

Starting API server on 0.0.0.0:8080...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

Expected total time: **3–6 minutes** on first boot.

---

### Step 5 — Get Your Railway URL

1. Go to your Railway service → **Settings** tab → **Networking**
2. Click **Generate Domain** (or use a custom domain)
3. Copy the URL — it looks like:

```
https://rag-based-mutual-fund-faq-chatbot.railway.app
```

---

### Step 6 — Test the API

```bash
# Health check
curl https://YOUR-APP.railway.app/health
# → {"status":"ok"}

# Test a structured answer (no LLM needed)
curl -X POST https://YOUR-APP.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the expense ratio of HDFC Flexi Cap Fund?"}'
# → {"status":"answered","answer":"The expense ratio of HDFC Flexi Cap Fund...","citation_url":"","last_updated":"June 2026"}

# Test fund manager
curl -X POST https://YOUR-APP.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is the fund manager of HDFC Flexi Cap Fund?"}'
# → {"status":"answered","answer":"The fund manager of HDFC Flexi Cap Fund is Chirag Setalvad.","..."}
```

Railway backend is now live. ✅

---

## Part 2 — Frontend: Vercel

### Step 7 — Update the Railway URL in the Frontend

Open `frontend/index.html` and find this line (~line 455):

```javascript
const RAILWAY_URL = "https://YOUR-APP.railway.app";
```

Replace `YOUR-APP` with your actual Railway subdomain:

```javascript
const RAILWAY_URL = "https://rag-based-mutual-fund-faq-chatbot.railway.app";
```

Save the file, commit, and push:

```bash
git add frontend/index.html
git commit -m "config: set Railway production API URL"
git push
```

---

### Step 8 — Deploy to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **Import Git Repository**
3. Authorise Vercel to access your GitHub account
4. Select **RAG-based-Mutual-Fund-FAQ-Chatbot**
5. In **Configure Project**:
   - **Framework Preset:** `Other`
   - **Root Directory:** click **Edit** → type `frontend` → click **Continue**
   - **Build Command:** *(leave empty)*
   - **Output Directory:** *(leave empty)*
6. Click **Deploy**

Vercel builds in ~10 seconds and provides a URL like:
```
https://hdfc-mf-faq-assistant.vercel.app
```

---

### Step 9 — Test the Frontend

1. Open the Vercel URL in your browser
2. Select a scheme (e.g. **HDFC Flexi Cap Fund**)
3. Click **Expense Ratio** → should return: `"The expense ratio of HDFC Flexi Cap Fund – Direct Plan is 0.85%."`
4. Click **Fund Manager** → should return: `"The fund manager of HDFC Flexi Cap Fund is Chirag Setalvad."`
5. Click **AUM** → should return: `"The assets under management (AUM) of HDFC Flexi Cap Fund are ₹52,347 crore."`
6. Type `"Should I invest in HDFC Mid Cap Fund?"` → should return a polite refusal

Full app is live. ✅

---

## Part 3 — Post-Deployment Checklist

### Railway

- [ ] Service shows **Active** (green) in the Railway dashboard
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] Logs show "Ingest pipeline complete" (first boot) or "ChromaDB found" (subsequent boots)
- [ ] `GROQ_API_KEY` environment variable is set
- [ ] Persistent volume is attached at `/app/data`

### Vercel

- [ ] Deployment status is **Ready** in Vercel dashboard
- [ ] `RAILWAY_URL` in `frontend/index.html` points to the live Railway URL
- [ ] Scheme selector buttons work
- [ ] FAQ category buttons return correct answers
- [ ] Advisory questions are refused
- [ ] PII inputs are blocked

---

## Environment Variables

### Railway (required)

| Variable | Value | Notes |
|----------|-------|-------|
| `GROQ_API_KEY` | `gsk_...` | From [console.groq.com/keys](https://console.groq.com/keys) |
| `PORT` | Auto-set by Railway | Do not override |

### Vercel

No environment variables required. The Railway URL is hardcoded in `frontend/index.html` as `RAILWAY_URL`.

---

## Deployment Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Builds the Railway container from `python:3.11-slim` |
| `start.sh` | Startup script — runs ingest pipeline if needed, then starts uvicorn |
| `.dockerignore` | Excludes `data/`, `.env`, `__pycache__`, `stitch/` from Docker build |
| `railway.toml` | Railway build + deploy config (Dockerfile builder, health check, restart policy) |
| `frontend/vercel.json` | Vercel static site config (`cleanUrls`, `trailingSlash`) |

---

## Redeployment & Updates

### Updating source code

Push to `main` → Railway and Vercel both auto-deploy via GitHub integration.

```bash
git add .
git commit -m "fix: update expense ratio for HDFC Mid Cap Fund"
git push
```

- **Railway:** rebuilds the Docker image, restarts the container. ChromaDB persists (volume).
- **Vercel:** rebuilds the static site in ~10 seconds.

### Rebuilding ChromaDB from scratch (e.g. new documents added)

```bash
# Option A: Delete the volume data via Railway shell
railway shell
rm -rf data/chroma data/raw data/extracted data/chunks
exit
# Then redeploy — start.sh will re-run the full ingest pipeline

# Option B: SSH into Railway and run ingest manually
railway shell
python ingest/fetcher.py
python ingest/extractor.py
python ingest/chunker.py
python ingest/embedder.py
```

### Rotating the Groq API key

1. Railway dashboard → Service → Variables
2. Update `GROQ_API_KEY`
3. Railway auto-restarts the service — no redeploy needed

---

## Architecture Decisions

### Why Railway for the backend?

- Native Docker support — `Dockerfile` + `start.sh` deploy without any configuration changes
- Persistent volumes keep ChromaDB data across deployments
- Free tier supports the workload (512 MB RAM is sufficient for `all-MiniLM-L6-v2`)
- `$PORT` is injected automatically — uvicorn binds to it directly

### Why Vercel for the frontend?

- Zero-config static HTML deployment from a GitHub repo subfolder
- Global CDN — fast load times worldwide
- Auto-deploy on every `git push`
- Free tier is unlimited for static sites

### Why split deployments?

Separating the backend (compute-heavy, Python) from the frontend (static HTML) means:
- Frontend deploys in seconds; backend deploys independently
- Frontend can be rolled back without affecting the API
- Each tier scales independently

### CORS

The backend sets `allow_origins=["*"]` which accepts requests from the Vercel domain. To restrict this to your Vercel URL only, update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://hdfc-mf-faq-assistant.vercel.app",   # your Vercel URL
        "https://your-custom-domain.com",              # optional custom domain
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Railway build fails | Docker build error | Check build logs; ensure `requirements.txt` is valid |
| "Sorry, I encountered an error" in chat | Frontend can't reach Railway API | Check `RAILWAY_URL` in `frontend/index.html`; check Railway is running |
| Health check timeout (first boot) | Ingest pipeline still running | Wait 5 min; Railway's `healthcheckTimeout = 300` covers this |
| `GROQ_API_KEY` error in logs | Key not set or invalid | Set `GROQ_API_KEY` in Railway Variables tab |
| ChromaDB errors after redeploy | Volume not attached | Attach persistent volume at `/app/data` in Railway |
| Vercel shows 404 | Wrong root directory | Set Root Directory to `frontend` in Vercel project settings |
| CORS error in browser console | `allow_origins` too restrictive | Keep `allow_origins=["*"]` or add your Vercel domain |
| Ingest re-runs on every boot | Volume not mounted | Attach Railway volume at `/app/data` |

---

## Resource Requirements

### Railway (Backend)

| Resource | Requirement | Notes |
|----------|------------|-------|
| RAM | 512 MB | `all-MiniLM-L6-v2` needs ~250 MB; leaves headroom for FastAPI + ChromaDB |
| CPU | 0.5 vCPU | Embedding 500 chunks on first boot takes ~2–4 min; API is lightweight after |
| Storage | 500 MB | Raw PDFs (~200 MB) + ChromaDB index (~50 MB) + extracted text (~20 MB) |
| Network | Outbound | First-boot ingest downloads PDFs from HDFC/AMFI/SEBI servers |

### Vercel (Frontend)

| Resource | Requirement |
|----------|------------|
| Bandwidth | Minimal — single static HTML file (~150 KB) |
| Build time | ~5 seconds |
| CDN | Global (included in free tier) |
