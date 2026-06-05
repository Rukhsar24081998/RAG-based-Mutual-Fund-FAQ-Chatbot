import csv
import json
import os
import uuid

EXTRACTED_DIR = "data/extracted"
CHUNKS_DIR = "data/chunks"
SOURCES_CSV = "sources.csv"

CHUNK_SIZE = 500
OVERLAP = 50

def parse_metadata_from_file(text):
    metadata = {}
    lines = text.split("="*80)[0]
    for line in lines.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    return metadata

def get_url_from_metadata(metadata):
    return metadata.get('URL', '')

def get_scheme_from_metadata(metadata):
    return metadata.get('SCHEME', '')

def get_type_from_metadata(metadata):
    return metadata.get('TYPE', '')

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(' '.join(chunk_words))
        i += chunk_size - overlap
    return chunks

def main():
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    
    all_chunks = []
    chunk_id = 1
    
    for filename in os.listdir(EXTRACTED_DIR):
        if not filename.endswith('.txt'):
            continue
        
        file_path = os.path.join(EXTRACTED_DIR, filename)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        metadata = parse_metadata_from_file(text)
        content = text.split("="*80)[-1].strip()
        
        chunks = chunk_text(content)
        
        url = get_url_from_metadata(metadata)
        scheme = get_scheme_from_metadata(metadata)
        doc_type = get_type_from_metadata(metadata)
        
        for chunk in chunks:
            if not chunk.strip():
                continue
            
            all_chunks.append({
                'id': str(chunk_id),
                'text': chunk,
                'url': url,
                'scheme': scheme,
                'type': doc_type
            })
            chunk_id += 1
    
    output_path = os.path.join(CHUNKS_DIR, 'chunks.jsonl')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
    
    print(f"Done! Created {len(all_chunks)} chunks in {output_path}")

if __name__ == "__main__":
    main()
