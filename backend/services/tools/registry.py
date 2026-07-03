from services.tools.expense import save_expense, get_expenses, delete_expense
from services.tools.agenda import add_agenda, get_agenda, delete_agenda

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "save_expense",
            "description": "Catat pengeluaran uang baru. Gunakan saat user menyebut nominal uang yang dikeluarkan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Jumlah pengeluaran dalam rupiah"},
                    "category": {"type": "string", "description": "Kategori: food, transport, health, entertainment, shopping, other"},
                    "description": {"type": "string", "description": "Deskripsi singkat pengeluaran"}
                },
                "required": ["amount", "category", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expenses",
            "description": "Ambil data pengeluaran. Gunakan saat user bertanya tentang pengeluaran.",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "Periode: today, week, month, all"}
                },
                "required": ["period"]
            }
        }
    },
{
    "type": "function",
    "function": {
        "name": "add_agenda",
        "description": """Tambah agenda/jadwal dengan WAKTU atau TANGGAL SPESIFIK — kegiatan yang terikat jam/hari tertentu.
GUNAKAN untuk kalimat seperti: 'jadwalkan meeting jam 3 sore', 'besok ada acara ulang tahun', 'tanggal 5 ada dokter gigi'.
WAJIB gunakan tool ini jika user menyebut JAM, HARI, atau TANGGAL SPESIFIK terkait suatu kegiatan.""",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Nama kegiatan"},
                "date": {"type": "string", "description": "Tanggal format YYYY-MM-DD"},
                "time": {"type": "string", "description": "Waktu format HH:MM, opsional"},
                "notes": {"type": "string", "description": "Catatan tambahan, opsional"}
            },
            "required": ["title", "date"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_agenda",
        "description": """Ambil agenda/jadwal kegiatan.
GUNAKAN untuk kalimat seperti: 'apa agenda aku', 'jadwal hari ini apa', 'ada acara apa minggu ini'.""",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Tanggal spesifik format YYYY-MM-DD, kosongkan untuk semua agenda mendatang"}
            },
            "required": []
        }
    }
}
]

TOOLS_MAP = {
    "save_expense": save_expense,
    "get_expenses": get_expenses,
    "delete_expense": delete_expense,
    "add_agenda": add_agenda,
    "get_agenda": get_agenda,
    "delete_agenda": delete_agenda,
}

def execute_tool(tool_name: str, session_id: str, args: dict):
    """Eksekusi tool berdasarkan nama."""
    if tool_name not in TOOLS_MAP:
        return {"error": f"Tool '{tool_name}' tidak ditemukan"}
    
    func = TOOLS_MAP[tool_name]
    return func(session_id=session_id, **args)