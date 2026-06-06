#!/bin/bash
#
# Manual Data Refresh Script
# 
# This script manually refreshes all mutual fund data by:
# 1. Re-downloading PDFs from HDFC website
# 2. Re-extracting text content
# 3. Re-chunking documents
# 4. Rebuilding ChromaDB embeddings
#
# Usage: ./refresh_data.sh
#
# Note: The scheduler automatically runs this on the 1st of every month at 02:00 AM IST
#       This script is for manual/emergency refreshes only.

set -e  # Exit on any error

echo "=========================================="
echo "HDFC Mutual Fund Data Refresh"
echo "Started: $(date)"
echo "=========================================="
echo ""

echo "Step 1/4: Fetching latest PDFs and sources..."
python3 ingest/fetcher.py --force
echo "✓ Fetch complete"
echo ""

echo "Step 2/4: Extracting text from documents..."
python3 ingest/extractor.py
echo "✓ Extraction complete"
echo ""

echo "Step 3/4: Chunking documents..."
python3 ingest/chunker.py
echo "✓ Chunking complete"
echo ""

echo "Step 4/4: Rebuilding vector embeddings..."
python3 ingest/embedder.py
echo "✓ Embeddings complete"
echo ""

echo "=========================================="
echo "Data refresh completed successfully!"
echo "Finished: $(date)"
echo "=========================================="
echo ""
echo "You can now restart the API server to use the updated data."
echo "The ChromaDB will automatically load the new embeddings."
