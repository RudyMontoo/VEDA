"""
VEDA — Venture Evaluation & Due Diligence Agent
Main FastAPI application with WebSocket live progress.
"""

import uuid
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import StreamingResponse 
from utils.pdf_generator import generate_pdf
import io
from agents.primary_agent import PrimaryAgent
from db.bigquery_client import BigQueryClient
from api.progress_manager import ProgressManager

app = FastAPI(
    title="VEDA — Venture Evaluation & Due Diligence Agent",
    description="Multi-agent AI system for M&A due diligence powered by Vertex AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

bq       = BigQueryClient()
progress = ProgressManager()
agent    = PrimaryAgent(progress_manager=progress)


# ── Schemas ───────────────────────────────────────────────────────────────────

class AuditRequest(BaseModel):
    company_name:              str
    github_repo_url:           str
    industry:                  str
    description:               Optional[str] = ""
    schedule_kickoff_meeting:  Optional[bool] = False
    attendee_email:            Optional[str] = ""

class AuditResponse(BaseModel):
    job_id:        str
    status:        str
    message:       str
    created_at:    str
    websocket_url: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the VEDA web dashboard."""
    with open("static/index.html") as f:
        return f.read()


@app.get("/health")
def health():
    return {
        "service": "VEDA — Venture Evaluation & Due Diligence Agent",
        "status":  "running",
        "version": "1.0.0",
    }


@app.post("/audit", response_model=AuditResponse)
async def start_audit(request: AuditRequest, background_tasks: BackgroundTasks):
    """
    Start a VEDA due diligence audit.
    Connect to /ws/{job_id} for live progress updates.
    """
    job_id     = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    bq.create_job(job_id, request.dict(), created_at)

    background_tasks.add_task(
        agent.run_full_audit,
        job_id           = job_id,
        company_name     = request.company_name,
        github_repo_url  = request.github_repo_url,
        industry         = request.industry,
        description      = request.description,
        schedule_meeting = request.schedule_kickoff_meeting,
        attendee_email   = request.attendee_email,
    )

    return AuditResponse(
        job_id        = job_id,
        status        = "PENDING",
        message       = "VEDA audit started. Connect to WebSocket for live updates.",
        created_at    = created_at,
        websocket_url = f"/ws/{job_id}",
    )


@app.websocket("/ws/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint — receives live agent progress events.

    Event format:
    {
      "job_id": "...",
      "step": 1,
      "total_steps": 4,
      "agent": "Code Auditor",
      "status": "RUNNING" | "DONE" | "FAILED" | "COMPLETED",
      "message": "Scanning GitHub repository...",
      "data": { ...agent results... },
      "progress_pct": 25,
      "timestamp": "..."
    }
    """
    await progress.connect(job_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        progress.disconnect(job_id, websocket)


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Poll the current status of an audit job."""
    record = bq.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    return record


@app.get("/report/{job_id}")
def get_report(job_id: str):
    """Get the full due diligence report (only available when COMPLETED)."""
    record = bq.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    if record["status"] != "COMPLETED":
        raise HTTPException(status_code=202, detail=f"Job status: {record['status']}")
    return bq.get_report(job_id)




@app.get("/report/{job_id}/trail")
def get_audit_trail(job_id: str):
    """Get the full agent event trail for an audit."""
    return {"events": bq.get_agent_events(job_id)}


@app.get("/jobs")
def list_jobs(limit: int = 10):
    """List recent audit jobs."""
    return bq.list_jobs(limit=limit)


@app.get("/analytics/stats")
def get_stats():
    """Dashboard stats — total audits, completion rate, avg duration."""
    return bq.get_dashboard_stats()


@app.get("/analytics/industries")
def get_industry_breakdown():
    """Industry breakdown for analytics dashboard."""
    return bq.get_industry_breakdown()

@app.post("/compare")
async def compare_companies(background_tasks: BackgroundTasks,
    company1_name: str = "",
    company1_url: str = "",
    company2_name: str = "",
    company2_url: str = "",
    industry: str = "saas"):
    
    job1_id = str(uuid.uuid4())
    job2_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    bq.create_job(job1_id, {
        "company_name": company1_name,
        "github_repo_url": company1_url,
        "industry": industry,
        "description": ""
    }, created_at)

    bq.create_job(job2_id, {
        "company_name": company2_name,
        "github_repo_url": company2_url,
        "industry": industry,
        "description": ""
    }, created_at)

    background_tasks.add_task(
        agent.run_full_audit,
        job_id=job1_id,
        company_name=company1_name,
        github_repo_url=company1_url,
        industry=industry,
        description="",
        schedule_meeting=False,
        attendee_email=""
    )

    background_tasks.add_task(
        agent.run_full_audit,
        job_id=job2_id,
        company_name=company2_name,
        github_repo_url=company2_url,
        industry=industry,
        description="",
        schedule_meeting=False,
        attendee_email=""
    )

    return {
        "job1_id": job1_id,
        "job2_id": job2_id,
        "status": "RUNNING",
        "message": "Both audits started. Poll /compare/result for results."
    }


@app.get("/compare/result")
def compare_result(job1_id: str, job2_id: str):
    report1 = bq.get_report(job1_id)
    report2 = bq.get_report(job2_id)
    job1 = bq.get_job(job1_id)
    job2 = bq.get_job(job2_id)

    if not report1 or not report2:
        return {
            "status": "PENDING",
            "job1_status": job1.get("status") if job1 else "UNKNOWN",
            "job2_status": job2.get("status") if job2 else "UNKNOWN",
        }

    score1 = report1.get("overall_risk_score", 0) or 0
    score2 = report2.get("overall_risk_score", 0) or 0
    winner = report1.get("company_name") if score1 >= score2 else report2.get("company_name")

    return {
        "status": "COMPLETED",
        "winner": winner,
        "company1": {
            "name": report1.get("company_name"),
            "overall_risk_score": score1,
            "tech_debt": report1.get("code_audit", {}).get("tech_debt_score"),
            "compliance": report1.get("regulatory", {}).get("compliance_score"),
            "market_fit": report1.get("market_forecast", {}).get("market_fit_score"),
            "recommendation": report1.get("executive_summary", {}).get("recommendation"),
        },
        "company2": {
            "name": report2.get("company_name"),
            "overall_risk_score": score2,
            "tech_debt": report2.get("code_audit", {}).get("tech_debt_score"),
            "compliance": report2.get("regulatory", {}).get("compliance_score"),
            "market_fit": report2.get("market_forecast", {}).get("market_fit_score"),
            "recommendation": report2.get("executive_summary", {}).get("recommendation"),
        }
    }
@app.get("/report/{job_id}/pdf")
def get_pdf_report(job_id: str):
    bq = BigQueryClient()
    report = bq.get_report(job_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    pdf_bytes = generate_pdf(report)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=VEDA-{job_id[:8]}.pdf"}
    )

# ── ADD THESE ROUTES TO api/main.py ──────────────────────────────────────────
# They proxy /mcp/* calls from the browser to the MCP server
# This fixes the CORS issue where browser can't call localhost:8001 directly
#
# Paste these routes BEFORE the last route in api/main.py
# ─────────────────────────────────────────────────────────────────────────────

import httpx as _httpx
from fastapi import Request as _Request
from fastapi.responses import JSONResponse as _JSONResponse

MCP_BASE = "http://localhost:8001"

@app.get("/mcp/tasks/list")
async def proxy_tasks_list():
    """Proxy: browser → VEDA API → MCP server (avoids CORS)"""
    try:
        async with _httpx.AsyncClient() as client:
            resp = await client.get(f"{MCP_BASE}/tasks/list", timeout=10)
            return _JSONResponse(resp.json())
    except Exception as e:
        return _JSONResponse({"tasks": [], "error": str(e)})

@app.post("/mcp/tasks/create")
async def proxy_tasks_create(request: _Request):
    """Proxy: browser → VEDA API → MCP server"""
    try:
        body = await request.json()
        async with _httpx.AsyncClient() as client:
            resp = await client.post(f"{MCP_BASE}/tasks/create", json=body, timeout=15)
            return _JSONResponse(resp.json())
    except Exception as e:
        return _JSONResponse({"created": False, "error": str(e)})

@app.get("/mcp/calendar/upcoming")
async def proxy_calendar_upcoming():
    """Proxy: browser → VEDA API → MCP server"""
    try:
        async with _httpx.AsyncClient() as client:
            resp = await client.get(f"{MCP_BASE}/calendar/upcoming", timeout=10)
            return _JSONResponse(resp.json())
    except Exception as e:
        return _JSONResponse({"meetings": [], "error": str(e)})

@app.post("/mcp/calendar/schedule")
async def proxy_calendar_schedule(request: _Request):
    """Proxy: browser → VEDA API → MCP server"""
    try:
        body = await request.json()
        async with _httpx.AsyncClient() as client:
            resp = await client.post(f"{MCP_BASE}/calendar/schedule", json=body, timeout=15)
            return _JSONResponse(resp.json())
    except Exception as e:
        return _JSONResponse({"scheduled": False, "error": str(e)})