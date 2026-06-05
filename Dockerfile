FROM python:3.11-slim

# System build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create data directories
RUN mkdir -p data/raw data/extracted data/chunks data/chroma tmp

# Copy custom_facts.txt into data/raw so the fetcher skips the file:// URL
# (the file:// path in sources.csv points to a local Mac path that won't
#  exist on the build server — this ensures custom facts are always available)
RUN cp custom_facts.txt data/raw/custom_facts.txt

# Run the full ingest pipeline at BUILD TIME
# HF Spaces build servers have internet access + 16 GB RAM — no OOM risk.
# ChromaDB is baked into the image so startup is instant at runtime.
RUN python ingest/fetcher.py && \
    python ingest/extractor.py && \
    python ingest/chunker.py && \
    python ingest/embedder.py

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
