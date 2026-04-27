"""
VEDA — Venture Evaluation & Due Diligence Agent
Main FastAPI application with Google OAuth, WebSocket live progress,
per-user session management, and MCP proxy routes.
"""
import io
import logging
import sys
import uuid
from datetime import datetime
from typing import Optional

import httpx as _httpx
from authlib.integrations.starlette_client import OAuthError
from fastapi import (
    BackgroundTasks, Depends, FastAPI, HTTPException,
    Request, WebSocket, WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from agents.primary_agent import PrimaryAgent
from api.auth import (
    SESSION_COOKIE, create_session_token,
    decode_session_token, get_current_user,
    oauth, require_user,
)
from api.progress_manager import ProgressManager
from db.bigquery_client import BigQueryClient
from utils.config import MCP_SERVER_URL, OAUTH_REDIRECT_URI, SESSION_SECRET
from utils.pdf_generator import generate_pdf

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="VEDA — Venture Evaluation & Due Diligence Agent",
    description="Multi-agent AI system for M&A due diligence powered by Vertex AI",
    version="2.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="veda_starlette_session",
    max_age=60 * 60 * 8,
    https_only=False,
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
    company_name:             str
    github_repo_url:          str
    industry:                 str
    description:              Optional[str] = ""
    schedule_kickoff_meeting: Optional[bool] = False
    attendee_email:           Optional[str] = ""

class AuditResponse(BaseModel):
    job_id:        str
    status:        str
    message:       str
    created_at:    str
    websocket_url: str


# ── Auth routes ───────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    with open("static/login.html") as f:
        return f.read()


@app.get("/auth/login")
async def auth_login(request: Request):
    """Redirect user to Google OAuth consent screen."""
    return await oauth.google.authorize_redirect(
        request,
        OAUTH_REDIRECT_URI,
    )


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle Google OAuth callback — create session and redirect to dashboard."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        logger.error("OAuth callback error: %s", exc)
        return RedirectResponse(url="/login?error=oauth_failed")

    user_info = token.get("userinfo") or {}
    if not user_info:
        try:
            user_info = await oauth.google.userinfo(token=token)
        except Exception as exc:
            logger.error("Failed to fetch userinfo: %s", exc)
            return RedirectResponse(url="/login?error=userinfo_failed")

    user = {
        "email":      user_info.get("email", ""),
        "name":       user_info.get("name", ""),
        "picture":    user_info.get("picture", ""),
        "sub":        user_info.get("sub", ""),
        "access_token":  token.get("access_token", ""),
        "refresh_token": token.get("refresh_token", ""),
        "refresh_token": token.get("refresh_token", ""),
        "token_uri":     "https://oauth2.googleapis.com/token",
    }

    logger.info("User authenticated: %s", user["email"])

    session_token = create_session_token(user)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_token,
        httponly=True,
        max_age=60 * 60 * 8,
        samesite="lax",
    )
    return response


@app.get("/auth/logout")
async def logout():
    """Clear session and redirect to login."""
    response = RedirectResponse(url="/login")
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/auth/me")
async def me(request: Request):
    """Return current authenticated user info."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"email": user["email"], "name": user["name"], "picture": user["picture"]}


# ── Core routes ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    """Serve dashboard — redirect to login if not authenticated."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    with open("static/index.html") as f:
        return f.read()


@app.get("/health")
def health():
    return {
        "service": "VEDA — Venture Evaluation & Due Diligence Agent",
        "status":  "running",
        "version": "2.0.0",
    }


@app.post("/audit", response_model=AuditResponse)
async def start_audit(
    request_body: AuditRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_user),
):
    job_id     = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    audit_data = request_body.dict()
    audit_data["user_email"] = user["email"]

    bq.create_job(job_id, audit_data, created_at)

    background_tasks.add_task(
        agent.run_full_audit,
        job_id           = job_id,
        company_name     = request_body.company_name,
        github_repo_url  = request_body.github_repo_url,
        industry         = request_body.industry,
        description      = request_body.description,
        schedule_meeting = request_body.schedule_kickoff_meeting,
        attendee_email      = request_body.attendee_email or user["email"],
        user_access_token   = user.get("access_token", ""),
        refresh_token       = user.get("refresh_token", ""),
    )

    logger.info("Audit started: %s by %s", job_id, user["email"])

    return AuditResponse(
        job_id        = job_id,
        status        = "PENDING",
        message       = "VEDA audit started. Connect to WebSocket for live updates.",
        created_at    = created_at,
        websocket_url = f"/ws/{job_id}",
    )


@app.websocket("/ws/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    await progress.connect(job_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        progress.disconnect(job_id, websocket)


@app.get("/status/{job_id}")
def get_status(job_id: str, user: dict = Depends(require_user)):
    record = bq.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    return record


@app.get("/report/{job_id}")
def get_report(job_id: str, user: dict = Depends(require_user)):
    record = bq.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    if record["status"] != "COMPLETED":
        raise HTTPException(status_code=202, detail=f"Job status: {record['status']}")
    return bq.get_report(job_id)


@app.get("/report/{job_id}/pdf")
def get_pdf_report(job_id: str, user: dict = Depends(require_user)):
    report = bq.get_report(job_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    pdf_bytes = generate_pdf(report)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=VEDA-{job_id[:8]}.pdf"},
    )


@app.get("/report/{job_id}/trail")
def get_audit_trail(job_id: str, user: dict = Depends(require_user)):
    return {"events": bq.get_agent_events(job_id)}


@app.get("/jobs")
def list_jobs(limit: int = 10, user: dict = Depends(require_user)):
    return bq.list_jobs(limit=limit)


@app.get("/analytics/stats")
def get_stats(user: dict = Depends(require_user)):
    return bq.get_dashboard_stats()


@app.get("/analytics/industries")
def get_industry_breakdown(user: dict = Depends(require_user)):
    return bq.get_industry_breakdown()


@app.post("/compare")
async def compare_companies(
    background_tasks: BackgroundTasks,
    request: Request,
    company1_name: str = "",
    company1_url: str = "",
    company2_name: str = "",
    company2_url: str = "",
    industry: str = "saas",
    user: dict = Depends(require_user),
):
    job1_id    = str(uuid.uuid4())
    job2_id    = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    for job_id, name, url in [
        (job1_id, company1_name, company1_url),
        (job2_id, company2_name, company2_url),
    ]:
        bq.create_job(job_id, {
            "company_name":    name,
            "github_repo_url": url,
            "industry":        industry,
            "description":     "",
            "user_email":      user["email"],
        }, created_at)
        background_tasks.add_task(
            agent.run_full_audit,
            job_id=job_id, company_name=name,
            github_repo_url=url, industry=industry,
            description="", schedule_meeting=False, attendee_email="",
        )

    return {
        "job1_id": job1_id,
        "job2_id": job2_id,
        "status":  "RUNNING",
        "message": "Both audits started.",
    }


@app.get("/compare/result")
def compare_result(
    job1_id: str,
    job2_id: str,
    user: dict = Depends(require_user),
):
    report1 = bq.get_report(job1_id)
    report2 = bq.get_report(job2_id)
    job1    = bq.get_job(job1_id)
    job2    = bq.get_job(job2_id)

    if not report1 or not report2:
        return {
            "status":      "PENDING",
            "job1_status": job1.get("status") if job1 else "UNKNOWN",
            "job2_status": job2.get("status") if job2 else "UNKNOWN",
        }

    score1 = report1.get("overall_risk_score", 0) or 0
    score2 = report2.get("overall_risk_score", 0) or 0
    winner = (
        report1.get("company_name") if score1 >= score2
        else report2.get("company_name")
    )

    def _summary(r):
        return {
            "name":               r.get("company_name"),
            "overall_risk_score": r.get("overall_risk_score", 0),
            "tech_debt":          r.get("code_audit", {}).get("tech_debt_score"),
            "compliance":         r.get("regulatory", {}).get("compliance_score"),
            "market_fit":         r.get("market_forecast", {}).get("market_fit_score"),
            "recommendation":     r.get("executive_summary", {}).get("recommendation"),
        }

    return {
        "status":   "COMPLETED",
        "winner":   winner,
        "company1": _summary(report1),
        "company2": _summary(report2),
    }


# ── MCP proxy routes (browser → API → MCP server, avoids CORS) ───────────────

@app.get("/mcp/tasks/list")
async def proxy_tasks_list(request: Request, user: dict = Depends(require_user)):
    async with _httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{MCP_SERVER_URL}/tasks/list",
                params={
                    "user_access_token": user.get("access_token", ""),
                    "refresh_token":     user.get("refresh_token", ""),
                },
                timeout=10,
            )
            return JSONResponse(resp.json())
        except Exception as exc:
            return JSONResponse({"tasks": [], "error": str(exc)})


@app.post("/mcp/tasks/create")
async def proxy_tasks_create(request: Request, user: dict = Depends(require_user)):
    body = await request.json()
    # Inject user OAuth token so task goes to THEIR calendar
    body["user_access_token"] = user.get("access_token", "")
    body["refresh_token"]     = user.get("refresh_token", "")
    async with _httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{MCP_SERVER_URL}/tasks/create", json=body, timeout=15)
            return JSONResponse(resp.json())
        except Exception as exc:
            return JSONResponse({"created": False, "error": str(exc)})


@app.get("/mcp/calendar/upcoming")
async def proxy_calendar_upcoming(user: dict = Depends(require_user)):
    async with _httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{MCP_SERVER_URL}/calendar/upcoming",
                params={
                    "user_access_token": user.get("access_token", ""),
                    "refresh_token":     user.get("refresh_token", ""),
                },
                timeout=10,
            )
            return JSONResponse(resp.json())
        except Exception as exc:
            return JSONResponse({"meetings": [], "error": str(exc)})


@app.post("/mcp/calendar/schedule")
async def proxy_calendar_schedule(request: Request, user: dict = Depends(require_user)):
    body = await request.json()
    body["user_access_token"] = user.get("access_token", "")
    body["refresh_token"] = user.get("refresh_token", "")
    async with _httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{MCP_SERVER_URL}/calendar/schedule", json=body, timeout=15)
            return JSONResponse(resp.json())
        except Exception as exc:
            return JSONResponse({"scheduled": False, "error": str(exc)})

@app.get("/history")
def get_audit_history(limit: int = 20, user: dict = Depends(require_user)):
    """Get audit history with scores for the history dashboard."""
    try:
        query = f"""
            SELECT
                j.job_id,
                j.company_name,
                j.status,
                CAST(j.created_at AS STRING) as created_at,
                r.overall_risk_score,
                JSON_VALUE(r.report_json, '$.code_audit.tech_debt_score') as tech_debt_score,
                JSON_VALUE(r.report_json, '$.regulatory.compliance_score') as compliance_score,
                JSON_VALUE(r.report_json, '$.market_forecast.market_fit_score') as market_fit_score,
                JSON_VALUE(r.report_json, '$.executive_summary.recommendation') as recommendation,
                JSON_VALUE(r.report_json, '$.industry') as industry,
                JSON_VALUE(r.report_json, '$.company_name') as report_company_name
            FROM (
                SELECT job_id, MAX(updated_at) as latest
                FROM `{bq.client.project}.{bq.dataset}.audit_jobs`
                GROUP BY job_id
            ) latest_jobs
            JOIN `{bq.client.project}.{bq.dataset}.audit_jobs` j
                ON j.job_id = latest_jobs.job_id AND j.updated_at = latest_jobs.latest
            LEFT JOIN `{bq.client.project}.{bq.dataset}.audit_reports` r
                ON r.job_id = j.job_id
            WHERE j.status = 'COMPLETED'
            ORDER BY j.created_at DESC
            LIMIT {limit}
        """
        rows = list(bq.client.query(query).result())
        history = []
        for row in rows:
            history.append({
                "job_id":             row.job_id,
                "company_name": row.report_company_name or row.company_name or "Unknown",
                "status":             row.status,
                "created_at":         str(row.created_at)[:19],
                "overall_risk_score": float(row.overall_risk_score) if row.overall_risk_score else None,
                "tech_debt_score":    float(row.tech_debt_score) if row.tech_debt_score else None,
                "compliance_score":   float(row.compliance_score) if row.compliance_score else None,
                "market_fit_score":   float(row.market_fit_score) if row.market_fit_score else None,
                "recommendation":     row.recommendation or "—",
                "industry":           row.industry or "—",
            })
        return {"history": history, "total": len(history)}
    except Exception as e:
        return {"history": [], "total": 0, "error": str(e)}
