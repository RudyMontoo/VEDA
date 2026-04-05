# VEDA — Venture Evaluation & Due Diligence Agent

> 🏆 **Google Gen AI APAC Hackathon 2025**
> Multi-Agent AI System for M&A Due Diligence · Powered by Vertex AI & Gemini 2.5 Flash

![Status](https://img.shields.io/badge/Status-Live-brightgreen)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-blue)
![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Enabled-orange)
![BigQuery](https://img.shields.io/badge/BigQuery-5%20Tables-yellow)
![MCP](https://img.shields.io/badge/MCP-GitHub%20%7C%20Calendar%20%7C%20Tasks-purple)
![Python](https://img.shields.io/badge/Python-3.12-blue)

---

## 🎯 Problem Statement

**Multi-Agent Productivity Assistant** — Build a multi-agent AI system that helps users manage tasks, schedules, and information by interacting with multiple tools and data sources.

**Core Requirements:**
- ✅ Primary agent coordinating one or more sub-agents
- ✅ Store and retrieve structured data from a database
- ✅ Integrate multiple tools via MCP (calendar, task manager, notes)
- ✅ Handle multi-step workflows and task execution
- ✅ Deploy as an API-based system

---

## 💡 Solution: VEDA

VEDA is an **Agentic M&A Due Diligence Suite** that automates the entire due diligence process for Mergers & Acquisitions using 4 specialised AI agents coordinated by a Primary Orchestrator Agent.

**What used to take 6–12 weeks → VEDA does in under 5 minutes.**

### Slogan
> *Audit. Analyse. Acquire.*

---

## 🏗️ Architecture

```
User Request (Web UI / REST API)
              │
              ▼
┌─────────────────────────────────────┐
│      Primary Agent                  │
│   (Investment Principal)            │  ← Orchestrator
│   primary_agent.py                  │
└──────────┬──────────────────────────┘
           │  Coordinates 4 Sub-Agents
    ┌──────┴────────────────────────────────┐
    ▼          ▼            ▼               ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌───────────────┐
│ Code   │ │  Reg.  │ │  Market  │ │   Executive   │
│Auditor │ │ Scout  │ │ Analyst  │ │   Summary     │
│Sub-Ag1 │ │Sub-Ag2 │ │ Sub-Ag3  │ │   Sub-Ag4    │
└───┬────┘ └───┬────┘ └────┬─────┘ └───────┬───────┘
    │          │           │               │
    ▼          ▼           ▼               ▼
MCP Server  Gemini 2.5  Gemini 2.5     Gemini 2.5
(GitHub)    Flash(RAG)  Flash(Sim)     Flash(Report)
    │
    ├── GitHub API (25+ signals)
    ├── Google Calendar API
    └── Google Tasks API
              │
              ▼
    ┌─────────────────┐
    │    BigQuery     │
    │   5 Tables      │
    │ audit_jobs      │
    │ audit_reports   │
    │ risk_scores     │
    │ agent_events    │
    │ error_logs      │
    └─────────────────┘
```

---

## 🤖 Multi-Agent System

| Agent | File | Role | Tools Used |
|-------|------|------|------------|
| **Primary Agent** | `agents/primary_agent.py` | Orchestrator — coordinates all sub-agents, manages pipeline | BigQuery, WebSocket, MCP |
| **Code Auditor** | `agents/code_auditor.py` | Scans GitHub repo, computes deterministic tech debt score | MCP → GitHub API (25+ signals) |
| **Regulatory Scout** | `agents/regulatory_scout.py` | Checks 40+ Indian regulations for compliance risk | Gemini 2.5 Flash + RAG |
| **Market Analyst** | `agents/market_analyst.py` | 3-year Bear/Base/Bull growth simulation | Gemini 2.5 Flash + benchmarks |
| **Executive Summary** | `agents/executive_summary.py` | Generates boardroom-ready report & recommendation | Gemini 2.5 Flash |

---

## 🛠️ MCP Integrations (Real, Not Mocked)

| Tool | Endpoint | What it does |
|------|----------|--------------|
| **GitHub API** | `POST /github/repo` | Fetches 25+ real signals: stars, commits, CI/CD, tests, security policy, PR merge time, contributor count |
| **Google Calendar** | `POST /calendar/schedule` | Creates real kickoff meeting events via Service Account |
| **Google Tasks** | `POST /tasks/create_checklist` | Auto-creates 6-item due diligence checklist when audit starts |
| **Google Tasks** | `POST /tasks/create` | Adds custom tasks with due dates from the UI |
| **Google Tasks** | `GET /tasks/list` | Fetches upcoming tasks for display in dashboard |

---

## 📊 Scoring Intelligence

Unlike simple LLM prompting, VEDA uses a **hybrid scoring system**:

### Code Auditor — Rule-Based + AI Blend
```
Final Score = (Gemini Score × 0.6) + (Rule Score × 0.4)
```

**25+ Real GitHub Signals Used:**
- Days since last commit (activity health)
- Commits in last 30/90 days (development pace)
- CI/CD pipeline count (automation maturity)
- Test directory presence (quality culture)
- Security policy file (security awareness)
- Open issues older than 90 days (maintenance debt)
- PR merge time average (team responsiveness)
- Contributor count (bus factor risk)
- README size (documentation quality)
- Release cadence (product maturity)
- Dependency files (package management)

### Regulatory Scout — 6 Industry Frameworks
- **Fintech**: RBI, SEBI, PMLA, PSS Act
- **Healthtech**: DISHA, CDSCO, Telemedicine Guidelines
- **Edtech**: NEP 2020, PDPB (children's data)
- **SaaS**: IT Act 43A, PDPB 2023, GST, RBI Cloud
- **E-Commerce**: Consumer Protection Rules, FDI Policy
- **Deeptech**: Patents Act, SCOMET Export Controls

### Market Analyst — Real Benchmarks
- Indian startup ARR benchmarks per industry
- GitHub traction signals (stars, forks, contributors)
- Tech debt impact on scaling velocity
- Compliance score impact on enterprise sales

---

## 📁 Project Structure

```
VEDA/
├── agents/
│   ├── primary_agent.py       # Orchestrator — coordinates all sub-agents
│   ├── code_auditor.py        # Sub-Agent 1 — GitHub scanning + rule-based scoring
│   ├── regulatory_scout.py    # Sub-Agent 2 — 6 industry compliance frameworks
│   ├── market_analyst.py      # Sub-Agent 3 — 3-year Bear/Base/Bull simulation
│   └── executive_summary.py   # Sub-Agent 4 — Boardroom report generation
│
├── api/
│   ├── main.py                # FastAPI app — 8 REST endpoints + WebSocket
│   └── progress_manager.py    # WebSocket broadcast manager
│
├── db/
│   ├── bigquery_client.py     # All BigQuery operations — 5 table CRUD
│   ├── setup_schema.py        # Run once — creates all BigQuery tables
│   └── test_connection.py     # Verify BigQuery connection
│
├── mcp_server/
│   └── server.py              # MCP Server — GitHub, Google Calendar, Google Tasks
│
├── utils/
│   ├── vertex_helper.py       # Gemini 2.5 Flash wrapper with retry logic
│   ├── pdf_generator.py       # ReportLab PDF report generator
│   └── config.py              # Environment configuration
│
├── static/
│   └── index.html             # Full web UI — Audit, Compare, Tasks tabs
│
├── tests/
│   └── test_e2e.py            # End-to-end test suite
│
├── Dockerfile                 # Main API container
├── Dockerfile.mcp             # MCP Server container
├── requirements.txt           # Python dependencies
└── .env.example               # Environment variables template
```

---

## ✅ Hackathon Requirements — How VEDA Meets Each One

| Requirement | Implementation | File |
|-------------|----------------|------|
| ✅ Primary agent coordinating sub-agents | `PrimaryAgent` runs async pipeline, delegates to 4 sub-agents | `agents/primary_agent.py` |
| ✅ Store & retrieve structured data | BigQuery — 5 tables with full CRUD | `db/bigquery_client.py` |
| ✅ Multiple MCP tools | GitHub API, Google Calendar, Google Tasks — all real | `mcp_server/server.py` |
| ✅ Multi-step workflows | Single `/audit` request → 4-agent sequential pipeline | `agents/primary_agent.py` |
| ✅ API-based deployment | FastAPI with 8 REST + WebSocket endpoints | `api/main.py` |

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/audit` | Start a new due diligence audit |
| `WS` | `/ws/{job_id}` | Live agent progress stream (WebSocket) |
| `GET` | `/status/{job_id}` | Poll audit status |
| `GET` | `/report/{job_id}` | Get full JSON report |
| `GET` | `/report/{job_id}/pdf` | Download PDF report |
| `POST` | `/compare` | Start side-by-side comparison of 2 companies |
| `GET` | `/compare/result` | Get comparison results |
| `GET` | `/jobs` | List recent audits |
| `GET` | `/health` | Health check |
| `GET` | `/mcp/tasks/list` | Proxy — list Google Tasks |
| `POST` | `/mcp/tasks/create` | Proxy — create Google Task |

---

## 🖥️ Web UI Features

| Tab | Features |
|-----|----------|
| 🔍 **Audit** | Company form, live agent progress bar, WebSocket updates, risk scores, radar chart, ARR forecast chart, Bear/Base/Bull scenarios, PDF download |
| ⚖️ **Compare** | Side-by-side audit of 2 companies, winner recommendation, color-coded metrics |
| 📋 **Tasks** | Add custom tasks to Google Calendar, view upcoming tasks, 6 quick templates (MCA filings, GST check, IP verification, etc.) |

---

## 🗄️ BigQuery Schema

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `audit_jobs` | Job lifecycle tracking | job_id, status, company_name, timestamps |
| `audit_reports` | Full report storage | job_id, overall_risk_score, report_json, recommendation |
| `risk_scores` | Per-agent analytics | tech_debt, compliance, market_fit, overall scores |
| `agent_events` | WebSocket audit trail | step, agent_name, status, progress_pct, event_data |
| `error_logs` | Debugging | job_id, agent_name, error_type, traceback |

---

## ⚡ Quick Start

### Prerequisites
- Google Cloud Project with Vertex AI + BigQuery enabled
- GitHub Personal Access Token (public_repo scope)
- Google Service Account with Calendar + Tasks access

### 1. Clone & Configure
```bash
git clone https://github.com/RudyMontoo/VEDA.git
cd VEDA
cp .env.example .env
# Fill in: GCP_PROJECT_ID, GITHUB_TOKEN, GOOGLE_CALENDAR_ID
```

### 2. Setup Database
```bash
gcloud auth application-default login
python db/setup_schema.py
python db/test_connection.py
```

### 3. Run
```bash
# Terminal 1 — MCP Server
cd VEDA
export $(cat .env | grep -v '^#' | xargs)
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001

# Terminal 2 — Main API
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Open Dashboard
```
http://localhost:8080
```

### 5. Run Tests
```bash
python tests/test_e2e.py
```

---

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GCP_PROJECT_ID` | ✅ | Google Cloud project ID |
| `GCP_LOCATION` | ✅ | Region (e.g. us-central1) |
| `BQ_DATASET` | ✅ | BigQuery dataset name |
| `VERTEX_AI_MODEL` | ✅ | Model name (gemini-2.5-flash) |
| `MCP_SERVER_URL` | ✅ | MCP server URL (http://localhost:8001) |
| `GITHUB_TOKEN` | ✅ | GitHub PAT for repo scanning |
| `GOOGLE_CALENDAR_ID` | ✅ | Calendar ID for scheduling |
| `GOOGLE_TASKS_LIST_ID` | ✅ | Tasks list ID |

---

## 🎬 Demo Output

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
  "code_audit": {
    "tech_debt_score": 90,
    "security_flags": [],
    "maintenance_health": "ACTIVE",
    "bus_factor_risk": "LOW"
  },
  "regulatory": {
    "compliance_score": 65,
    "red_flags": [],
    "estimated_remediation_time": "1-2 months"
  },
  "market_forecast": {
    "market_fit_score": 78.75,
    "scenarios": {
      "bear": { "year3_arr_inr_lakhs": 240, "probability": "20%" },
      "base": { "year3_arr_inr_lakhs": 480, "probability": "55%" },
      "bull": { "year3_arr_inr_lakhs": 820, "probability": "25%" }
    },
    "recommended_acquisition_price_range_inr_cr": { "min": 12, "max": 28 }
  },
  "executive_summary": {
    "recommendation": "PROCEED WITH CONDITIONS",
    "overall_rating": "BUY",
    "one_line_verdict": "Strong technical foundation with minor compliance gaps."
  }
}
```

---

## 🏆 What Makes VEDA Unique

| Feature | Others | VEDA |
|---------|--------|------|
| Scoring method | LLM guessing | Rule-based + AI blend (25+ real signals) |
| MCP integration | Mock/stub | Real GitHub, Calendar, Tasks APIs |
| Compliance | Generic | 6 industry-specific Indian regulatory frameworks |
| Forecast | Simple estimate | Bear/Base/Bull with INR benchmarks |
| Real-time | Polling | WebSocket live streaming |
| Output | JSON only | PDF report + Web UI + BigQuery |
| Workflow | Single agent | 4 specialised agents + orchestrator |

---

## 👨‍💻 Built By

**Rudra** — Gen AI APAC Hackathon 2025

---

*VEDA — Venture Evaluation & Due Diligence Agent*
*Powered by Vertex AI · Gemini 2.5 Flash · Google BigQuery · Google Cloud*

*Audit. Analyse. Acquire.*
