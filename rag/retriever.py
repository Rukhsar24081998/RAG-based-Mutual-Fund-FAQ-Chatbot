import os
import tempfile

# Set up temporary directory first
os.environ["TMPDIR"] = "/tmp"
tempfile.tempdir = "/tmp"

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "hdfc_mf_faq"

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )

def retrieve(query, top_k=5):
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    chunks = []
    for i in range(len(results['ids'][0])):
        chunks.append({
            'id': results['ids'][0][i],
            'text': results['documents'][0][i],
            'metadata': results['metadatas'][0][i]
        })
    
    # Prioritize custom facts chunks
    custom_chunks = [c for c in chunks if c['metadata'].get('type') == 'Custom Facts']
    other_chunks = [c for c in chunks if c['metadata'].get('type') != 'Custom Facts']
    return custom_chunks + other_chunks
