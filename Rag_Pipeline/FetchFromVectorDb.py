from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma")  # Same path!
collection = client.get_or_create_collection(name="rag_docs")

query = "What is ChromaDB?"

# Embed the query
query_embedding = embedding_model.encode([query]).tolist()

# Retrieve top 2 most relevant documents
results = collection.query(
    query_embeddings=query_embedding,
    n_results=1
)

relevant_docs = results["documents"][0]
print(relevant_docs)