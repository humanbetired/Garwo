import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

mcp = FastMCP("Garwo Web Search")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@mcp.tool()
async def search_web(query: str, max_results: int = 5) -> dict:
    """
    Cari informasi terbaru dari internet.
    Gunakan saat user bertanya tentang berita terkini, harga saham,
    cuaca, informasi yang mungkin berubah, atau hal yang butuh 
    data real-time dari internet.
    
    Args:
        query: Kata kunci atau pertanyaan yang ingin dicari
        max_results: Jumlah hasil maksimal (default 5)
    """
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY tidak ditemukan di .env"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": True
            }
        )
        data = response.json()
    
    results = []
    for r in data.get("results", []):
        results.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "snippet": r.get("content", "")[:300]
        })
    
    return {
        "answer": data.get("answer", ""),
        "results": results,
        "query": query
    }

@mcp.tool()
async def get_weather(city: str) -> dict:
    """
    Cari informasi cuaca untuk kota tertentu.
    
    Args:
        city: Nama kota yang ingin dicek cuacanya
    """
    return await search_web(f"cuaca hari ini di {city}", max_results=3)

if __name__ == "__main__":
    mcp.run(transport="stdio")