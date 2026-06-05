import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "hdfc_mf_faq"

client = chromadb.PersistentClient(path=CHROMA_DIR)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=sentence_transformer_ef
)

# Get chunk with id 365
results = collection.get(ids=["365"])
print("Chunk 365:")
print(results)
