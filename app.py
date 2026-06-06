"""
Hugging Face Space entry point for HDFC Mutual Fund FAQ API

This file runs the ingest pipeline and starts the FastAPI server.
"""

import os
import subprocess
import sys

def run_ingest_pipeline():
    """Run the complete data ingestion pipeline"""
    print("=" * 80)
    print("HDFC Mutual Fund FAQ API - First-time setup")
    print("=" * 80)
    
    # Check if data already exists
    if os.path.exists("data/chroma/chroma.sqlite3"):
        print("✓ ChromaDB already exists, skipping ingest pipeline")
        return
    
    print("\n📥 Running data ingest pipeline...")
    
    steps = [
        ("Fetching sources", ["python3", "ingest/fetcher.py"]),
        ("Extracting text", ["python3", "ingest/extractor.py"]),
        ("Chunking documents", ["python3", "ingest/chunker.py"]),
        ("Building embeddings", ["python3", "ingest/embedder.py"]),
    ]
    
    for step_name, cmd in steps:
        print(f"\n▶ {step_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ {step_name} failed:")
            print(result.stderr)
            sys.exit(1)
        else:
            print(f"✓ {step_name} complete")
            if result.stdout:
                print(result.stdout)
    
    print("\n" + "=" * 80)
    print("✅ Data pipeline complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    # Run ingest pipeline
    run_ingest_pipeline()
    
    # Start FastAPI server
    print("🚀 Starting FastAPI server...\n")
    subprocess.run(["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"])
