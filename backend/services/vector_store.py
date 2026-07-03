import chromadb
from chromadb.config import Settings
from config import CHROMA_DIR

client = chromadb.PersistentClient(
    path=CHROMA_DIR,
    settings=Settings(anonymized_telemetry=False)
)

def get_collection(session_id: str):
    """Ambil atau buat collection per user session."""
    collection_name = f"garwo_{session_id}"
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks(session_id: str, chunks: list[str], embeddings: list[list[float]], doc_name: str):
    """Simpan chunks + embeddings ke ChromaDB."""
    collection = get_collection(session_id)
    
    ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
    
    try:
        existing = collection.get(where={"doc_name": doc_name})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except:
        pass
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"doc_name": doc_name, "chunk_index": i} for i in range(len(chunks))]
    )
    return len(chunks)

def search_similar(session_id: str, query_embedding: list[float], n_results: int = 3) -> list[str]:
    """Cari chunks paling relevan dengan query."""
    collection = get_collection(session_id)
    
    count = collection.count()
    if count == 0:
        return []
    
    n_results = min(n_results, count)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    return results["documents"][0] if results["documents"] else []

def list_documents(session_id: str) -> list[str]:
    """List semua dokumen yang sudah diupload."""
    collection = get_collection(session_id)
    results = collection.get()
    
    if not results["metadatas"]:
        return []
    
    doc_names = list(set(m["doc_name"] for m in results["metadatas"]))
    return doc_names

def delete_document(session_id: str, doc_name: str):
    """Hapus dokumen dari vector store."""
    collection = get_collection(session_id)
    existing = collection.get(where={"doc_name": doc_name})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])