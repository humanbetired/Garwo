from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import json
import re
from datetime import datetime
from config import OLLAMA_BASE_URL, MODEL_NAME, SYSTEM_PROMPT
from services.session import get_history, add_message
from services.embedder import get_embedding
from services.vector_store import search_similar
from services.mcp_client import get_all_tools, execute_mcp_tool

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    context_used: bool = False
    tools_used: list = []

MAX_HISTORY_MESSAGES = 6

TOOL_REINFORCEMENT = """[INSTRUKSI SISTEM — PENTING]
Kamu memiliki akses ke tools berikut: save_expense, get_expenses, delete_expense,
add_agenda, get_agenda, delete_agenda, search_web, get_weather.

ATURAN WAJIB:
- Jika user menyebut NOMINAL UANG yang dikeluarkan → WAJIB panggil save_expense
- Jika user bertanya TOTAL/JUMLAH pengeluaran → WAJIB panggil get_expenses
- Jika user ingin MENGHAPUS pengeluaran → WAJIB panggil delete_expense
- Jika user menyebut KEGIATAN dengan JAM/TANGGAL spesifik → WAJIB panggil add_agenda
- Jika user bertanya JADWAL/AGENDA → WAJIB panggil get_agenda
- Jika user ingin MENGHAPUS agenda → WAJIB panggil delete_agenda
- Jika user bertanya INFO TERKINI, BERITA, HARGA, atau hal yang butuh internet → WAJIB panggil search_web
- Jika user bertanya CUACA → WAJIB panggil get_weather
- JANGAN PERNAH mengatakan sudah melakukan aksi tanpa benar-benar memanggil tool
- SELALU panggil tool via mekanisme tool_calls resmi
- Jika user menambah agenda DAN ingin sync ke Google Calendar → panggil add_agenda LALU sync_agenda_to_calendar
- Jika user ingin lihat jadwal dari Google Calendar → WAJIB panggil get_calendar_events
- Jika user ingin KIRIM PESAN ke Telegram → WAJIB panggil send_telegram_message
- Jika user ingin BACA PESAN Telegram → WAJIB panggil get_telegram_messages
- Jika user ingin LAPORAN PENGELUARAN via Telegram → WAJIB panggil send_expense_report_to_telegram
- Jika user ingin REMINDER AGENDA via Telegram → WAJIB panggil send_agenda_reminder_to_telegram"""


TELEGRAM_KEYWORDS = ["telegram", "kirim pesan", "notifikasi", "reminder", "laporan ke", "beritahu aku"]

# tambahkan keyword baru
SEARCH_KEYWORDS = ["cari", "search", "browsing", "berita", "terbaru", "harga", "info", "informasi", "berapa harga", "apa itu", "siapa", "kapan"]
WEATHER_KEYWORDS = ["cuaca", "suhu", "hujan", "panas", "mendung", "prakiraan"]

HALLUCINATION_RETRY_PROMPT = """[PERINGATAN KERAS]
Kamu BARU SAJA mengklaim sudah melakukan aksi (mencatat/menambahkan/menghapus) TANPA 
benar-benar memanggil tool. Ini SALAH dan TIDAK BOLEH terjadi.

Sekarang, untuk pesan user terakhir, kamu WAJIB memanggil tool yang sesuai.
JANGAN menjawab dengan teks biasa. PANGGIL TOOL SEKARANG melalui mekanisme tool_calls."""

HALLUCINATION_KEYWORDS = [
    "sudah dicatat", "telah dicatat", "berhasil dicatat",
    "sudah ditambahkan", "telah ditambahkan", "berhasil ditambahkan",
    "sudah disimpan", "telah disimpan",
    "sudah saya catat", "sudah saya tambahkan",
    "kami catat", "telah kami catat", "sudah kami catat",
    "telah dihapus", "sudah dihapus", "berhasil dihapus",
    "telah diselesaikan", "sudah diselesaikan", "berhasil diselesaikan",
    "telah ditandai", "sudah ditandai"
]

READ_EXPENSE_KEYWORDS = ["pengeluaran", "habis berapa", "spend", "uang keluar", "budget"]
WRITE_EXPENSE_KEYWORDS = ["catat", "habis", "beli", "bayar", "keluar uang"]
READ_AGENDA_KEYWORDS = ["agenda", "jadwal", "kegiatan", "acara", "ada apa aja"]
WRITE_AGENDA_KEYWORDS = ["jadwalkan", "tambah agenda", "tambahkan agenda", "ada meeting", "ada acara", "jam ", "tanggal "]
DELETE_KEYWORDS = ["hapus", "batalkan", "buang", "cancel", "remove"]
COMPLETE_KEYWORDS = ["selesai", "sudah dikerjakan", "centang", "tandai selesai"]

def is_hallucinated_claim(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in HALLUCINATION_KEYWORDS)

def detect_required_tool_choice(message: str) -> str:
    text = message.lower()
    all_keywords = (
        READ_EXPENSE_KEYWORDS + READ_AGENDA_KEYWORDS +
        WRITE_EXPENSE_KEYWORDS + WRITE_AGENDA_KEYWORDS +
        DELETE_KEYWORDS + SEARCH_KEYWORDS + WEATHER_KEYWORDS + TELEGRAM_KEYWORDS + COMPLETE_KEYWORDS
    )
    if any(keyword in text for keyword in all_keywords):
        return "required"
    return "auto"

def try_parse_malformed_tool_call(content: str):
    """Coba parse tool call yang 'bocor' jadi text biasa alih-alih field tool_calls resmi."""
    if not content or '"name"' not in content or '"arguments"' not in content:
        return None
    try:
        match = re.search(r'\{[^{}]*"name"\s*:\s*"(\w+)"[^{}]*"arguments"\s*:\s*(\{[^{}]*\})[^{}]*\}', content)
        if match:
            tool_name = match.group(1)
            args_str = match.group(2)
            args = json.loads(args_str)
            return {"name": tool_name, "arguments": args}
    except Exception as e:
        print(f"Failed to parse malformed tool call: {e}")
    return None

async def call_ollama(messages: list, tools: list = None, tool_choice: str = None) -> dict:
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "think": False  
    }
    if tools:
        payload["tools"] = tools
    if tool_choice:
        payload["tool_choice"] = tool_choice

    async with httpx.AsyncClient(
        timeout=300.0,
        headers={"ngrok-skip-browser-warning": "true", "User-Agent": "python-httpx"}
    ) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload
        )
        return response.json()

async def execute_tool_calls(
    tool_calls: list,
    session_id: str,
    messages: list
) -> list:
    """
    Mengeksekusi seluruh tool call yang dikembalikan oleh LLM melalui MCP.
    """

    tools_used = []

    # Tool yang membutuhkan session_id
    SESSION_TOOLS = {
        "save_expense",
        "get_expenses",
        "delete_expense",
        "add_agenda",
        "get_agenda",
        "delete_agenda",
        "sync_agenda_to_calendar",
        "get_calendar_events",
        "send_expense_report_to_telegram",
        "send_agenda_reminder_to_telegram",
    }

    for tool_call in tool_calls:

        function = tool_call.get("function", {})
        tool_name = function.get("name")
        raw_args = function.get("arguments", {})

        print("=" * 70)
        print("RAW TOOL CALL")
        print(json.dumps(tool_call, indent=2, ensure_ascii=False))
        print("=" * 70)

        # -----------------------------
        # Parse arguments
        # -----------------------------
        try:
            if isinstance(raw_args, str):
                tool_args = json.loads(raw_args)
            elif isinstance(raw_args, dict):
                tool_args = raw_args.copy()
            else:
                tool_args = {}
        except Exception as e:
            print(f"[ERROR] Gagal parse tool arguments: {e}")
            tool_args = {}

        # -----------------------------
        # Inject session_id bila diperlukan
        # -----------------------------
        if tool_name in SESSION_TOOLS:
            tool_args["session_id"] = session_id

        print(f"[MCP] EXECUTING : {tool_name}")
        print(f"[MCP] ARGUMENTS : {json.dumps(tool_args, indent=2, ensure_ascii=False)}")

        # -----------------------------
        # Execute MCP Tool
        # -----------------------------
        try:
            tool_result = await execute_mcp_tool(
                tool_name,
                tool_args
            )
        except Exception as e:
            tool_result = {
                "success": False,
                "error": str(e)
            }

        print(f"[MCP] RESULT :")
        print(json.dumps(tool_result, indent=2, ensure_ascii=False))

        tools_used.append(tool_name)

        messages.append({
            "role": "tool",
            "content": json.dumps(tool_result, ensure_ascii=False)
        })

    return tools_used

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    full_history = get_history(request.session_id)
    history = full_history[-MAX_HISTORY_MESSAGES:] if len(full_history) > MAX_HISTORY_MESSAGES else full_history
    today = datetime.now().strftime("%Y-%m-%d")

    context_chunks = []
    context_used = False
    if request.use_rag:
        query_embedding = await get_embedding(request.message)
        context_chunks = search_similar(request.session_id, query_embedding, n_results=3)
        context_used = len(context_chunks) > 0

    system_content = SYSTEM_PROMPT + f"\n\nHari ini: {today}"
    if context_chunks:
        context_text = "\n\n---\n\n".join(context_chunks)
        system_content += f"\n\n## KONTEKS DOKUMEN:\n{context_text}"

    # Load tools dynamically dari MCP Servers
    tools_definition = await get_all_tools()

    messages = [
        {"role": "system", "content": system_content},
        *history,
        {"role": "system", "content": TOOL_REINFORCEMENT},
        {"role": "user", "content": request.message}
    ]

    forced_choice = "auto"
    print(f"Tool choice mode: {forced_choice}")

    # First call
    data = await call_ollama(messages, tools=tools_definition, tool_choice=forced_choice)
    response_message = data["message"]
    tools_used = []

    print("=" * 50)
    print("FIRST CALL RESPONSE:", json.dumps(response_message, indent=2, ensure_ascii=False))

    if response_message.get("tool_calls"):
        messages.append(response_message)
        tools_used = await execute_tool_calls(response_message["tool_calls"], request.session_id, messages)
        final_data = await call_ollama(messages)
        reply = final_data["message"]["content"]

    else:
        reply = response_message["content"]

        # Cek malformed tool call
        malformed = try_parse_malformed_tool_call(reply)
        if malformed:
            print(f"RECOVERED malformed tool call: {malformed}")
            malformed_args = malformed["arguments"]
            malformed_args["session_id"] = request.session_id
            tool_result = await execute_mcp_tool(malformed["name"], malformed_args)
            tools_used.append(malformed["name"])

            messages.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": malformed["name"], "arguments": malformed["arguments"]}}]
            })
            messages.append({"role": "tool", "content": json.dumps(tool_result, ensure_ascii=False)})

            final_data = await call_ollama(messages)
            reply = final_data["message"]["content"]

        elif is_hallucinated_claim(reply):
            print("HALLUCINATION DETECTED! Retrying...")

            retry_messages = [
                {"role": "system", "content": system_content},
                *history,
                {"role": "system", "content": TOOL_REINFORCEMENT},
                {"role": "user", "content": request.message},
                {"role": "system", "content": HALLUCINATION_RETRY_PROMPT}
            ]

            retry_data = await call_ollama(retry_messages, tools=tools_definition, tool_choice="required")
            retry_response = retry_data["message"]

            print("RETRY RESPONSE:", json.dumps(retry_response, indent=2, ensure_ascii=False))

            if retry_response.get("tool_calls"):
                retry_messages.append(retry_response)
                tools_used = await execute_tool_calls(retry_response["tool_calls"], request.session_id, retry_messages)
                final_data = await call_ollama(retry_messages)
                reply = final_data["message"]["content"]
            else:
                reply = "Maaf, sepertinya saya kesulitan memproses permintaan itu. Bisa diulangi dengan kalimat yang lebih spesifik?"

    print("=" * 50)

    add_message(request.session_id, "user", request.message)
    add_message(request.session_id, "assistant", reply)

    return ChatResponse(
        reply=reply,
        session_id=request.session_id,
        context_used=context_used,
        tools_used=tools_used
    )

@router.delete("/chat/{session_id}")
async def clear_chat(session_id: str):
    from services.session import clear_history
    clear_history(session_id)
    return {"message": f"History sesi {session_id} dihapus"}