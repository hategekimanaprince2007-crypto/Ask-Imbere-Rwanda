import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from groq import Groq
from conversation_engine import classify_message


# =========================================================
# IMBERE_RWANDA AI - PRODUCTION-READY FASTAPI BACKEND
# =========================================================

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("imbere_rwanda")

BASE_DIR = Path(__file__).resolve().parent
WEBSITE_DIR = Path(os.getenv("WEBSITE_DIR", str(BASE_DIR / "website")))

# On Render, set DB_PATH=/var/data/imbere_rwanda.db and attach
# a persistent disk mounted at /var/data if using SQLite.
DB_PATH = Path(
    os.getenv(
        "DB_PATH",
        str(BASE_DIR / "data" / "imbere_rwanda.db"),
    )
)

SUPPORTED_LANGUAGES = {"en", "rw", "fr", "sw"}

CATEGORY_NAMES = {
    "agriculture": "Agriculture",
    "healthcare": "Healthcare",
    "culture": "Culture and Traditions",
    "genocide_1994": "History",
    "education": "Education",
    "tourism": "Tourism and Heritage",
}

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# Groq is initialized only when a key is configured. Missing API keys
# do not prevent the website or knowledge-library API from starting.
groq_client = (
    Groq(api_key=GROQ_API_KEY, timeout=45.0, max_retries=1)
    if GROQ_API_KEY
    else None
)

app = FastAPI(
    title="Imbere_Rwanda AI",
    description="A Rwanda-focused multilingual knowledge and conversation assistant",
    version="2.0.0",
)

# Set CORS_ORIGINS on Render to a comma-separated list of trusted
# frontend origins. Example: https://your-site.onrender.com
cors_origins_raw = os.getenv("CORS_ORIGINS", "*").strip()
cors_origins = (
    ["*"]
    if cors_origins_raw == "*"
    else [origin.strip().rstrip("/") for origin in cors_origins_raw.split(",") if origin.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    language: str = "en"
    category: str | None = None
    # Optional recent conversation context from the frontend.
    # Only user/assistant messages are accepted; maximum 8 entries.
    history: list[dict] = Field(default_factory=list, max_length=8)
