"""
VEDA — Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID      = os.getenv("GCP_PROJECT_ID",    "veda-491808")
LOCATION        = os.getenv("GCP_LOCATION",       "us-central1")
BQ_DATASET      = os.getenv("BQ_DATASET",         "veda_ma_diligence")
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-flash")
MCP_SERVER_URL  = os.getenv("MCP_SERVER_URL",     "http://localhost:8001")
GITHUB_TOKEN = os.getenv("", "")