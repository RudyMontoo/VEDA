"""
VEDA — MCP Server v3
Real integrations:
- GitHub API (enhanced 25+ signals)
- Google Calendar API (real events via Service Account)
- Google Tasks API (real tasks via Service Account)
"""

import os
import httpx
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="VEDA MCP Server", version="3.0.0")

GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN", "")
CALENDAR_ID    = os.getenv("GOOGLE_CALENDAR_ID", "primary")
TASKS_LIST_ID  = os.getenv("GOOGLE_TASKS_LIST_ID", "@default")
SERVICE_ACCOUNT_FILE = "service_account.json"


# ── Schemas ───────────────────────────────────────────────────────────────────

class RepoRequest(BaseModel):
    repo_url: str

class CalendarRequest(BaseModel):
    summary:        str
    start_datetime: str
    end_datetime:   str
    attendee_email: Optional[str] = ""
    description:    Optional[str] = ""

class TaskRequest(BaseModel):
    title:       str
    description: Optional[str] = ""
    due_date:    Optional[str] = ""  # Format: YYYY-MM-DD

class TaskUpdateRequest(BaseModel):
    task_id: str
    status:  str  # "completed" or "needsAction"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _github_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

def _days_since(date_str: str) -> int:
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return 999

def _repo_path(url: str) -> str:
    url = url.rstrip("/")
    if "github.com/" in url:
        return url.split("github.com/")[-1]
    return url

def _get_google_service(api: str, version: str):
    """Build a Google API service using service account credentials."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/tasks",
    ]
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    return build(api, version, credentials=creds)


# ── Tool 1: GitHub Repository Scanner ────────────────────────────────────────

@app.post("/github/repo")
async def scan_repo(request: RepoRequest):
    """Fetch 25+ real GitHub signals for accurate due diligence scoring."""
    repo_path = _repo_path(request.repo_url)
    headers   = _github_headers()

    async with httpx.AsyncClient(follow_redirects=True) as client:
        repo_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}",
            headers=headers, timeout=15
        )
        if repo_resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Repository not found")
        if repo_resp.status_code != 200:
            raise HTTPException(status_code=repo_resp.status_code, detail="GitHub API error")
        repo = repo_resp.json()

        lang_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/languages",
            headers=headers, timeout=10
        )
        languages = lang_resp.json() if lang_resp.status_code == 200 else {}

        commits_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/commits?per_page=30",
            headers=headers, timeout=15
        )
        commits = commits_resp.json() if commits_resp.status_code == 200 else []
        commit_dates = []
        for c in commits:
            try:
                commit_dates.append(_days_since(c["commit"]["author"]["date"]))
            except Exception:
                pass

        commits_last_30_days = sum(1 for d in commit_dates if d <= 30)
        commits_last_90_days = sum(1 for d in commit_dates if d <= 90)

        issues_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/issues?state=open&per_page=20",
            headers=headers, timeout=10
        )
        open_issues_data = issues_resp.json() if issues_resp.status_code == 200 else []
        real_issues = [i for i in open_issues_data if "pull_request" not in i]
        old_issues  = sum(1 for i in real_issues if _days_since(i.get("created_at","")) > 90)

        cicd_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/contents/.github/workflows",
            headers=headers, timeout=10
        )
        has_cicd   = cicd_resp.status_code == 200
        cicd_files = len(cicd_resp.json()) if has_cicd and isinstance(cicd_resp.json(), list) else 0

        has_tests = False
        for d in ["tests", "test", "__tests__", "spec"]:
            t = await client.get(
                f"https://api.github.com/repos/{repo_path}/contents/{d}",
                headers=headers, timeout=5
            )
            if t.status_code == 200:
                has_tests = True
                break

        security_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/contents/SECURITY.md",
            headers=headers, timeout=5
        )
        has_security_policy = security_resp.status_code == 200

        contrib_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/contributors?per_page=1&anon=true",
            headers=headers, timeout=10
        )
        contributors = int(contrib_resp.headers.get("x-total-count", 0)) if contrib_resp.status_code == 200 else 0

        pr_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/pulls?state=open&per_page=1",
            headers=headers, timeout=10
        )
        open_prs = int(pr_resp.headers.get("x-total-count", 0)) if pr_resp.status_code == 200 else 0

        release_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/releases?per_page=3",
            headers=headers, timeout=10
        )
        releases = release_resp.json() if release_resp.status_code == 200 else []
        latest_release         = releases[0].get("tag_name", "none") if releases else "none"
        days_since_last_release = _days_since(releases[0]["published_at"]) if releases else 999

        readme_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/readme",
            headers=headers, timeout=5
        )
        readme_size = readme_resp.json().get("size", 0) if readme_resp.status_code == 200 else 0

        dep_files = []
        for dep in ["requirements.txt", "package.json", "go.mod", "Cargo.toml", "pom.xml"]:
            d = await client.get(
                f"https://api.github.com/repos/{repo_path}/contents/{dep}",
                headers=headers, timeout=5
            )
            if d.status_code == 200:
                dep_files.append(dep)

    total_bytes = sum(languages.values()) or 1
    lang_pct    = {l: round(b / total_bytes * 100, 1) for l, b in languages.items()}
    days_since_push = _days_since(repo.get("pushed_at", ""))

    return {
        "repo_url":                request.repo_url,
        "name":                    repo.get("name"),
        "description":             repo.get("description"),
        "stars":                   repo.get("stargazers_count", 0),
        "forks":                   repo.get("forks_count", 0),
        "watchers":                repo.get("watchers_count", 0),
        "languages":               lang_pct,
        "size_kb":                 repo.get("size", 0),
        "days_since_push":         days_since_push,
        "commits_last_30_days":    commits_last_30_days,
        "commits_last_90_days":    commits_last_90_days,
        "open_issues":             repo.get("open_issues_count", 0),
        "old_issues_90d":          old_issues,
        "open_prs":                open_prs,
        "has_tests":               has_tests,
        "has_cicd":                has_cicd,
        "cicd_workflow_count":     cicd_files,
        "has_security_policy":     has_security_policy,
        "dependency_files":        dep_files,
        "readme_size_bytes":       readme_size,
        "contributors_count":      contributors,
        "latest_release":          latest_release,
        "days_since_last_release": days_since_last_release,
        "license":                 repo.get("license", {}).get("name") if repo.get("license") else "None",
        "default_branch":          repo.get("default_branch", "main"),
        "is_archived":             repo.get("archived", False),
        "is_fork":                 repo.get("fork", False),
        "created_at":              repo.get("created_at", ""),
    }


# ── Tool 2: Google Calendar (REAL) ───────────────────────────────────────────

@app.post("/calendar/schedule")
async def schedule_meeting(request: CalendarRequest):
    """Schedule a real due diligence kickoff meeting on Google Calendar."""
    try:
        service = _get_google_service("calendar", "v3")
        event = {
            "summary":     request.summary,
            "description": request.description or "Scheduled by VEDA — Venture Evaluation & Due Diligence Agent",
            "start": {"dateTime": request.start_datetime, "timeZone": "Asia/Kolkata"},
            "end":   {"dateTime": request.end_datetime,   "timeZone": "Asia/Kolkata"},
        }
        created = service.events().insert(
            calendarId=CALENDAR_ID, body=event
        ).execute()

        return {
            "event_id":  created["id"],
            "summary":   created["summary"],
            "start":     created["start"]["dateTime"],
            "end":       created["end"]["dateTime"],
            "html_link": created.get("htmlLink", ""),
            "meet_link": created.get("hangoutLink", ""),
            "scheduled": True,
        }
    except Exception as e:
        print(f"[Calendar] Error: {e}")
        return {
            "event_id":  f"evt_fallback_{abs(hash(request.summary)) % 9999:04d}",
            "summary":   request.summary,
            "scheduled": False,
            "error":     str(e),
        }


@app.get("/calendar/upcoming")
async def get_upcoming_meetings(max_results: int = 5):
    """Fetch upcoming VEDA due diligence meetings from Google Calendar."""
    try:
        service = _get_google_service("calendar", "v3")
        now     = datetime.utcnow().isoformat() + "Z"
        result  = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
            q="VEDA",
        ).execute()
        events = result.get("items", [])
        return {
            "meetings": [
                {
                    "event_id": e.get("id"),
                    "summary":  e.get("summary"),
                    "start":    e.get("start", {}).get("dateTime"),
                    "html_link":e.get("htmlLink", ""),
                }
                for e in events
            ]
        }
    except Exception as e:
        return {"meetings": [], "error": str(e)}


# ── Tool 3: Google Tasks (REAL) ───────────────────────────────────────────────

@app.post("/tasks/create")
async def create_task(request: TaskRequest):
    """Create a real due diligence checklist task in Google Tasks."""
    try:
        service = _get_google_service("tasks", "v1")

        task_body = {
            "title": request.title,
            "notes": request.description or "",
            "status": "needsAction",
        }
        if request.due_date:
            task_body["due"] = f"{request.due_date}T00:00:00.000Z"

        result = service.tasks().insert(
            tasklist=TASKS_LIST_ID,
            body=task_body,
        ).execute()

        return {
            "task_id": result.get("id"),
            "title":   result.get("title"),
            "status":  result.get("status"),
            "due":     result.get("due", ""),
            "created": True,
        }
    except Exception as e:
        print(f"[Tasks] Error: {e}")
        return {
            "task_id": f"task_{abs(hash(request.title)) % 99999:05d}",
            "title":   request.title,
            "status":  "needsAction",
            "created": False,
            "error":   str(e),
        }


@app.get("/tasks/list")
async def list_tasks(max_results: int = 20):
    """List all due diligence tasks from Google Tasks."""
    try:
        service = _get_google_service("tasks", "v1")
        result  = service.tasks().list(
            tasklist=TASKS_LIST_ID,
            showCompleted=False,
            maxResults=max_results,
        ).execute()
        tasks = result.get("items", [])
        return {
            "tasks": [
                {
                    "task_id": t.get("id"),
                    "title":   t.get("title"),
                    "status":  t.get("status"),
                    "notes":   t.get("notes", ""),
                    "due":     t.get("due", ""),
                }
                for t in tasks
            ],
            "total": len(tasks),
        }
    except Exception as e:
        return {"tasks": [], "error": str(e)}


@app.post("/tasks/complete")
async def complete_task(request: TaskUpdateRequest):
    """Mark a due diligence task as completed."""
    try:
        service = _get_google_service("tasks", "v1")
        task = service.tasks().get(
            tasklist=TASKS_LIST_ID,
            task=request.task_id
        ).execute()

        task["status"] = request.status
        result = service.tasks().update(
            tasklist=TASKS_LIST_ID,
            task=request.task_id,
            body=task,
        ).execute()

        return {
            "task_id": result.get("id"),
            "title":   result.get("title"),
            "status":  result.get("status"),
            "updated": True,
        }
    except Exception as e:
        return {"updated": False, "error": str(e)}


@app.post("/tasks/create_checklist")
async def create_due_diligence_checklist(company_name: str, industry: str = "saas"):
    """
    Auto-create a full due diligence checklist in Google Tasks
    when a new audit starts. This is called by the Primary Agent.
    """
    from datetime import timedelta
    base_date = datetime.utcnow()

    checklist = [
        {"title": f"[VEDA] Review technical audit — {company_name}",
         "notes": "Review code quality, security flags, and tech debt findings",
         "days": 1},
        {"title": f"[VEDA] Verify regulatory compliance — {company_name}",
         "notes": f"Check {industry} sector compliance documents",
         "days": 2},
        {"title": f"[VEDA] Validate 3-year financial forecast — {company_name}",
         "notes": "Review Bear/Base/Bull scenarios and acquisition price range",
         "days": 3},
        {"title": f"[VEDA] Request due diligence documents — {company_name}",
         "notes": "Request MCA filings, GST records, IP assignments, employee agreements",
         "days": 3},
        {"title": f"[VEDA] Legal review of deal conditions — {company_name}",
         "notes": "Review conditions for deal closure from executive summary",
         "days": 5},
        {"title": f"[VEDA] Final acquisition decision — {company_name}",
         "notes": "Board presentation and final go/no-go decision",
         "days": 7},
    ]

    created_tasks = []
    try:
        service = _get_google_service("tasks", "v1")
        for item in checklist:
            due_date = (base_date + timedelta(days=item["days"])).strftime("%Y-%m-%d")
            task_body = {
                "title":  item["title"],
                "notes":  item["notes"],
                "status": "needsAction",
                "due":    f"{due_date}T00:00:00.000Z",
            }
            result = service.tasks().insert(
                tasklist=TASKS_LIST_ID, body=task_body
            ).execute()
            created_tasks.append({
                "task_id": result.get("id"),
                "title":   result.get("title"),
                "due":     due_date,
            })
        return {
            "created": True,
            "tasks_created": len(created_tasks),
            "tasks": created_tasks,
            "message": f"Due diligence checklist created for {company_name}",
        }
    except Exception as e:
        return {"created": False, "error": str(e)}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    sa_exists = os.path.exists(SERVICE_ACCOUNT_FILE)
    return {
        "service":             "VEDA MCP Server v3",
        "tools":               ["github", "google_calendar", "google_tasks"],
        "github_configured":   bool(GITHUB_TOKEN),
        "google_configured":   sa_exists,
        "version":             "3.0.0 — Real GitHub + Calendar + Tasks",
    }
