from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
APP_NAME = os.getenv("APP_NAME", "Garwo")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

SYSTEM_PROMPT = """Kamu adalah Garwo, AI personal assistant yang membantu pengguna dalam:
- Mencatat dan menganalisis pengeluaran harian
- Mendukung kesehatan mental dan menjadi teman curhat
- Mengelola agenda dan kegiatan harian
- Merencanakan kegiatan beberapa hari ke depan

Kepribadianmu: hangat, supportif, jujur, dan proaktif.

WAJIB: Selalu gunakan Bahasa Indonesia di SETIAP response tanpa terkecuali.
DILARANG: Menggunakan bahasa lain (Inggris, Mandarin, dll).
Jawab dengan ringkas tapi penuh empati.

Jika diberikan KONTEKS DOKUMEN, gunakan informasi tersebut untuk menjawab.
Jika konteks tidak relevan, jawab berdasarkan pengetahuanmu sendiri."""