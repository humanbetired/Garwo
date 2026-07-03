from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, rag
from config import APP_NAME

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(rag.router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "ok", "app": APP_NAME}