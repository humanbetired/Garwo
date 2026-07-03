import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Garwo Agenda Manager")

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../backend/data")
os.makedirs(DATA_DIR, exist_ok=True)

def _get_file(session_id: str) -> str:
    return os.path.join(DATA_DIR, f"{session_id}_agenda.json")

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
def add_agenda(session_id: str, title: str, date: str, time: str = None, notes: str = None) -> dict:
    """
    Tambah agenda atau jadwal dengan WAKTU atau TANGGAL SPESIFIK.
    Gunakan saat user menyebut kegiatan di tanggal atau jam tertentu.
    WAJIB gunakan tool ini jika user menyebut jam, hari, atau tanggal spesifik.
    
    Args:
        session_id: ID sesi user
        title: Nama kegiatan
        date: Tanggal format YYYY-MM-DD
        time: Waktu format HH:MM (opsional)
        notes: Catatan tambahan (opsional)
    """
    agendas = _load(session_id)
    agenda = {
        "id": len(agendas) + 1,
        "title": title,
        "date": date,
        "time": time,
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    agendas.append(agenda)
    _save(session_id, agendas)
    return agenda

@mcp.tool()
def get_agenda(session_id: str, date: str = None) -> list:
    """
    Ambil agenda atau jadwal kegiatan.
    Gunakan saat user bertanya tentang jadwal, agenda, atau kegiatan mendatang.
    
    Args:
        session_id: ID sesi user
        date: Tanggal spesifik format YYYY-MM-DD, kosongkan untuk semua agenda mendatang
    """
    agendas = _load(session_id)
    if date:
        return [a for a in agendas if a["date"] == date]
    today = datetime.now().strftime("%Y-%m-%d")
    return [a for a in agendas if a["date"] >= today]

@mcp.tool()
def delete_agenda(session_id: str, agenda_id: int) -> dict:
    """
    Hapus agenda berdasarkan ID.
    
    Args:
        session_id: ID sesi user
        agenda_id: ID agenda yang ingin dihapus
    """
    agendas = _load(session_id)
    new_agendas = [a for a in agendas if a["id"] != agenda_id]
    if len(new_agendas) == len(agendas):
        return {"success": False, "message": f"Agenda ID {agenda_id} tidak ditemukan"}
    _save(session_id, new_agendas)
    return {"success": True, "message": f"Agenda ID {agenda_id} berhasil dihapus"}

if __name__ == "__main__":
    mcp.run(transport="stdio")