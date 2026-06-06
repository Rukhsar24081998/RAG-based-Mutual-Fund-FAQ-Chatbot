# Data Refresh Guide

## Overview

The HDFC Mutual Fund FAQ Assistant uses data from official sources (PDFs, scheme pages) that can become outdated. This guide explains how the automated refresh system works and how to manually trigger updates when needed.

---

## Automated Refresh (Production)

### Monthly Scheduled Refresh

The system automatically refreshes data **on the 1st of every month at 02:00 AM IST** via APScheduler.

**What happens during automated refresh:**
1. Downloads latest Fund Facts PDFs from HDFC (May update monthly)
2. Re-extracts text content from all sources
3. Re-chunks documents into 500-word segments
4. Rebuilds ChromaDB vector embeddings (496+ chunks)
5. Updates the retrieval index with fresh data

**Monitoring:**
- Check scheduler status: `GET /scheduler/status`
- View last run results in API logs
- Health checks run daily at 10:00 AM IST

### Scheduler Configuration

Located in `scheduler/core.py`:
```python
MONTHLY_CRON_DAY = 1        # 1st of month
MONTHLY_CRON_HOUR = 2       # 02:00 AM
MONTHLY_CRON_MINUTE = 0
IST = pytz.timezone("Asia/Kolkata")
```

To change the schedule, modify these constants and restart the API.

---

## Manual Refresh

### Option 1: API Endpoint (Recommended)

Trigger an immediate refresh via REST API:

```bash
curl -X POST http://localhost:8000/scheduler/refresh-now
```

**Response:**
```json
{
  "status": "completed",
  "message": "Data refresh completed successfully",
  "details": {
    "job": "monthly_data_refresh",
    "status": "PASS",
    "results": {
      "fetcher": "OK (completed in 12.3s)",
      "extractor": "OK (completed in 8.5s)",
      "chunker": "OK (completed in 2.1s)",
      "embedder": "OK (completed in 45.7s)"
    },
    "duration_ms": 68600,
    "executed_at": "2026-06-06T10:30:00Z"
  }
}
```

**Notes:**
- Takes 5-10 minutes to complete
- API remains available during refresh
- Errors are logged to console
- Use for emergency updates when data is stale

### Option 2: Shell Script

Run the refresh script directly:

```bash
./refresh_data.sh
```

This executes the full pipeline:
1. `ingest/fetcher.py --force` → Re-downloads all sources
2. `ingest/extractor.py` → Re-extracts text
3. `ingest/chunker.py` → Re-chunks documents
4. `ingest/embedder.py` → Rebuilds ChromaDB

### Option 3: Manual Pipeline (Development)

Run each step individually for debugging:

```bash
# Step 1: Force re-download (--force skips "already exists" check)
python3 ingest/fetcher.py --force

# Step 2: Extract text from PDFs/HTML
python3 ingest/extractor.py

# Step 3: Chunk into 500-word segments
python3 ingest/chunker.py

# Step 4: Embed into ChromaDB
python3 ingest/embedder.py
```

---

## Data Sources

### Primary Sources (Updated Monthly)

| Source Type | Update Frequency | Example |
|------------|------------------|---------|
| **Fund Facts PDFs** | Monthly (1st week) | `Fund_Facts_-_HDFC_Flexi_Cap_Fund_May_26.pdf` |
| **FOF Book** | Monthly | `The_FOF_Book_-_May_2026_2.pdf` |
| **Scheme Pages** | Real-time (HTML) | `https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct` |

### Secondary Sources (Updated Annually)

| Source Type | Update Frequency | Example |
|------------|------------------|---------|
| **KIM (Key Information Memorandum)** | Annually | `KIM_-_HDFC_Flexi_Cap_Fund_dated_November_21,_2025_1.pdf` |
| **SID (Scheme Information Document)** | Annually | `SID_-_HDFC_Flexi_Cap_Fund_dated_November_21,_2025_0.pdf` |

### Static Sources

- **AMFI Education**: `https://www.amfiindia.com/investor/knowledge-center-info`
- **SEBI Portal**: `https://investor.sebi.gov.in/`
- **Custom Facts**: `custom_facts.txt` (manually maintained)

All sources are defined in `sources.csv`.

---

## Updating Custom Facts

The `custom_facts.txt` file contains **canonical scheme data** that overrides PDF sources for critical fields like:
- Expense ratio (Direct Plan)
- Minimum SIP amount
- Exit load rules
- Riskometer classification
- Fund manager names
- AUM (Assets Under Management)

### When to Update

Update `custom_facts.txt` when:
1. HDFC announces fund manager changes
2. Expense ratios are revised
3. AUM data is published (end of each month)
4. Exit load rules change
5. Any hardcoded fact becomes outdated

### Update Process

1. Edit `custom_facts.txt` with new data
2. Update the corresponding `doc_date` in `sources.csv` (last line)
3. Run the data refresh pipeline:
   ```bash
   ./refresh_data.sh
   ```

**Example:**
```txt
HDFC Flexi Cap Fund:
- Expense Ratio (Direct Plan): 0.68%  ← UPDATE THIS
- Minimum SIP Amount: ₹100
- Fund Manager: Amit Ganatra (since February 01, 2026)  ← OR THIS
- AUM: ₹1,01,821.82 crore (as on 31/05/2026)  ← OR THIS
```

---

## Troubleshooting

### Issue: "Data still outdated after refresh"

**Cause:** `SCHEME_DATA` dictionary in `rag/assembler.py` has hardcoded values that override `custom_facts.txt`.

**Solution:** 
1. Update `custom_facts.txt` first
2. Update the `SCHEME_DATA` dictionary in `rag/assembler.py` to match
3. Restart the API server

Example:
```python
SCHEME_DATA = {
    "HDFC Flexi Cap Fund": {
        "expense_ratio": "0.68%",  # ← Update this
        "aum": "1,00,479.23",       # ← And this
        # ...
    }
}
```

### Issue: "Scheduler job failed"

**Check logs:**
```bash
# View API logs
tail -f /var/log/hdfc-mf-api.log

# Or if running in foreground
python3 -m uvicorn api.main:app --reload
```

**Common causes:**
- Network timeout downloading PDFs
- Disk space full (embeddings are ~500MB)
- HDFC changed PDF URLs
- Missing dependencies

**Fix:**
1. Check `sources.csv` URLs are still valid
2. Run pipeline manually to see detailed errors
3. Check disk space: `df -h`

### Issue: "ChromaDB collection not found"

**Cause:** Embeddings were deleted or corrupted.

**Solution:**
```bash
# Rebuild from scratch
rm -rf data/chroma/
python3 ingest/embedder.py
```

### Issue: "Fetcher skipping files"

**Cause:** Files already exist, and `--force` flag was not used.

**Solution:**
```bash
# Delete old files first
rm -rf data/raw/*.pdf data/raw/*.html

# Or use --force flag
python3 ingest/fetcher.py --force
```

---

## Data Freshness Indicators

### In API Responses

Every answer includes:
```json
{
  "answer": "The expense ratio of HDFC Flexi Cap Fund is 0.68%",
  "last_updated": "June 2026",  ← User-facing timestamp
  "source_documents": [
    {
      "url": "https://files.hdfcfund.com/...",
      "type": "Fund Facts",
      "scheme": "HDFC Flexi Cap Fund",
      "doc_date": "2026-05-01"  ← Source document date
    }
  ]
}
```

### Recency-Aware Retrieval

The retriever automatically boosts newer documents in search results:
- Documents from the last 30 days: **+50% relevance boost**
- Linear decay over 365 days
- Combines semantic similarity + recency score

Configured in `rag/retriever.py`:
```python
RECENCY_MAX_BOOST = 0.5      # 50% boost for new docs
RECENCY_DECAY_DAYS = 365     # Boost decays to 0 over 1 year
```

---

## Best Practices

1. **Run refresh after official HDFC updates**  
   HDFC typically publishes Fund Facts PDFs in the first week of each month.

2. **Verify data after refresh**  
   Test a few queries to confirm updated data is being returned:
   ```bash
   curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the AUM of HDFC Flexi Cap Fund?"}'
   ```

3. **Monitor scheduler logs**  
   Set up log monitoring to catch failed scheduled refreshes.

4. **Keep sources.csv updated**  
   If HDFC changes PDF URLs, update `sources.csv` immediately.

5. **Test before production deploy**  
   Always test the refresh pipeline in staging before production.

---

## Performance Notes

| Step | Duration | Disk Usage |
|------|----------|-----------|
| Fetcher | ~15-30s | +50MB (PDFs) |
| Extractor | ~10-15s | +5MB (text) |
| Chunker | ~2-5s | +2MB (JSONL) |
| Embedder | ~45-90s | +500MB (ChromaDB) |
| **Total** | **~2-3 minutes** | **~560MB** |

**Network usage:** ~30-50MB download per refresh (re-downloading PDFs)

---

## Future Enhancements

- [ ] Web scraper to detect when HDFC publishes new Fund Facts
- [ ] Automatic email alerts when scheduled refresh fails
- [ ] Differential updates (only refresh changed documents)
- [ ] Data versioning (rollback to previous month's data)
- [ ] Admin dashboard to view refresh history
- [ ] Real-time AUM scraping from HDFC API (if available)

---

## Related Documentation

- [Problem Statement](Problemstatement.md) — Original requirements
- [Architecture](phase-wise-architecture.md) — Technical design
- [Deployment Plan](deployment-plan.md) — Production setup
- [README](../README.md) — Getting started guide
