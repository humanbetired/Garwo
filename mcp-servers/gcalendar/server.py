import os
import json
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

mcp = FastMCP("Garwo Google Calendar")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    """Authenticate dan return Google Calendar service."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

@mcp.tool()
def sync_agenda_to_calendar(title: str, date: str, time: str = None, notes: str = None) -> dict:
    """
    Sync agenda/jadwal ke Google Calendar user.
    Gunakan setiap kali user menambahkan agenda baru yang perlu disimpan di Google Calendar.
    
    Args:
        title: Nama kegiatan
        date: Tanggal format YYYY-MM-DD
        time: Waktu format HH:MM (opsional)
        notes: Catatan tambahan (opsional)
    """
    try:
        service = get_calendar_service()

        if time:
            start_datetime = f"{date}T{time}:00"
            end_datetime = f"{date}T{time}:00"
            # Default durasi 1 jam
            end_dt = datetime.fromisoformat(start_datetime) + timedelta(hours=1)
            end_datetime = end_dt.isoformat()

            event = {
                "summary": title,
                "description": notes or "",
                "start": {
                    "dateTime": start_datetime,
                    "timeZone": "Asia/Jakarta"
                },
                "end": {
                    "dateTime": end_datetime,
                    "timeZone": "Asia/Jakarta"
                }
            }
        else:
            # All-day event kalau tidak ada jam
            event = {
                "summary": title,
                "description": notes or "",
                "start": {"date": date},
                "end": {"date": date}
            }

        result = service.events().insert(calendarId="primary", body=event).execute()

        return {
            "success": True,
            "event_id": result.get("id"),
            "event_link": result.get("htmlLink"),
            "message": f"'{title}' berhasil ditambahkan ke Google Calendar"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_calendar_events(days_ahead: int = 7) -> list:
    """
    Ambil event dari Google Calendar untuk beberapa hari ke depan.
    Gunakan saat user ingin melihat jadwal dari Google Calendar mereka.
    
    Args:
        days_ahead: Berapa hari ke depan yang ingin ditampilkan (default 7)
    """
    try:
        service = get_calendar_service()

        now = datetime.utcnow().isoformat() + "Z"
        end = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=end,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        result = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            result.append({
                "id": event.get("id"),
                "title": event.get("summary", "Tanpa judul"),
                "start": start,
                "description": event.get("description", ""),
                "link": event.get("htmlLink")
            })

        return result

    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def delete_calendar_event(event_id: str) -> dict:
    """
    Hapus event dari Google Calendar berdasarkan ID.
    
    Args:
        event_id: ID event Google Calendar yang ingin dihapus
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"success": True, "message": f"Event berhasil dihapus dari Google Calendar"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")