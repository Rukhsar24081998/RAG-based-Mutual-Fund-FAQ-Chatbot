# HDFC Mutual Fund FAQ API - Hugging Face Space

This is the backend API for the HDFC Mutual Fund FAQ Assistant.

## Auto-Setup on Hugging Face

The Space will automatically:
1. Install dependencies from `requirements.txt`
2. Run the ingest pipeline to build ChromaDB
3. Start the FastAPI server

## Environment Variables

Set these in your Space Settings → Repository secrets:

```
GROQ_API_KEY=your_groq_api_key_here
```

## First-Time Setup

The Space will automatically run:
```bash
python3 ingest/fetcher.py
python3 ingest/extractor.py
python3 ingest/chunker.py
python3 ingest/embedder.py
```

This creates the ChromaDB vector store in the `data/` directory.

## API Endpoints

- `GET /health` - Health check
- `POST /ask` - Submit questions
- `GET /scheduler/status` - View scheduler status
- `POST /scheduler/refresh-now` - Trigger manual data refresh

## Version

2.0.1 - Production Ready ✅
