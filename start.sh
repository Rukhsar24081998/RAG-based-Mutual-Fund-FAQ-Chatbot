#!/bin/bash
set -e

echo "========================================"
echo "  HDFC Mutual Fund FAQ Assistant"
echo "========================================"

# Run the ingest pipeline only if ChromaDB has not been built yet.
# On Railway with a persistent volume mounted at /app/data, this runs
# exactly once and is skipped on every subsequent deployment.
if [ ! -f "data/chroma/chroma.sqlite3" ]; then
    echo ""
    echo "[1/4] Downloading 21 official sources..."
    python ingest/fetcher.py

    echo ""
    echo "[2/4] Extracting text from PDFs and HTML..."
    python ingest/extractor.py

    echo ""
    echo "[3/4] Chunking into 500-word segments..."
    python ingest/chunker.py

    echo ""
    echo "[4/4] Embedding into ChromaDB (this takes 2-4 minutes)..."
    python ingest/embedder.py

    echo ""
    echo "Ingest pipeline complete. ChromaDB ready."
else
    echo "ChromaDB found — skipping ingest pipeline."
fi

echo ""
echo "Starting API server on 0.0.0.0:${PORT:-8000}..."
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
