# VEDA — Venture Evaluation & Due Diligence Agent

> **Google Cloud Gen AI Academy APAC Edition — Top 100 Shortlisted**
> Multi-Agent AI System for M&A Due Diligence · Powered by Vertex AI & Gemini 2.5 Flash

[![Status](https://img.shields.io/badge/Status-Live-brightgreen)](https://veda-api-790567978781.us-central1.run.app/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-blue)](https://cloud.google.com/vertex-ai)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Enabled-orange)](https://cloud.google.com/vertex-ai)
[![BigQuery](https://img.shields.io/badge/BigQuery-5%20Tables-yellow)](https://cloud.google.com/bigquery)
[![MCP](https://img.shields.io/badge/MCP-GitHub%20%7C%20Calendar%20%7C%20Tasks-purple)](https://github.com/RudyMontoo/VEDA)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-success)](https://veda-api-790567978781.us-central1.run.app/)

---

## 🔗 Live Demo

**Production URL:** [https://veda-api-790567978781.us-central1.run.app](https://veda-api-790567978781.us-central1.run.app)

**Demo Video:** [Watch on Google Drive](https://drive.google.com/file/d/1-lnddI3YflZG5HpdHcVVI-lnChE-ke-r/view?usp=drive_link)

---

## The Problem

M&A due diligence takes **6–12 weeks** and costs lakhs in consulting fees. Investors still miss critical risks — hidden technical debt, regulatory violations, and compliance gaps that surface only after the deal closes.

VEDA solves this. **Enter a company name and GitHub URL. Get a complete boardroom-ready due diligence report in under 5 minutes.**

> *Audit. Analyse. Acquire.*

---

## What VEDA Does

VEDA deploys **5 specialised AI agents** coordinated by a Primary Orchestrator:

| Agent | Role | Technology |
|---|---|---|
| **Primary Agent** | Orchestrates the full pipeline | Gemini 2.5 Flash + asyncio |
| **Code Auditor** | Scans GitHub repo — 25+ real signals | MCP → GitHub API (deterministic scoring) |
| **Regulatory Scout** | Checks 40+ Indian regulations | Gemini 2.5 Flash + 6 industry frameworks |
| **Market Analyst** | Bear / Base / Bull 3-year simulation | Gemini 2.5 Flash + INR benchmarks |
| **Executive Summary** | Weighted scoring matrix → board verdict | Gemini 2.5 Flash (narrative only) |
| **Competitor Intelligence** | Finds 3 real competitors, scores them on GitHub | Gemini 2.5 Flash + GitHub API |

---

## Architecture

```
Browser (Google OAuth Login)
          │
          ▼
┌─────────────────────────────────────────┐
│     FastAPI — Google Cloud Run          │
│     WebSocket · REST API · MCP Proxy    │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    Primary Agent     │  ← Orchestrator
        │   (Gemini 2.5 Flash) │
        └──┬───┬───┬───┬───┬──┘
           │   │   │   │   │
           ▼   ▼   ▼   ▼   ▼
        [1]  [2]  [3]  [4]  [5]
        Code  Reg  Mkt  Exec Competitor
        Audit Scout Anl  Sum  Intel
           │              │
           ▼              ▼
      MCP Server     Gemini 2.5
      (GitHub API)   Flash (Vertex AI)
           │
           ▼
    ┌──────────────────┐
    │    BigQuery      │
    │  5 structured    │
    │  tables          │
    └──────────────────┘
           │
           ▼
    Google Calendar API
    (per-user OAuth token)
```

---

## Key Features

**Scoring Intelligence — Not Just LLM Guessing**

The Code Auditor uses a deterministic weighted formula from real GitHub signals. The Executive Summary uses a fixed scoring matrix — Gemini writes the narrative, the algorithm decides the verdict.

```
Final Recommendation Score = Tech Debt (35%) + Compliance (35%) + Market Fit (30%)
```

**Real MCP Integrations**

| Tool | Endpoint | What It Does |
|---|---|---|
| GitHub API | `POST /github/repo` | 25+ signals: commits, CI/CD, tests, security, PRs, contributors |
| Google Calendar | `POST /calendar/schedule` | Creates kickoff meeting in logged-in user's calendar |
| Google Tasks | `POST /tasks/create_checklist` | Auto-creates 6-item M&A checklist per audit |
| Google Tasks | `POST /tasks/create` | Adds custom tasks from the UI |
| Google Tasks | `GET /tasks/list` | Lists upcoming tasks in dashboard |

**Per-User Google Integration**

Every user signs in with Google OAuth. Calendar events and tasks go to **their own** Google Calendar — not a shared service account. Multi-user ready.

**Competitor Intelligence (Agent 5)**

After the main audit, VEDA automatically discovers 3 real competitors using Gemini + GitHub, scores them, and produces:
- Competitive position badge (Market Leader / Strong Challenger / Niche Player)
- GitHub score for each competitor (stars, commits, CI/CD, tests)
- Threat level assessment (LOW / MEDIUM / HIGH)
- Acquisition rationale — why this company vs its competitors

---

## Indian Regulatory Frameworks

VEDA checks compliance across 6 industry verticals with specific Indian laws:

| Industry | Laws Checked |
|---|---|
| **Fintech** | RBI Cloud Outsourcing, PMLA, PSS Act, SEBI guidelines |
| **Healthtech** | DISHA, CDSCO, Telemedicine Guidelines 2020 |
| **Edtech** | NEP 2020, PDPB 2023 (children's data), UDISE |
| **SaaS** | IT Act Section 43A, PDPB 2023, GST, RBI Cloud |
| **E-Commerce** | Consumer Protection Rules 2020, FDI Policy |
| **Deeptech** | Patents Act 1970, SCOMET Export Controls |

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Vertex AI · Gemini 2.5 Flash |
| Backend | FastAPI · Python 3.12 · uvicorn |
| Real-time | WebSocket (live agent progress) |
| Database | Google BigQuery (5 structured tables) |
| MCP Tools | GitHub API · Google Calendar API · Google Tasks API |
| Auth | Google OAuth 2.0 (per-user sessions) |
| PDF | ReportLab |
| Deployment | Google Cloud Run (auto-scaling, serverless) |
| CI/CD | Google Cloud Build · Artifact Registry |

---

## Project Structure

```
VEDA/
├── agents/
│   ├── primary_agent.py            # Orchestrator — async pipeline, timeouts
│   ├── code_auditor.py             # Agent 1 — GitHub scanning, deterministic scoring
│   ├── regulatory_scout.py         # Agent 2 — 6 industry compliance frameworks
│   ├── market_analyst.py           # Agent 3 — Bear/Base/Bull simulation
│   ├── executive_summary.py        # Agent 4 — Weighted matrix + board report
│   └── competitor_intelligence.py  # Agent 5 — GitHub competitor scoring
│
├── api/
│   ├── main.py                     # FastAPI app — REST + WebSocket + MCP proxy
│   ├── auth.py                     # Google OAuth 2.0 + session management
│   └── progress_manager.py         # WebSocket broadcast manager
│
├── db/
│   ├── bigquery_client.py          # All BigQuery CRUD operations
│   └── setup_schema.py             # Creates 5 BigQuery tables (run once)
│
├── mcp_server/
│   └── server.py                   # MCP Server v3 — GitHub, Calendar, Tasks
│
├── utils/
│   ├── vertex_helper.py            # Gemini wrapper — retry, logging, timeout
│   ├── pdf_generator.py            # ReportLab PDF generator
│   └── config.py                   # Centralised environment config
│
├── static/
│   ├── index.html                  # Dashboard — Audit, Compare, Tasks tabs
│   └── login.html                  # Google OAuth login page
│
├── Dockerfile                      # Cloud Run container
└── requirements.txt
```

---

## BigQuery Schema

| Table | Purpose |
|---|---|
| `audit_jobs` | Job lifecycle — status, timestamps, user email |
| `audit_reports` | Full report JSON — all agent outputs |
| `risk_scores` | Per-agent scores for analytics |
| `agent_events` | WebSocket audit trail — step-by-step events |
| `error_logs` | Structured error logs with traceback |

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/audit` | Start a due diligence audit |
| `WS` | `/ws/{job_id}` | Live agent progress (WebSocket) |
| `GET` | `/status/{job_id}` | Poll audit status |
| `GET` | `/report/{job_id}` | Full JSON report |
| `GET` | `/report/{job_id}/pdf` | Download PDF report |
| `POST` | `/compare` | Compare 2 companies side-by-side |
| `GET` | `/compare/result` | Get comparison winner |
| `GET` | `/jobs` | List recent audits |
| `GET` | `/health` | Health check |
| `GET` | `/auth/me` | Current logged-in user |
| `GET` | `/mcp/tasks/list` | Proxy → user's Google Tasks |
| `POST` | `/mcp/tasks/create` | Proxy → create task in user's calendar |

---

## Quick Start

### Prerequisites
- Google Cloud Project with Vertex AI + BigQuery enabled
- GitHub Personal Access Token (`public_repo` scope)
- Google OAuth 2.0 client credentials

### 1. Clone & Configure

```bash
git clone https://github.com/RudyMontoo/VEDA.git
cd VEDA
cp .env.example .env
# Fill in: GCP_PROJECT_ID, GITHUB_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
```

### 2. Setup BigQuery

```bash
gcloud auth application-default login
python db/setup_schema.py
```

### 3. Run Locally

```bash
# Terminal 1 — MCP Server
uvicorn mcp_server.server:app --port 8001

# Terminal 2 — Main API
export $(cat .env | grep -v '^#' | xargs)
uvicorn api.main:app --port 8080 --reload
```

### 4. Deploy to Cloud Run

```bash
python tests/test_e2e.py
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GCP_PROJECT_ID` | ✅ | Google Cloud project ID |
| `GCP_LOCATION` | ✅ | Region (us-central1) |
| `BQ_DATASET` | ✅ | BigQuery dataset name |
| `VERTEX_AI_MODEL` | ✅ | gemini-2.5-flash |
| `MCP_SERVER_URL` | ✅ | http://localhost:8001 |
| `GITHUB_TOKEN` | ✅ | GitHub PAT (public_repo scope) |
| `GOOGLE_CLIENT_ID` | ✅ | OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | OAuth 2.0 client secret |
| `OAUTH_REDIRECT_URI` | ✅ | OAuth callback URL |
| `SESSION_SECRET` | ✅ | Random secret for session signing |

---

## Sample Output

**Input:**
```json
{
  "company_name": "FastAPI Framework",
  "github_repo_url": "https://github.com/tiangolo/fastapi",
  "industry": "saas"
}
```

**Output:**
```json
{
  "overall_risk_score": 83.0,
  "executive_summary": {
    "recommendation": "PROCEED WITH CONDITIONS",
    "overall_rating": "BUY",
    "composite_score": 83.0,
    "one_line_verdict": "Strong technical foundation with minor compliance gaps — acquisition viable at ₹12–28Cr."
  },
  "code_audit": {
    "tech_debt_score": 90,
    "maintenance_health": "ACTIVE",
    "bus_factor_risk": "LOW",
    "security_flags": []
  },
  "regulatory": {
    "compliance_score": 65,
    "estimated_remediation_time": "1-2 months"
  },
  "market_forecast": {
    "market_fit_score": 78,
    "scenarios": {
      "bear": { "year3_arr_inr_lakhs": 240, "probability": "20%" },
      "base": { "year3_arr_inr_lakhs": 480, "probability": "55%" },
      "bull": { "year3_arr_inr_lakhs": 820, "probability": "25%" }
    }
  },
  "competitor_intelligence": {
    "competitive_position": "MARKET LEADER",
    "threat_level": "LOW",
    "competitors_found": 3
  }
}
```

---

## What Makes VEDA Different

| Aspect | Typical AI Tools | VEDA |
|---|---|---|
| Scoring | LLM guesses a number | Deterministic formula from 25+ real GitHub signals |
| Compliance | Generic checklist | 6 industry-specific Indian regulatory frameworks |
| Competitors | Not included | Agent 5 discovers + scores 3 real competitors via GitHub |
| Calendar/Tasks | Mocked | Real Google OAuth — goes to each user's own calendar |
| Real-time | Polling | WebSocket live agent streaming |
| Output | JSON only | JSON + PDF + Web Dashboard + BigQuery audit trail |
| Multi-user | Single user | Per-user OAuth sessions, each sees their own data |

---

## Built By

**Rudra Sharma** — First Year B.Tech Computer Science
Google Cloud Gen AI Academy APAC Edition 2025 · Top 100

---

*VEDA — Venture Evaluation & Due Diligence Agent*
*Powered by Vertex AI · Gemini 2.5 Flash · Google BigQuery · Google Cloud Run*

*Audit. Analyse. Acquire.*