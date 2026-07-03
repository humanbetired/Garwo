import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MCP_SERVERS = {
    "expense": os.path.join(BASE_DIR, "../mcp-servers/expense/server.py"),
    "agenda": os.path.join(BASE_DIR, "../mcp-servers/agenda/server.py"),
    "websearch": os.path.join(BASE_DIR, "../mcp-servers/websearch/server.py"),
    "gcalendar": os.path.join(BASE_DIR, "../mcp-servers/gcalendar/server.py"),
    "telegram": os.path.join(BASE_DIR, "../mcp-servers/telegram/server.py"),
}

async def get_all_tools() -> list:
    all_tools = []
    for server_name, server_path in MCP_SERVERS.items():
        try:
            server_params = StdioServerParameters(command="python", args=[server_path])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_response = await session.list_tools()
                    for tool in tools_response.tools:
                        all_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema
                            }
                        })
        except Exception as e:
            print(f"Error connecting to {server_name} MCP Server: {e}")
    return all_tools

async def execute_mcp_tool(tool_name: str, tool_args: dict) -> dict:
    TOOL_SERVER_MAP = {
    "save_expense": "expense",
    "get_expenses": "expense",
    "delete_expense": "expense",
    "add_agenda": "agenda",
    "get_agenda": "agenda",
    "delete_agenda": "agenda",
    "search_web": "websearch",
    "get_weather": "websearch",
    "sync_agenda_to_calendar": "gcalendar",
    "get_calendar_events": "gcalendar",
    "delete_calendar_event": "gcalendar",
    "send_telegram_message": "telegram",
    "get_telegram_messages": "telegram",
    "send_expense_report_to_telegram": "telegram",
    "send_agenda_reminder_to_telegram": "telegram",
}

    server_name = TOOL_SERVER_MAP.get(tool_name)
    if not server_name:
        return {"error": f"Tool '{tool_name}' tidak dikenali"}

    server_path = MCP_SERVERS[server_name]
    try:
        server_params = StdioServerParameters(command="python", args=[server_path])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, tool_args)
                if result.content:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        try:
                            return json.loads(content.text)
                        except:
                            return {"result": content.text}
                return {"success": True}
    except Exception as e:
        return {"error": str(e)}