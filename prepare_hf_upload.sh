#!/bin/bash

# Prepare files for Hugging Face Space manual upload
# This creates a clean folder with only the files you need to upload

echo "🚀 Preparing files for Hugging Face upload..."

# Create upload directory on Desktop
UPLOAD_DIR="$HOME/Desktop/hf-upload-fixed"
rm -rf "$UPLOAD_DIR"
mkdir -p "$UPLOAD_DIR"

# Copy updated Python files (preserve directory structure)
echo "📦 Copying updated Python files..."

mkdir -p "$UPLOAD_DIR/rag"
cp rag/assembler.py "$UPLOAD_DIR/rag/"

mkdir -p "$UPLOAD_DIR/api"
cp api/main.py "$UPLOAD_DIR/api/"
cp api/__init__.py "$UPLOAD_DIR/api/"

mkdir -p "$UPLOAD_DIR/scheduler"
cp scheduler/core.py "$UPLOAD_DIR/scheduler/"
cp scheduler/jobs.py "$UPLOAD_DIR/scheduler/"
cp scheduler/__init__.py "$UPLOAD_DIR/scheduler/"

mkdir -p "$UPLOAD_DIR/ingest"
cp ingest/fetcher.py "$UPLOAD_DIR/ingest/"
cp ingest/extractor.py "$UPLOAD_DIR/ingest/"
cp ingest/chunker.py "$UPLOAD_DIR/ingest/"
cp ingest/embedder.py "$UPLOAD_DIR/ingest/"
cp ingest/__init__.py "$UPLOAD_DIR/ingest/"

# Copy entry point
cp app.py "$UPLOAD_DIR/"

# Copy updated custom facts
cp custom_facts.txt "$UPLOAD_DIR/"
mkdir -p "$UPLOAD_DIR/data/extracted"
cp data/extracted/custom_facts.txt "$UPLOAD_DIR/data/extracted/"

# Copy config files
cp requirements.txt "$UPLOAD_DIR/" 2>/dev/null || true
cp .env.example "$UPLOAD_DIR/" 2>/dev/null || true

echo ""
echo "✅ Files prepared in: $UPLOAD_DIR"
echo ""
echo "📋 Files to upload to Hugging Face:"
find "$UPLOAD_DIR" -type f | sort

echo ""
echo "🚨 IMPORTANT STEPS:"
echo "1. Go to: https://huggingface.co/spaces/Rukhsar24081998/hdfc-mf-faq-api"
echo "2. Click 'Files' tab"
echo "3. DELETE the 'data/chroma/' folder (contains old data)"
echo "4. Upload ALL files from: $UPLOAD_DIR"
echo "5. In Settings, click 'Factory reboot' OR edit app.py to trigger rebuild"
echo ""
echo "⏰ Wait ~5-10 minutes for rebuild to complete"
echo ""
