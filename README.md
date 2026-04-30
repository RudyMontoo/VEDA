# VEDA — Venture Evaluation & Due Diligence Agent

> **Google Cloud Gen AI Academy APAC Edition — Top 100 Shortlisted**
> 6-Agent AI System for M&A Due Diligence · 10 Google Cloud Services · Powered by Gemini 2.5 Flash

[![Live](https://img.shields.io/badge/Status-Live-brightgreen)](https://veda-api-790567978781.us-central1.run.app/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google)](https://cloud.google.com/vertex-ai)
[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-2%20Services-34A853?logo=google-cloud)](https://cloud.google.com/run)
[![BigQuery](https://img.shields.io/badge/BigQuery-5%20Tables-FBBC04?logo=google-cloud)](https://cloud.google.com/bigquery)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## Links

| | |
|---|---|
| **Production App** | https://veda-api-790567978781.us-central1.run.app |
| **MCP Server** | https://veda-mcp-790567978781.us-central1.run.app |
| **GitHub** | https://github.com/RudyMontoo/VEDA |
| **Demo Video** | https://drive.google.com/file/d/1-lnddI3YflZG5HpdHcVVI-lnChE-ke-r/view |

---

## The Problem

M&A due diligence takes **6–12 weeks** and costs lakhs in consulting fees. Analysts miss critical risks — hidden technical debt, regulatory violations, and compliance gaps that surface only after the deal closes.

**VEDA solves this. Enter a company name and GitHub URL. Get a complete boardroom-ready due diligence report in under 5 minutes.**

> *Audit. Analyse. Acquire.*

---

## 6 Specialised AI Agents

| # | Agent | Role | Technology |
|---|---|---|---|
| 0 | **Primary Agent** | Orchestrates the full async pipeline | Gemini 2.5 Flash + asyncio |
| 1 | **Code Auditor** | 25+ real GitHub signals, deterministic scoring | MCP → GitHub API |
| 2 | **Regulatory Scout** | 40+ Indian regulations, RAG-grounded with real law | Gemini + Vertex AI Search |
| 3 | **Market Analyst** | Bear / Base / Bull 3-year INR simulation | Gemini + INR benchmarks |
| 4 | **Executive Summary** | Weighted scoring matrix → deterministic verdict | Gemini (narrative only) |
| 5 | **Competitor Intelligence** | Discovers 3 real competitors, GitHub-scored | Gemini + GitHub API |
| 6 | **News Sentiment** | Market perception from recent developments | Google Natural Language API |

---

## 10 Google Cloud Services

| # | Service | Usage in VEDA |
|---|---|---|
| 1 | **Vertex AI + Gemini 2.5 Flash** | Powers all 6 agents — reasoning, analysis, narrative |
| 2 | **BigQuery** | 5 structured tables — full audit history and analytics |
| 3 | **Cloud Run — Main API** | Serverless FastAPI deployment, auto-scaling |
| 4 | **Cloud Run — MCP Server** | GitHub, Calendar, Tasks tools live for every user |
| 5 | **Secret Manager** | Secure storage for all API keys and OAuth secrets |
| 6 | **Vertex AI Search (Discovery Engine)** | RAG over 5 indexed Indian legal documents |
| 7 | **Google Calendar API + OAuth 2.0** | Per-user task creation — each user's own calendar |
| 8 | **Cloud Logging** | Structured agent logs visible in GCP Console |
| 9 | **Natural Language API** | Real sentiment scoring with score + magnitude |
| 10 | **Vertex AI Embeddings** | Startup similarity search using cosine similarity |

---

## Architecture

```
Browser (Google OAuth 2.0 Login)
              │
              ▼
┌─────────────────────────────────────────────────┐
│       FastAPI — Google Cloud Run (Main API)      │
│    WebSocket · REST API · MCP Proxy · OAuth      │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │    Primary Agent     │  Orchestrator
            │   (Gemini 2.5 Flash) │
            └──┬───┬───┬───┬───┬──┘
               │   │   │   │   │   │
              [1] [2] [3] [4] [5] [6]
             Code Reg Mkt Exec Comp News
              │              │
              ▼              ▼
      MCP Server          Gemini 2.5 Flash
   (Cloud Run)            Vertex AI Search (RAG)
  GitHub · Calendar
      Tasks
              │
              ▼
   ┌──────────────────┐    ┌─────────────────────┐
   │    BigQuery       │    │    Cloud Logging     │
   │   5 tables        │    │  Structured logs     │
   └──────────────────┘    └─────────────────────┘
              │
              ▼
   ┌──────────────────────────────────────────┐
   │         Deal Intelligence Layer           │
   │  NL API Sentiment  ·  Investment Score   │
   │  Vertex Embeddings  ·  Document AI PDF   │
   └──────────────────────────────────────────┘
```

---

## Scoring Intelligence

VEDA does not guess. Every verdict is deterministic.

### Code Auditor — 25+ Real GitHub Signals
```
Final Score = (Gemini Score × 0.6) + (Rule-Based Score × 0.4)
```
Signals: days since last commit · commits in 30/90 days · CI/CD pipeline count · test directory presence · security policy · open issues age · PR merge time · contributor count · README quality · release cadence · dependency management.

### Executive Summary — Weighted Scoring Matrix
```
Composite Score = Tech Debt (35%) + Compliance (35%) + Market Fit (30%)
```
Hard penalties applied for deal-blockers (archived repo → tech capped at 15, compliance violations → compliance capped at 20).

**Verdict bands:** 85+ STRONG BUY · 70+ BUY · 55+ HOLD · 40+ CAUTIOUS · 0+ AVOID

### Deal Intelligence — Investment Score
```
Investment Score = Tech(25%) + Compliance(20%) + Market(20%) + Sentiment(15%) + Financial(10%) + Keywords(10%)
```
**Grade:** A+ / A / B / C / D / F · **Recommendation:** INVEST / WATCH / AVOID

### Regulatory Scout — RAG-Grounded Compliance

| Industry | Indian Laws Checked |
|---|---|
| **Fintech** | RBI Cloud Outsourcing · PMLA · PSS Act · SEBI Guidelines |
| **Healthtech** | DISHA · CDSCO Medical Device Rules · Telemedicine Guidelines 2020 |
| **Edtech** | NEP 2020 · PDPB 2023 (children's data) · UDISE |
| **SaaS** | IT Act Section 43A · PDPB 2023 · GST Act · RBI Cloud |
| **E-Commerce** | Consumer Protection Rules 2020 · FDI Policy |
| **Deeptech** | Patents Act 1970 · SCOMET Export Controls |

---

## Deal Intelligence Layer

After every audit, VEDA automatically runs a 4-part intelligence analysis:

**1. Natural Language API Sentiment** — Real sentiment score (-1 to +1) with magnitude on the executive summary, not a simple prompt.

**2. Auto Investment Score (0–100)** — 6-component weighted score combining technical health, compliance, market fit, NL API sentiment, financial signals, and keyword heuristics.

**3. Similar Startups** — Vertex AI Embeddings (text-embedding-004) generate vector representations of each audit. Cosine similarity finds the top-3 most similar past deals — no external vector database needed.

**4. Pitch Deck Parser** — Upload a PDF pitch deck. Document AI + pypdf extract company name, industry, problem, solution, revenue, growth rate, team size, and funding stage — auto-filling the audit form.

---

## MCP Integrations (Real, Not Mocked)

| Tool | What It Does |
|---|---|
| **GitHub API** | 25+ real signals per repo scan |
| **Google Calendar** | Creates kickoff meeting in logged-in user's calendar |
| **Google Tasks** | Auto-creates 6-item M&A due diligence checklist per audit |
| **Custom Tasks** | Add tasks from dashboard → directly to user's Google Calendar |

Every calendar event and task goes to the **logged-in user's own Google Calendar** via OAuth 2.0. Multi-user ready — each user sees only their own data.

---

## Project Structure

```
VEDA/
├── agents/
│   ├── primary_agent.py            # Orchestrator — async pipeline, per-agent timeouts
│   ├── code_auditor.py             # 25+ GitHub signals, deterministic scoring
│   ├── regulatory_scout.py         # RAG-grounded Indian compliance (6 frameworks)
│   ├── market_analyst.py           # Bear/Base/Bull 3-year INR simulation
│   ├── executive_summary.py        # Weighted matrix + board-ready report
│   ├── competitor_intelligence.py  # GitHub-scored competitor discovery
│   └── news_sentiment.py           # Market perception analysis
│
├── api/
│   ├── main.py                     # FastAPI — REST + WebSocket + MCP proxy + 15 endpoints
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
│   ├── vertex_helper.py            # Gemini 2.5 Flash wrapper — retry, logging, timeout
│   ├── vertex_search.py            # Vertex AI Search RAG (Discovery Engine)
│   ├── cloud_logger.py             # Google Cloud Logging — structured agent logs
│   ├── sentiment_engine.py         # Natural Language API sentiment scoring
│   ├── embeddings_engine.py        # Vertex AI Embeddings + cosine similarity
│   ├── investment_scorer.py        # Auto Investment Score 0–100 with grade
│   ├── pitch_deck_parser.py        # Document AI + pypdf PDF extraction
│   ├── pdf_generator.py            # ReportLab PDF report generator
│   └── config.py                   # Secret Manager integration
│
├── regulatory_docs/                # 5 Indian legal documents (RAG-indexed)
│   ├── pdpb_2023.txt
│   ├── it_act_43a.txt
│   ├── rbi_cloud_guidelines.txt
│   ├── gst_compliance.txt
│   └── sebi_guidelines.txt
│
├── static/
│   └── index.html                  # Dashboard — Audit · Compare · Tasks · History
│
├── Dockerfile                      # Main API — Cloud Run
├── Dockerfile.mcp                  # MCP Server — Cloud Run
└── requirements.txt
```

---

## BigQuery Schema

| Table | Purpose | Key Fields |
|---|---|---|
| `audit_jobs` | Job lifecycle tracking | job_id · status · company_name · user_email · timestamps |
| `audit_reports` | Full report JSON | job_id · overall_risk_score · report_json · recommendation |
| `risk_scores` | Per-agent analytics | tech_debt · compliance · market_fit · overall |
| `agent_events` | WebSocket audit trail | step · agent_name · status · progress_pct · event_data |
| `error_logs` | Debugging | job_id · agent_name · error_type · traceback |

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/audit` | Start a due diligence audit |
| `WS` | `/ws/{job_id}` | Live agent progress via WebSocket |
| `GET` | `/status/{job_id}` | Poll audit status |
| `GET` | `/report/{job_id}` | Full JSON report |
| `GET` | `/report/{job_id}/pdf` | Download PDF report |
| `POST` | `/compare` | Compare 2 companies side-by-side |
| `GET` | `/history` | Audit history from BigQuery |
| `GET` | `/health` | Health check |
| `GET` | `/auth/me` | Current logged-in user |
| `POST` | `/pitch-deck/parse` | Upload PDF → extract startup data |
| `POST` | `/sentiment/analyze` | Natural Language API sentiment |
| `POST` | `/embeddings/similar` | Find similar past audits |
| `POST` | `/intelligence/score` | Compute Investment Score |
| `GET` | `/intelligence/report/{job_id}` | Full Deal Intelligence report |
| `POST` | `/mcp/tasks/create` | Create task in user's Google Calendar |

---

## Quick Start

### Prerequisites
- Google Cloud Project with Vertex AI + BigQuery enabled
- GitHub Personal Access Token (`public_repo` scope)
- Google OAuth 2.0 client credentials

### Run Locally

```bash
git clone https://github.com/RudyMontoo/VEDA.git
cd VEDA
cp .env.example .env
# Fill in: GCP_PROJECT_ID, GITHUB_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

gcloud auth application-default login
python db/setup_schema.py

# Terminal 1 — MCP Server
uvicorn mcp_server.server:app --port 8001

# Terminal 2 — Main API
export $(cat .env | grep -v '^#' | xargs)
uvicorn api.main:app --port 8080 --reload
```

### Deploy to Cloud Run

```bash
# Main API
gcloud run deploy veda-api \
  --source . --region us-central1 --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=veda-491808,BQ_DATASET=veda_ma_diligence \
  --memory 2Gi --timeout 300

# MCP Server
cp Dockerfile Dockerfile.main.bak && cp Dockerfile.mcp Dockerfile
gcloud run deploy veda-mcp \
  --source . --region us-central1 --allow-unauthenticated \
  --memory 512Mi --timeout 120 --port 8001
cp Dockerfile.main.bak Dockerfile
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GCP_PROJECT_ID` | ✅ | Google Cloud project ID |
| `GCP_LOCATION` | ✅ | Region — `us-central1` |
| `BQ_DATASET` | ✅ | BigQuery dataset name |
| `VERTEX_AI_MODEL` | ✅ | `gemini-2.5-flash` |
| `MCP_SERVER_URL` | ✅ | MCP server URL |
| `GITHUB_TOKEN` | ✅ | GitHub PAT (`public_repo` scope) |
| `GOOGLE_CLIENT_ID` | ✅ | OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | OAuth 2.0 client secret |
| `OAUTH_REDIRECT_URI` | ✅ | OAuth callback URL |
| `SESSION_SECRET` | ✅ | Random secret for session signing |

All secrets stored in **Google Cloud Secret Manager** — not in environment variables on Cloud Run.

---

## What Makes VEDA Different

| Aspect | Typical AI Tools | VEDA |
|---|---|---|
| Scoring | LLM guesses a number | Deterministic formula from 25+ real GitHub signals |
| Compliance | Generic checklist | 6 Indian frameworks, RAG-grounded with real legal docs |
| Competitors | Not included | Agent 5 discovers + GitHub-scores 3 real competitors |
| Calendar | Mocked or shared | Real OAuth — each user's own Google Calendar |
| Sentiment | Simple LLM prompt | Google Natural Language API with score + magnitude |
| Investment Score | Not included | 6-component weighted score, A+/A/B/C/D/F grade |
| Similar Deals | Not included | Vertex AI Embeddings + cosine similarity, no vector DB |
| Pitch Deck | Manual form entry | Document AI + pypdf → auto-fills all form fields |
| Real-time | Polling | WebSocket live streaming of agent pipeline |
| Logs | print() statements | Google Cloud Logging — structured JSON in GCP Console |

---

## Sample Output

```json
{
  "company_name": "Razorpay",
  "overall_risk_score": 83.0,
  "executive_summary": {
    "recommendation": "PROCEED WITH CONDITIONS",
    "composite_score": 83.0,
    "one_line_verdict": "Strong technical foundation with RBI compliance gaps — viable at ₹18–32Cr."
  },
  "code_audit": {
    "tech_debt_score": 88,
    "maintenance_health": "ACTIVE",
    "bus_factor_risk": "LOW"
  },
  "regulatory": {
    "compliance_score": 72,
    "rag_grounded": true,
    "estimated_remediation_time": "2-3 months"
  },
  "market_forecast": {
    "market_fit_score": 82,
    "scenarios": {
      "bear": { "year3_arr_inr_lakhs": 480, "probability": "20%" },
      "base": { "year3_arr_inr_lakhs": 920, "probability": "55%" },
      "bull": { "year3_arr_inr_lakhs": 1600, "probability": "25%" }
    }
  },
  "competitor_intelligence": {
    "competitive_position": "MARKET LEADER",
    "threat_level": "LOW",
    "competitors_found": 3
  },
  "news_sentiment": {
    "market_perception_score": 88,
    "overall_sentiment": "VERY POSITIVE",
    "funding_status": "Series F funded"
  },
  "deal_intelligence": {
    "investment_score": 81,
    "grade": "A",
    "recommendation": "INVEST"
  }
}
```

---

## Credits Used

- **$1,000 GenAI App Builder credit** — Vertex AI Search (Discovery Engine)
- **Vertex AI Gemini 2.5 Flash** — per-call token cost (minimal at hackathon scale)
- **Natural Language API** — per-call cost for sentiment scoring
- **Vertex AI Embeddings** — per-call cost for similarity search
- BigQuery, Cloud Run, Cloud Logging, Secret Manager — within free tier

---

## Built By

**Rudra Sharma** — First Year B.Tech Computer Science
Google Cloud Gen AI Academy APAC Edition 2025 · Top 100

---

*VEDA — Venture Evaluation & Due Diligence Agent*
*Powered by Vertex AI · Gemini 2.5 Flash · 10 Google Cloud Services*

*Audit. Analyse. Acquire.*
