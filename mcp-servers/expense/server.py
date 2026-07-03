import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Inisialisasi MCP Server
mcp = FastMCP("Garwo Expense Tracker")

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../backend/data")
os.makedirs(DATA_DIR, exist_ok=True)

def _get_file(session_id: str) -> str:
    return os.path.join(DATA_DIR, f"{session_id}_expenses.json")

def _load(session_id: str) -> list:
    f = _get_file(session_id)
    if not os.path.exists(f):
        return []
    with open(f) as file:
        return json.load(file)

def _save(session_id: str, data: list):
    with open(_get_file(session_id), "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@mcp.tool()
def save_expense(session_id: str, amount: float, category: str, description: str) -> dict:
    """
    Catat pengeluaran uang baru.
    Gunakan saat user menyebut nominal uang yang dikeluarkan.
    
    Args:
        session_id: ID sesi user
        amount: Jumlah pengeluaran dalam rupiah
        category: Kategori pengeluaran (food, transport, health, entertainment, shopping, other)
        description: Deskripsi singkat pengeluaran
    """
    expenses = _load(session_id)
    entry = {
        "id": len(expenses) + 1,
        "amount": amount,
        "category": category,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M")
    }
    expenses.append(entry)
    _save(session_id, expenses)
    return entry

@mcp.tool()
def get_expenses(session_id: str, period: str = "today") -> dict:
    """
    Ambil data pengeluaran berdasarkan periode.
    Gunakan saat user bertanya tentang total atau rincian pengeluaran.
    
    Args:
        session_id: ID sesi user
        period: Periode waktu - today, week, month, atau all
    """
    expenses = _load(session_id)
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now()

    if period == "today":
        filtered = [e for e in expenses if e["date"] == today]
    elif period == "week":
        filtered = [e for e in expenses if (now - datetime.strptime(e["date"], "%Y-%m-%d")).days <= 7]
    elif period == "month":
        filtered = [e for e in expenses if e["date"].startswith(now.strftime("%Y-%m"))]
    else:
        filtered = expenses

    total = sum(e["amount"] for e in filtered)
    by_category = {}
    for e in filtered:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + e["amount"]

    return {
        "period": period,
        "total": total,
        "count": len(filtered),
        "by_category": by_category,
        "entries": filtered
    }

@mcp.tool()
def delete_expense(session_id: str, expense_id: int) -> dict:
    """
    Hapus pengeluaran berdasarkan ID.
    
    Args:
        session_id: ID sesi user
        expense_id: ID pengeluaran yang ingin dihapus
    """
    expenses = _load(session_id)
    new_expenses = [e for e in expenses if e["id"] != expense_id]
    if len(new_expenses) == len(expenses):
        return {"success": False, "message": f"Expense ID {expense_id} tidak ditemukan"}
    _save(session_id, new_expenses)
    return {"success": True, "message": f"Expense ID {expense_id} berhasil dihapus"}

if __name__ == "__main__":
    mcp.run(transport="stdio")