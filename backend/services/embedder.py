import httpx
from config import OLLAMA_BASE_URL, EMBEDDING_MODEL

async def get_embedding(text: str) -> list[float]:
    """Ubah teks jadi vektor embedding via Ollama."""
    async with httpx.AsyncClient(
        timeout=120.0,
        headers={"ngrok-skip-browser-warning": "true", "User-Agent": "python-httpx"}
    ) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": EMBEDDING_MODEL, "input": text}
        )
        data = response.json()
        return data["embeddings"][0]

async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Embed banyak teks sekaligus."""
    async with httpx.AsyncClient(
        timeout=120.0,
        headers={"ngrok-skip-browser-warning": "true", "User-Agent": "python-httpx"}
    ) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": EMBEDDING_MODEL, "input": texts}
        )
        data = response.json()
        return data["embeddings"]