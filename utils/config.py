"""
VEDA — Central configuration.
All environment variables resolved here — nowhere else.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Google Cloud ──────────────────────────────────────────────────────────────
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "veda-491808")
LOCATION   = os.getenv("GCP_LOCATION",   "us-central1")

# ── BigQuery ──────────────────────────────────────────────────────────────────
BQ_DATASET = os.getenv("BQ_DATASET", "veda_ma_diligence")

# ── Vertex AI ─────────────────────────────────────────────────────────────────
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "gemini-2.5-flash")

# ── MCP Server ────────────────────────────────────────────────────────────────
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

# ── GitHub ────────────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# ── Agent timeouts (seconds) ──────────────────────────────────────────────────
AGENT_TIMEOUT_CODE       = int(os.getenv("AGENT_TIMEOUT_CODE",       "120"))
AGENT_TIMEOUT_REGULATORY = int(os.getenv("AGENT_TIMEOUT_REGULATORY", "60"))
AGENT_TIMEOUT_MARKET     = int(os.getenv("AGENT_TIMEOUT_MARKET",     "90"))
AGENT_TIMEOUT_SUMMARY    = int(os.getenv("AGENT_TIMEOUT_SUMMARY",    "60"))

# ── Validation ────────────────────────────────────────────────────────────────
if not GITHUB_TOKEN:
    logger.warning("GITHUB_TOKEN not set — GitHub API will use unauthenticated rate limits (60 req/hr)")

if not PROJECT_ID:
    raise EnvironmentError("GCP_PROJECT_ID is required")

# ── OAuth ─────────────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
OAUTH_REDIRECT_URI   = os.getenv("OAUTH_REDIRECT_URI", "")
SESSION_SECRET       = os.getenv("SESSION_SECRET", "change-me-in-production")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    logger.warning("Google OAuth credentials not set — login will not work")
