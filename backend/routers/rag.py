from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import fitz  
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.embedder import get_embeddings_batch
from services.vector_store import add_chunks, list_documents, delete_document
from config import UPLOAD_DIR

router = APIRouter()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " "]
)

def extract_text_from_pdf(file_path: str) -> str:
    """Ekstrak teks dari PDF menggunakan PyMuPDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

@router.post("/rag/upload/{session_id}")
async def upload_document(session_id: str, file: UploadFile = File(...)):
    """Upload PDF dan index ke vector store."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang didukung")
    
    # Simpan file
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Ekstrak teks
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="PDF tidak bisa dibaca atau kosong")
    
    # Chunking
    chunks = text_splitter.split_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Gagal memproses dokumen")
    
    # Embedding batch
    embeddings = await get_embeddings_batch(chunks)
    
    # Simpan ke ChromaDB
    doc_name = file.filename
    total = add_chunks(session_id, chunks, embeddings, doc_name)
    
    return {
        "message": f"Dokumen '{doc_name}' berhasil diindex",
        "chunks": total,
        "doc_name": doc_name
    }

@router.get("/rag/documents/{session_id}")
async def get_documents(session_id: str):
    """List semua dokumen yang sudah diupload."""
    docs = list_documents(session_id)
    return {"documents": docs}

@router.delete("/rag/documents/{session_id}/{doc_name}")
async def remove_document(session_id: str, doc_name: str):
    """Hapus dokumen dari vector store."""
    delete_document(session_id, doc_name)
    return {"message": f"Dokumen '{doc_name}' berhasil dihapus"}