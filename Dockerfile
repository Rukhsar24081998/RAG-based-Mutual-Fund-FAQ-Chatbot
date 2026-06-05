FROM python:3.11-slim

# System build dependencies (gcc required for some Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first — cached layer, only re-runs if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application source files
COPY . .

# Create data directories — populated at first boot by start.sh ingest pipeline
RUN mkdir -p data/raw data/extracted data/chunks data/chroma tmp

# Make startup script executable
RUN chmod +x start.sh

# Railway sets $PORT automatically; default to 8000 for local Docker runs
EXPOSE 8000

CMD ["./start.sh"]
