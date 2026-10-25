
from pathlib import Path
import re

import chromadb
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "novacart_policies"

model = SentenceTransformer(MODEL_NAME)
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


def load_and_chunk_documents(file_path):
    """Split a NovaCart Markdown policy into searchable sections."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")

    sections = re.split(r"(?=^###\s+)", text, flags=re.MULTILINE)
    chunks = []

    for index, section in enumerate(sections):
        section = section.strip()

        if not section:
            continue

        match = re.search(r"NC-AC-\d{3}", section)
        control_id = match.group(0) if match else ""

        chunks.append({
            "id": f"{path.stem}-{index}",
            "text": section,
            "source": path.name,
            "control_id": control_id
        })

    return chunks


def index_documents(file_path):
    """Generate embeddings and save document sections in ChromaDB."""
    chunks = load_and_chunk_documents(file_path)

    if not chunks:
        return 0

    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts).tolist()

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": chunk["source"],
                "control_id": chunk["control_id"]
            }
            for chunk in chunks
        ]
    )

    return len(chunks)


def search_knowledge_base(query, top_k=3):
    """Retrieve relevant policy sections using semantic similarity."""
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        matches.append({
            "text": document,
            "source": metadata["source"],
            "control_id": metadata["control_id"],
            "distance": distance
        })

    return matches
