import os
import tempfile

# Set up temporary directory first
os.environ["TMPDIR"] = "/tmp"
tempfile.tempdir = "/tmp"

from datetime import datetime, date

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "hdfc_mf_faq"

# Recency scoring constants
RECENCY_MAX_BOOST = 0.5  # Maximum boost for brand-new documents
RECENCY_DECAY_DAYS = 365  # Boost decays to 0 over this many days


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )


def _parse_doc_date(date_str: str):
    """Parse a YYYY-MM-DD date string. Returns None if invalid."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _recency_boost(doc_date_str: str) -> float:
    """Calculate recency boost for a document date.
    
    Returns a value between 0.0 and RECENCY_MAX_BOOST.
    - Brand new document (today): RECENCY_MAX_BOOST
    - Document older than RECENCY_DECAY_DAYS: 0.0
    - Linear decay in between.
    """
    doc_date = _parse_doc_date(doc_date_str)
    if doc_date is None:
        return 0.0  # No date = no boost
    
    days_old = (date.today() - doc_date).days
    if days_old < 0:
        days_old = 0
    
    boost = RECENCY_MAX_BOOST * max(0.0, 1.0 - (days_old / RECENCY_DECAY_DAYS))
    return boost


def retrieve(query, top_k=5, use_recency=True):
    """Retrieve relevant chunks with optional recency-aware re-ranking.
    
    Args:
        query: The user's question.
        top_k: Number of chunks to return.
        use_recency: If True, re-rank by combining semantic similarity with
                     document recency. Newer documents are preferred.
    
    Returns:
        List of dicts with keys: id, text, metadata, source_documents.
    """
    collection = get_collection()
    
    # Over-retrieve to allow re-ranking
    fetch_k = top_k * 3 if use_recency else top_k
    
    results = collection.query(
        query_texts=[query],
        n_results=fetch_k
    )
    
    chunks = []
    for i in range(len(results['ids'][0])):
        chunk_id = results['ids'][0][i]
        meta = results['metadatas'][0][i]
        text = results['documents'][0][i]
        distance = results['distances'][0][i] if 'distances' in results else 1.0
        
        chunks.append({
            'id': chunk_id,
            'text': text,
            'metadata': meta,
            '_distance': distance,
        })
    
    if use_recency and chunks:
        # Re-rank: convert distance to similarity, add recency boost
        # ChromaDB L2 distance: lower = more similar
        # Convert to a pseudo-similarity score: 1 / (1 + distance)
        for chunk in chunks:
            semantic_score = 1.0 / (1.0 + chunk['_distance'])
            recency = _recency_boost(chunk['metadata'].get('doc_date', ''))
            chunk['_final_score'] = semantic_score + recency
        
        # Sort by final_score descending (highest = most relevant + recent)
        chunks.sort(key=lambda c: c['_final_score'], reverse=True)
        chunks = chunks[:top_k]
    else:
        # Original behavior: prioritize custom facts
        custom_chunks = [c for c in chunks if c['metadata'].get('type') == 'Custom Facts']
        other_chunks = [c for c in chunks if c['metadata'].get('type') != 'Custom Facts']
        chunks = (custom_chunks + other_chunks)[:top_k]
    
    # Clean up internal scoring fields before returning
    for chunk in chunks:
        chunk.pop('_distance', None)
        chunk.pop('_final_score', None)
    
    return chunks


def get_source_documents(chunks):
    """Extract unique source document info from retrieved chunks.
    
    Returns a list of dicts with: url, type, scheme, doc_date.
    Useful for showing the user exactly which sources produced the answer.
    """
    seen_urls = set()
    sources = []
    
    for chunk in chunks:
        meta = chunk.get('metadata', {})
        url = meta.get('url', '')
        if not url or url in seen_urls:
            continue
        
        seen_urls.add(url)
        sources.append({
            'url': url,
            'type': meta.get('type', ''),
            'scheme': meta.get('scheme', ''),
            'doc_date': meta.get('doc_date', ''),
        })
    
    return sources
