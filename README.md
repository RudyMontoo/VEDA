# VEDA — Venture Evaluation & Due Diligence Agent

> 🏆 Built for **Google Gen AI APAC Hackathon 2025**
> Multi-Agent AI System for M&A Due Diligence powered by Vertex AI & Gemini 2.5 Flash

![VEDA Dashboard](https://img.shields.io/badge/Status-Live-brightgreen)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-blue)
![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Enabled-orange)
![BigQuery](https://img.shields.io/badge/BigQuery-5%20Tables-yellow)

---

## 🎯 Problem Statement

**Multi-Agent Productivity Assistant** — Build a multi-agent AI system that helps users manage tasks, schedules, and information by interacting with multiple tools and data sources.

---

## 💡 Solution: VEDA

VEDA is an **Agentic M&A Due Diligence Suite** that automates the entire due diligence process for mergers and acquisitions using 4 specialized AI agents coordinated by a primary orchestrator.

---

## 🏗️ Architecture
```
User Request
     │
     ▼
┌─────────────────────────────┐
│   Primary Agent             │  ← Orchestrator (coordinates all agents)
│   (Investment Principal)    │
└─────────────┬───────────────┘
              │
    ┌─────────┼──────────┬──────────────┐
    ▼         ▼          ▼              ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ Code   │ │ Reg.   │ │ Market │ │Executive │
│Auditor │ │ Scout  │ │Analyst │ │ Summary  │
│Sub-Ag1 │ │Sub-Ag2 │ │Sub-Ag3 │ │ Sub-Ag4  │
└────┬───┘ └────┬───┘ └────┬───┘ └────┬─────┘
     │          │          │          │
     ▼          ▼          ▼          ▼
  MCP Server  Gemini    Gemini     Gemini
  (GitHub)   (RAG)    (Forecast)  (Report)
     │
     ▼
 BigQuery (5 Tables)
```

---

## 🤖 Multi-Agent System

| Agent | Role | Tools |
|-------|------|-------|
| **Primary Agent** | Orchestrator — coordinates all sub-agents | BigQuery, WebSocket |
| **Code Auditor** | Scans GitHub repo, scores technical debt | MCP → GitHub API |
| **Regulatory Scout** | Checks compliance (PDPB, GST, RBI) | Gemini 2.5 Flash |
| **Market Analyst** | 3-year Bear/Base/Bull forecast | Gemini 2.5 Flash |
| **Executive Summary** | Board-level report generation | Gemini 2.5 Flash |

---

## ✅ Hackathon Requirements Met

| Requirement | Implementation |
|-------------|----------------|
| ✅ Primary agent coordinating sub-agents | `PrimaryAgent` orchestrates 4 sub-agents sequentially |
| ✅ Store & retrieve structured data | BigQuery — 5 tables (audit_jobs, audit_reports, risk_scores, agent_events, error_logs) |
| ✅ Multiple tools via MCP | MCP Server exposes GitHub, Calendar, Tasks tools |
| ✅ Multi-step workflows | Single audit request triggers 4-agent pipeline |
| ✅ API-based deployment | FastAPI with `/audit`, `/status`, `/report`, `/ws` endpoints |

---

## 🛠️ Tech Stack

- **AI/ML:** Vertex AI, Gemini 2.5 Flash
- **Backend:** FastAPI, Python 3.12
- **Database:** Google BigQuery
- **MCP Server:** FastAPI + GitHub API
- **Frontend:** Vanilla JS + CSS (dark theme)
- **Real-time:** WebSockets
- **PDF:** ReportLab
- **Deploy:** Google Cloud Run

---

## 📁 Project Structure
```
VEDA/
├── agents/
│   ├── primary_agent.py      # Orchestrator
│   ├── code_auditor.py       # Sub-Agent 1 — GitHub scanning
│   ├── regulatory_scout.py   # Sub-Agent 2 — Compliance check
│   ├── market_analyst.py     # Sub-Agent 3 — 3-year forecast
│   └── executive_summary.py  # Sub-Agent 4 — Board report
├── api/
│   ├── main.py               # FastAPI app
│   └── progress_manager.py   # WebSocket manager
├── db/
│   ├── bigquery_client.py    # All DB operations
│   └── setup_schema.py       # Create BigQuery tables
├── mcp_server/
│   └── server.py             # MCP Server (GitHub, Calendar, Tasks)
├── utils/
│   ├── vertex_helper.py      # Gemini API wrapper
│   ├── pdf_generator.py      # PDF report generator
│   └── config.py             # Configuration
├── static/
│   └── index.html            # Web UI dashboard
├── Dockerfile                # Main API
├── Dockerfile.mcp            # MCP Server
└── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites
- Google Cloud Project with Vertex AI enabled
- BigQuery API enabled
- GitHub Personal Access Token

### 1. Clone & Setup
```bash
git clone https://github.com/RudyMontoo/VEDA.git
cd VEDA
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials:
# GCP_PROJECT_ID=your-project-id
# GITHUB_TOKEN=your-github-token
```

### 3. Setup Database
```bash
gcloud auth application-default login
python db/setup_schema.py
```

### 4. Run
```bash
# Terminal 1 — MCP Server
uvicorn mcp_server.server:app --port 8001

# Terminal 2 — Main API
uvicorn api.main:app --port 8080
```

### 5. Open Dashboard
```
http://localhost:8080
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/audit` | Start a new due diligence audit |
| `GET` | `/status/{job_id}` | Poll audit status |
| `GET` | `/report/{job_id}` | Get full JSON report |
| `GET` | `/report/{job_id}/pdf` | Download PDF report |
| `WS` | `/ws/{job_id}` | Live agent progress stream |
| `GET` | `/jobs` | List recent audits |
| `GET` | `/health` | Health check |

---

## 🎬 Demo

**Input:** Company name + GitHub URL + Industry

**Output:**
- ⚡ Live agent progress (WebSocket)
- 📊 Risk scores (Tech Debt, Compliance, Market Fit)
- 📈 3-year Bear/Base/Bull forecast
- 📄 Professional PDF report
- 🏷️ Recommendation: BUY / PROCEED WITH CONDITIONS / AVOID

---

## 👨‍💻 Built By

**Rudra** — Gen AI APAC Hackathon 2025

---

*VEDA — Venture Evaluation & Due Diligence Agent*
*Powered by Vertex AI · Gemini 2.5 Flash · Google Cloud*
