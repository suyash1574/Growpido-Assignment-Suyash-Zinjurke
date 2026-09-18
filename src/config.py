import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Groq LLM Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

# NVIDIA Fallback Settings
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

# Search Settings (Live OSINT)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
USE_LIVE_SEARCH = os.getenv("USE_LIVE_SEARCH", "true").lower() == "true"

# Storage Settings
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(ROOT_DIR / "data" / "growpido.db"))
DATABASE_URL = os.getenv("DATABASE_URL", "")

# UI & Operational
ENABLE_HUMAN_GATE = os.getenv("ENABLE_HUMAN_GATE", "true").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
