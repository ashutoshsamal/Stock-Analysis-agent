from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma")
collection = client.get_or_create_collection(name="rag_docs")

# Example documents
docs = [
    "Python is a programming language.",
    "ChromaDB is a vector database for LLM RAG pipelines.",
    "The Eiffel Tower is in Paris.",
]

# Create embeddings
embeddings = embedding_model.encode(docs).tolist()

# Add to Chroma
collection.add(
    documents=docs,
    embeddings=embeddings,
    ids=[f"doc_{i}" for i in range(len(docs))]
)