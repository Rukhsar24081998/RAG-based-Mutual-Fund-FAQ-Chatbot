# Changelog

All notable changes to the HDFC Mutual Fund FAQ Assistant project.

---

## [2.0.0] - 2026-06-06

### ✨ Added - Automated Data Refresh System

**Major Feature:** Implemented automated monthly data refresh to keep mutual fund information current.

#### New Components

1. **Monthly Data Refresh Job** (`scheduler/jobs.py`)
   - Automatically runs on the 1st of every month at 02:00 AM IST
   - Executes full data pipeline: fetch → extract → chunk → embed
   - Logs results and errors for monitoring
   - Takes ~5-10 minutes to complete

2. **Manual Refresh API** (`api/main.py`)
   - New endpoint: `POST /scheduler/refresh-now`
   - Allows administrators to trigger immediate data refresh
   - Returns detailed execution results
   - Useful for emergency updates

3. **Enhanced Scheduler Status** (`api/main.py`)
   - Improved `GET /scheduler/status` endpoint
   - Shows next run times for all scheduled jobs
   - Displays last run results and status
   - Monitors both health checks and data refresh

4. **Force Re-download Flag** (`ingest/fetcher.py`)
   - Added `--force` flag to force re-download of all sources
   - Used by scheduler to bypass "already exists" checks
   - Ensures latest PDFs are always fetched
   - Usage: `python3 ingest/fetcher.py --force`

5. **Refresh Shell Script** (`refresh_data.sh`)
   - Convenience script for manual refreshes
   - Runs all 4 pipeline steps sequentially
   - Provides progress indicators
   - Usage: `./refresh_data.sh`

6. **Data Refresh Guide** (`docs/data-refresh-guide.md`)
   - Comprehensive documentation for data refresh
   - Automated and manual refresh procedures
   - Troubleshooting common issues
   - Best practices and performance notes

#### Updated Components

- **Scheduler Core** (`scheduler/core.py`)
  - Now registers two jobs: daily health check + monthly data refresh
  - Enhanced logging for both jobs
  - Configuration constants for cron schedules

- **README.md**
  - Added "Data Refresh & Currency" section
  - Documented new API endpoints
  - Marked "Auto-refresh data" as implemented (was "High priority")
  - Added reference to data refresh guide

#### API Changes

**New Endpoints:**
```
POST /scheduler/refresh-now
```

**Enhanced Endpoints:**
```
GET /scheduler/status  (now includes monthly_data_refresh job)
```

#### Configuration

**Scheduler Settings:**
- Daily health check: 10:00 AM IST (unchanged)
- Monthly data refresh: 1st of month, 02:00 AM IST (new)
- Timezone: Asia/Kolkata (IST)

**Performance:**
- Fetcher: ~15-30s
- Extractor: ~10-15s
- Chunker: ~2-5s
- Embedder: ~45-90s
- **Total: ~2-3 minutes**

#### Data Updates

**Refreshed on 2026-06-06:**
- Re-downloaded 27 sources (15 PDFs, 11 HTML pages, 1 custom facts)
- Extracted text from 22 documents
- Created 496 chunks (down from 500 — fewer duplicates)
- Rebuilt ChromaDB embeddings

#### Known Issues

- None at this time
- All tests passing
- No diagnostic errors

---

## [1.0.0] - 2026-06-05

### Initial Release

- RAG-based FAQ assistant for 5 HDFC Mutual Fund schemes
- Dual-layer answer system (structured + LLM)
- Safety guards (PII detection, advice blocking)
- ChromaDB vector store with 500 embedded chunks
- FastAPI backend with CORS support
- Single-page frontend (Tailwind CSS + vanilla JS)
- APScheduler with daily health checks
- Groq API integration (llama-3.3-70b-versatile)
- Recency-aware retrieval
- Test suite with 19 passing tests
- Docker deployment ready
- Comprehensive documentation

### Supported Schemes

1. HDFC Flexi Cap Fund
2. HDFC Mid Cap Fund
3. HDFC Small Cap Fund
4. HDFC Defence Fund
5. HDFC Silver ETF Fund of Fund

### Data Sources

- 15 PDFs (Fund Facts, KIMs, SIDs, FOF Book)
- 11 HTML pages (AMFI, SEBI, HDFC scheme pages)
- 1 custom facts file (canonical scheme data)

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backwards-compatible)
- **PATCH** version for backwards-compatible bug fixes

---

## Future Roadmap

### High Priority
- [ ] Multi-AMC support (SBI, ICICI Prudential, Axis, Mirae Asset)
- [ ] Fund comparison feature
- [ ] Citation URLs per answer (source document links)

### Medium Priority
- [ ] Docker deployment to Render/Fly.io
- [ ] Conversation memory (multi-turn context)
- [ ] Admin dashboard for monitoring
- [ ] Data freshness alerts

### Low Priority
- [ ] Portfolio analytics (CAS statement parsing)
- [ ] Voice interface (Web Speech API)
- [ ] Hindi language support
- [ ] Regular Plan data (in addition to Direct Plan)

---

## Contributors

- Built with Kiro AI Assistant
- Maintained by Rukhsar Khan

---

## License

MIT License — See LICENSE file for details
