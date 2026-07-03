import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")

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

def add_agenda(session_id: str, title: str, date: str, time: str = None, notes: str = None) -> dict:
    """Tambah agenda/event."""
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

def get_agenda(session_id: str, date: str = None) -> list:
    """Ambil agenda berdasarkan tanggal."""
    agendas = _load(session_id)
    if date:
        return [a for a in agendas if a["date"] == date]
    
    # Default: tampilkan agenda hari ini dan ke depan
    today = datetime.now().strftime("%Y-%m-%d")
    return [a for a in agendas if a["date"] >= today]

def delete_agenda(session_id: str, agenda_id: int) -> bool:
    """Hapus agenda."""
    agendas = _load(session_id)
    new_agendas = [a for a in agendas if a["id"] != agenda_id]
    if len(new_agendas) == len(agendas):
        return False
    _save(session_id, new_agendas)
    return True