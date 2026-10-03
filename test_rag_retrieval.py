import os

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "rag_data", "chroma")

COLLECTION_NAME = "agriculture_rag"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


print("=" * 60)
print("RAG RETRIEVAL EVALUATION")
print("=" * 60)

print("\nLoading embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL)
print("Embedding model loaded successfully.")

print("\nConnecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(name=COLLECTION_NAME)
print("\nSearching specifically for Tomato Powdery Mildew...")

results = collection.get(
    where_document={
        "$and": [
            {"$contains": "tomato"},
            {"$contains": "powdery mildew"}
        ]
    },
    limit=10
)

documents = results.get("documents", [])

print(f"Matching documents found: {len(documents)}")

for index, document in enumerate(documents, start=1):
    print(f"\n--- Match {index} ---")
    print(document)
    
print("ChromaDB connected successfully.")
print(f"Documents in collection: {collection.count()}")


TEST_QUERIES = [
    "Tomato powdery mildew: How do I control powdery mildew?",
    "Tomato early blight: What are the symptoms and management methods?",
    "Tomato bacterial leaf spot: How can I control it?",
    "Tomato fungal diseases: How can I control them?",
    "Tomato diseases: What are common diseases and how can they be managed?",
]


for query in TEST_QUERIES:

    print("\n" + "=" * 60)
    print(f"QUERY: {query}")
    print("=" * 60)

    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    documents = results.get("documents", [[]])[0]

    for index, document in enumerate(documents, start=1):

        print(f"\n--- Result {index} ---")
        print(document)


print("\n" + "=" * 60)
print("RETRIEVAL EVALUATION FINISHED")
print("=" * 60)