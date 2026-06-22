import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.db.client import SupabaseDB
from src.api import auth, chat
from src.middleware.audit_logger import audit_chat_request
from src.middleware.rate_limiter import rate_limit_chat
from src.middleware.jwt_auth import jwt_auth_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    SupabaseDB.init()
    print("Supabase connection initialized")
    yield
    print("Shutting down...")

app = FastAPI(
    title="Electricity Bill Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middlewares
app.middleware("http")(rate_limit_chat)
app.middleware("http")(audit_chat_request)
app.middleware("http")(jwt_auth_middleware)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/health")
async def health():
    return {"status": "ok", "phase": "3.3"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("src.main:app", host="127.0.0.1", port=port, reload=True)