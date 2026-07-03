import os
import json
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

mcp = FastMCP("Garwo Telegram")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"



@mcp.tool()
async def send_telegram_message(message: str) -> dict:
    """
    Kirim pesan ke Telegram pribadi Garwo.

    Tool ini SELALU mengirim pesan ke chat yang telah dikonfigurasi
    melalui TELEGRAM_CHAT_ID pada file .env.

    Args:
        message: Isi pesan yang ingin dikirim.
    """

    if not BOT_TOKEN:
        return {
            "success": False,
            "error": "TELEGRAM_BOT_TOKEN tidak ditemukan pada .env"
        }

    if not DEFAULT_CHAT_ID:
        return {
            "success": False,
            "error": "TELEGRAM_CHAT_ID tidak ditemukan pada .env"
        }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/sendMessage",
                json={
                    "chat_id": DEFAULT_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown",
                },
            )

            response.raise_for_status()
            data = response.json()

    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Gagal menghubungi Telegram API: {str(e)}",
        }

    if not data.get("ok"):
        return {
            "success": False,
            "error": data.get("description", "Unknown Telegram API error"),
        }

    return {
        "success": True,
        "message": "Pesan berhasil dikirim ke Telegram",
        "message_id": data["result"]["message_id"],
    }

@mcp.tool()
async def get_telegram_messages(limit: int = 10) -> list:
    """
    Baca pesan terbaru dari Telegram.
    Gunakan saat user ingin melihat pesan masuk di Telegram mereka.
    
    Args:
        limit: Jumlah pesan yang ingin dibaca (default 10)
    """
    if not BOT_TOKEN:
        return [{"error": "TELEGRAM_BOT_TOKEN tidak ditemukan"}]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/getUpdates",
            params={"limit": limit, "allowed_updates": ["message"]}
        )
        data = response.json()

    if not data.get("ok"):
        return [{"error": data.get("description")}]

    messages = []
    for update in data.get("result", []):
        msg = update.get("message", {})
        if msg:
            messages.append({
                "message_id": msg.get("message_id"),
                "from": msg.get("from", {}).get("first_name", "Unknown"),
                "text": msg.get("text", ""),
                "date": datetime.fromtimestamp(msg.get("date", 0)).strftime("%Y-%m-%d %H:%M")
            })

    return messages if messages else [{"info": "Tidak ada pesan baru"}]

@mcp.tool()
async def send_expense_report_to_telegram(session_id: str, period: str = "today") -> dict:
    """
    Kirim laporan pengeluaran ke Telegram.
    Gunakan saat user ingin mendapat laporan pengeluaran via Telegram.
    
    Args:
        session_id: ID sesi user
        period: Periode laporan - today, week, month
    """
    import json as json_module
    import os

    DATA_DIR = os.path.join(os.path.dirname(__file__), "../../backend/data")
    file_path = os.path.join(DATA_DIR, f"{session_id}_expenses.json")

    if not os.path.exists(file_path):
        return await send_telegram_message("Belum ada data pengeluaran.")

    with open(file_path) as f:
        expenses = json_module.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now()

    if period == "today":
        filtered = [e for e in expenses if e["date"] == today]
        period_label = "Hari Ini"
    elif period == "week":
        filtered = [e for e in expenses if (now - datetime.strptime(e["date"], "%Y-%m-%d")).days <= 7]
        period_label = "7 Hari Terakhir"
    else:
        filtered = [e for e in expenses if e["date"].startswith(now.strftime("%Y-%m"))]
        period_label = "Bulan Ini"

    total = sum(e["amount"] for e in filtered)
    by_category = {}
    for e in filtered:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + e["amount"]

    # Format pesan
    report = f"*Laporan Pengeluaran — {period_label}*\n\n"
    report += f"*Total: Rp {total:,.0f}*\n\n"

    if by_category:
        report += "*Per Kategori:*\n"
        emoji_map = {
            "food": "🍽️", "transport": "🚗", "health": "💊",
            "entertainment": "🎬", "shopping": "🛍️", "other": "📦"
        }
        for cat, amount in by_category.items():
            emoji = emoji_map.get(cat, "📌")
            report += f"{emoji} {cat.capitalize()}: Rp {amount:,.0f}\n"

    if filtered:
        report += f"\n*Detail ({len(filtered)} transaksi):*\n"
        for e in filtered[-5:]:  # tampilkan 5 terakhir
            report += f"• {e['description']}: Rp {e['amount']:,.0f}\n"

    report += f"\nDikirim oleh Garwo"

    return await send_telegram_message(report)

@mcp.tool()
async def send_agenda_reminder_to_telegram(session_id: str) -> dict:
    """
    Kirim reminder agenda hari ini ke Telegram.
    Gunakan saat user ingin mendapat reminder jadwal via Telegram.
    
    Args:
        session_id: ID sesi user
    """
    import json as json_module
    import os

    DATA_DIR = os.path.join(os.path.dirname(__file__), "../../backend/data")
    file_path = os.path.join(DATA_DIR, f"{session_id}_agenda.json")
    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(file_path):
        return await send_telegram_message("Tidak ada agenda hari ini.")

    with open(file_path) as f:
        agendas = json_module.load(f)

    today_agendas = [a for a in agendas if a["date"] == today]

    if not today_agendas:
        message = "*Agenda Hari Ini*\n\nTidak ada agenda hari ini. Santai dulu!"
    else:
        message = f"*Agenda Hari Ini — {today}*\n\n"
        for agenda in today_agendas:
            time_str = f"{agenda['time']}" if agenda.get('time') else "Sepanjang hari"
            message += f"*{agenda['title']}*\n{time_str}\n"
            if agenda.get('notes'):
                message += f"{agenda['notes']}\n"
            message += "\n"
        message += "Dikirim oleh Garwo "

    return await send_telegram_message(message)

if __name__ == "__main__":
    mcp.run(transport="stdio")