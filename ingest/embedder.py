import os
import tempfile

# Set up temporary directory first
os.environ["TMPDIR"] = "/tmp"
tempfile.tempdir = "/tmp"

import json
import chromadb
from chromadb.utils import embedding_functions

CHUNKS_PATH = "data/chunks/chunks.jsonl"
CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "hdfc_mf_faq"

def main():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef,
        metadata={"description": "HDFC Mutual Fund FAQ corpus"}
    )
    
    chunks = []
    with open(CHUNKS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))
    
    ids = [c['id'] for c in chunks]
    texts = [c['text'] for c in chunks]
    metadatas = [{
        'url': c['url'],
        'scheme': c['scheme'],
        'type': c['type'],
        'doc_date': c.get('doc_date', '')
    } for c in chunks]
    
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    
    print(f"Done! Added {len(chunks)} chunks to ChromaDB")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Data directory: {os.path.abspath(CHROMA_DIR)}")

if __name__ == "__main__":
    main()
