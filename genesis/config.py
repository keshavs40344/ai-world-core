"""
genesis/config.py
=================
Central configuration for Project Genesis.
All tuneable parameters live here; override via environment variables or a
local `.env` file at the project root.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (silently ignored if absent)
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR          = _ROOT
GENESIS_DIR       = ROOT_DIR / "genesis"
RADAR_DIR         = ROOT_DIR / "radar"
FOUNDRY_DIR       = ROOT_DIR / "foundry"
VAULT_DIR         = ROOT_DIR / "vault"
PROJECTS_DIR      = VAULT_DIR / "projects"
GOVERNANCE_DIR    = ROOT_DIR / "governance"
WORKERS_DIR       = ROOT_DIR / "workers"
MANIFESTS_DIR     = ROOT_DIR / "manifests"
LOGS_DIR          = ROOT_DIR / "logs"
RELEASE_GATE_DIR  = ROOT_DIR / "release_gate"
DASHBOARD_DIR     = ROOT_DIR / "dashboard"

# Auto-create critical directories
for _d in [PROJECTS_DIR, MANIFESTS_DIR, LOGS_DIR, RELEASE_GATE_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

STATE_DB_PATH     = GENESIS_DIR / "state.db"
CHROMA_PATH       = str(VAULT_DIR / "chromadb")
DIGEST_LOG_PATH   = LOGS_DIR / "daily_digest.jsonl"
MANIFEST_PATH     = MANIFESTS_DIR / "project_manifest.json"


# ---------------------------------------------------------------------------
# Ollama / LLM
# ---------------------------------------------------------------------------

OLLAMA_HOST          = os.getenv("OLLAMA_HOST", "https://mariah-unprescinded-appreciatively.ngrok-free.dev")

# HTTP headers for Ollama requests (including ngrok bypass header)
OLLAMA_HEADERS: dict[str, str] = {
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "ProjectGenesis/1.0",
}

# Primary model — change via OLLAMA_PRIMARY_MODEL env var
OLLAMA_PRIMARY_MODEL = os.getenv("OLLAMA_PRIMARY_MODEL", "qwen2.5-coder:7b")

# Fallback chain — invoked automatically under memory pressure (ascending size)
OLLAMA_FALLBACK_MODELS: list[str] = [
    m.strip()
    for m in os.getenv(
        "OLLAMA_FALLBACK_MODELS", "qwen2.5-coder:7b"
    ).split(",")
    if m.strip()
]

# RAM threshold (GB) below which we step down to the next fallback model
OLLAMA_RAM_THRESHOLD_GB = float(os.getenv("OLLAMA_RAM_THRESHOLD_GB", "4.0"))

# Ollama generation options
OLLAMA_TEMPERATURE  = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
OLLAMA_CTX_WINDOW   = int(os.getenv("OLLAMA_CTX_WINDOW", "4096"))


# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

# On Windows with Docker Desktop, the named pipe is the native socket
DOCKER_SOCKET = os.getenv(
    "DOCKER_SOCKET",
    "npipe:////./pipe/docker_engine"   # Windows Docker Desktop default
)
WORKER_IMAGE_NAME = os.getenv("WORKER_IMAGE_NAME", "genesis-worker:latest")
WORKER_DOCKERFILE  = str(WORKERS_DIR / "Dockerfile.worker")
CONTAINER_TIMEOUT_SEC = int(os.getenv("CONTAINER_TIMEOUT_SEC", "300"))  # 5 min


# ---------------------------------------------------------------------------
# ChromaDB / Embeddings
# ---------------------------------------------------------------------------

CHROMA_HOST          = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT          = int(os.getenv("CHROMA_PORT", "8000"))

# Embedding model (runs locally via sentence-transformers)
EMBEDDING_MODEL      = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Collection names
CHROMA_COLLECTION_CODE     = "code_helpers"
CHROMA_COLLECTION_DOCS     = "project_docs"
CHROMA_COLLECTION_FAILURES = "failure_archive"


# ---------------------------------------------------------------------------
# Scheduler / Engine
# ---------------------------------------------------------------------------

# How often the main RADAR→FOUNDRY cycle fires (seconds)
CYCLE_INTERVAL_SEC = int(os.getenv("CYCLE_INTERVAL_SEC", "3600"))   # 1 hour

# Maximum concurrent FOUNDRY worker containers
MAX_CONCURRENT_WORKERS = int(os.getenv("MAX_CONCURRENT_WORKERS", "2"))

# Circuit breaker: max test iterations before archiving failure
CIRCUIT_BREAKER_LIMIT = int(os.getenv("CIRCUIT_BREAKER_LIMIT", "5"))

# RADAR: max projects to keep in the backlog queue
BACKLOG_MAX_SIZE = int(os.getenv("BACKLOG_MAX_SIZE", "20"))


# ---------------------------------------------------------------------------
# RADAR Scraping
# ---------------------------------------------------------------------------

# Rate limit between outbound HTTP requests (seconds)
RADAR_RATE_LIMIT_SEC = float(os.getenv("RADAR_RATE_LIMIT_SEC", "1.5"))

# How many top PyPI packages to analyse per cycle
RADAR_PYPI_TOP_N = int(os.getenv("RADAR_PYPI_TOP_N", "50"))

# GitHub topics to scan (comma-separated)
RADAR_GITHUB_TOPICS = [
    t.strip()
    for t in os.getenv(
        "RADAR_GITHUB_TOPICS",
        "developer-tools,automation,cli,local-first,open-source"
    ).split(",")
    if t.strip()
]


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------

# Tier A: digest is written silently; Tier B: execution freezes
TIER_B_POLL_INTERVAL_SEC = int(os.getenv("TIER_B_POLL_INTERVAL_SEC", "30"))
TIER_B_TIMEOUT_HOURS     = float(os.getenv("TIER_B_TIMEOUT_HOURS", "72.0"))


# ---------------------------------------------------------------------------
# Monetization (Stub — disabled in v1)
# ---------------------------------------------------------------------------

MONETIZATION_ENABLED      = os.getenv("MONETIZATION_ENABLED", "false").lower() == "true"
OPERATING_RESERVE_PERCENT = float(os.getenv("OPERATING_RESERVE_PERCENT", "25.0"))
PAYOUT_API_KEY            = os.getenv("PAYOUT_API_KEY", "")   # Must be set manually


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_active_model(available_ram_gb: float) -> str:
    """Return the best model that fits within available RAM."""
    if available_ram_gb >= OLLAMA_RAM_THRESHOLD_GB:
        return OLLAMA_PRIMARY_MODEL
    for fallback in OLLAMA_FALLBACK_MODELS:
        return fallback  # Return first available fallback
    return OLLAMA_PRIMARY_MODEL
