from rag.retriever import retrieve

query = "What is the expense ratio of HDFC Mid Cap Fund?"
chunks = retrieve(query)
print(f"Retrieved {len(chunks)} chunks:")
for i, chunk in enumerate(chunks):
    print(f"\n--- CHUNK {i+1} ---")
    print(f"URL: {chunk['metadata']['url']}")
    print(f"Text:\n{chunk['text']}")
