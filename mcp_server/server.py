"""
VEDA — MCP Server (Enhanced)
Fetches much richer GitHub data for accurate scoring.
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta

app = FastAPI(title="VEDA MCP Server", version="2.0.0")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


class RepoRequest(BaseModel):
    repo_url: str

class CalendarRequest(BaseModel):
    summary: str
    start_datetime: str
    end_datetime: str
    attendee_email: Optional[str] = ""
    description: Optional[str] = ""

class TaskRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = ""


def _repo_path(url: str) -> str:
    url = url.rstrip("/")
    if "github.com/" in url:
        return url.split("github.com/")[-1]
    return url


def _headers():
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


def _get_calendar_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=creds)


@app.post("/github/repo")
async def scan_repo(request: RepoRequest):
    repo_path = _repo_path(request.repo_url)
    headers   = _headers()

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
                date_str = c["commit"]["author"]["date"]
                commit_dates.append(_days_since(date_str))
            except Exception:
                pass

        commits_last_30_days = sum(1 for d in commit_dates if d <= 30)
        commits_last_90_days = sum(1 for d in commit_dates if d <= 90)
        avg_days_between_commits = (
            round(sum(commit_dates[:10]) / min(len(commit_dates), 10), 1)
            if commit_dates else 999
        )

        issues_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/issues?state=open&per_page=20",
            headers=headers, timeout=10
        )
        open_issues_data = issues_resp.json() if issues_resp.status_code == 200 else []
        real_issues = [i for i in open_issues_data if "pull_request" not in i]
        old_issues = sum(1 for i in real_issues if _days_since(i.get("created_at", "")) > 90)

        pr_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/pulls?state=open&per_page=1",
            headers=headers, timeout=10
        )
        open_prs = int(pr_resp.headers.get("x-total-count", 0)) if pr_resp.status_code == 200 else 0

        closed_pr_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/pulls?state=closed&per_page=10",
            headers=headers, timeout=10
        )
        closed_prs = closed_pr_resp.json() if closed_pr_resp.status_code == 200 else []
        avg_pr_merge_days = 0
        if closed_prs:
            merge_times = []
            for pr in closed_prs:
                if pr.get("merged_at") and pr.get("created_at"):
                    days = _days_since(pr["created_at"]) - _days_since(pr["merged_at"])
                    merge_times.append(abs(days))
            avg_pr_merge_days = round(sum(merge_times) / len(merge_times), 1) if merge_times else 0

        cicd_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/contents/.github/workflows",
            headers=headers, timeout=10
        )
        has_cicd = cicd_resp.status_code == 200
        cicd_files = len(cicd_resp.json()) if has_cicd and isinstance(cicd_resp.json(), list) else 0

        test_dirs = ["tests", "test", "__tests__", "spec", "specs"]
        has_tests = False
        for d in test_dirs:
            test_resp = await client.get(
                f"https://api.github.com/repos/{repo_path}/contents/{d}",
                headers=headers, timeout=5
            )
            if test_resp.status_code == 200:
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

        release_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/releases?per_page=5",
            headers=headers, timeout=10
        )
        releases = release_resp.json() if release_resp.status_code == 200 else []
        latest_release = releases[0].get("tag_name", "none") if releases else "none"
        days_since_last_release = (
            _days_since(releases[0]["published_at"]) if releases else 999
        )

        readme_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/readme",
            headers=headers, timeout=5
        )
        readme_size = readme_resp.json().get("size", 0) if readme_resp.status_code == 200 else 0

        dep_files = ["requirements.txt", "package.json", "go.mod", "Cargo.toml", "pom.xml", "build.gradle"]
        dependency_files_found = []
        for dep in dep_files:
            dep_resp = await client.get(
                f"https://api.github.com/repos/{repo_path}/contents/{dep}",
                headers=headers, timeout=5
            )
            if dep_resp.status_code == 200:
                dependency_files_found.append(dep)

    total_bytes = sum(languages.values()) or 1
    lang_pct = {l: round(b / total_bytes * 100, 1) for l, b in languages.items()}
    days_since_push = _days_since(repo.get("pushed_at", ""))

    return {
        "repo_url":           request.repo_url,
        "name":               repo.get("name"),
        "description":        repo.get("description"),
        "created_at":         repo.get("created_at", ""),
        "days_since_push":    days_since_push,
        "stars":              repo.get("stargazers_count", 0),
        "forks":              repo.get("forks_count", 0),
        "watchers":           repo.get("watchers_count", 0),
        "languages":          lang_pct,
        "size_kb":            repo.get("size", 0),
        "has_tests":          has_tests,
        "has_cicd":           has_cicd,
        "cicd_workflow_count":cicd_files,
        "has_security_policy":has_security_policy,
        "dependency_files":   dependency_files_found,
        "readme_size_bytes":  readme_size,
        "commits_last_30_days":   commits_last_30_days,
        "commits_last_90_days":   commits_last_90_days,
        "avg_days_between_commits": avg_days_between_commits,
        "days_since_last_release":  days_since_last_release,
        "latest_release":           latest_release,
        "open_issues":        repo.get("open_issues_count", 0),
        "old_issues_90d":     old_issues,
        "open_prs":           open_prs,
        "avg_pr_merge_days":  avg_pr_merge_days,
        "contributors_count": contributors,
        "license":            repo.get("license", {}).get("name") if repo.get("license") else "None",
        "default_branch":     repo.get("default_branch", "main"),
        "is_fork":            repo.get("fork", False),
        "is_archived":        repo.get("archived", False),
        "has_wiki":           repo.get("has_wiki", False),
    }


@app.post("/calendar/schedule")
async def schedule_meeting(request: CalendarRequest):
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        import os

        creds = service_account.Credentials.from_service_account_file(
            "service_account.json",
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": request.summary,
            "description": request.description,
            "start": {"dateTime": request.start_datetime, "timeZone": "Asia/Kolkata"},
            "end":   {"dateTime": request.end_datetime,   "timeZone": "Asia/Kolkata"},
        }

        created = service.events().insert(
            calendarId="rudraeng27@gmail.com", body=event
        ).execute()

        return {
            "event_id":  created["id"],
            "summary":   created["summary"],
            "start":     created["start"]["dateTime"],
            "meet_link": created.get("hangoutLink", "https://meet.google.com/veda-meeting"),
            "html_link": created.get("htmlLink", ""),
            "scheduled": True,
        }
    except Exception as e:
        return {
            "event_id":  "evt_fallback",
            "summary":   request.summary,
            "scheduled": False,
            "error":     str(e),
        }


@app.post("/tasks/create")
async def create_task(request: TaskRequest):
    try:
        service = _get_calendar_service()
        due = request.due_date or (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")
        event = {
            "summary": f"[TASK] {request.title}",
            "description": request.description or "",
            "start": {"date": due},
            "end":   {"date": due},
            "colorId": "6",
        }
        created = service.events().insert(
            calendarId="rudraeng27@gmail.com", body=event
        ).execute()
        return {
            "task_id": created["id"],
            "title":   request.title,
            "status":  "needsAction",
            "due":     due,
            "created": True,
        }
    except Exception as e:
        return {
            "task_id": f"task_{abs(hash(request.title)) % 99999:05d}",
            "title":   request.title,
            "status":  "TODO",
            "created": False,
            "error":   str(e),
        }


@app.post("/tasks/create_checklist")
async def create_due_diligence_checklist(company_name: str, industry: str = "saas"):
    checklist = [
        {"title": f"[TASK] Review technical audit — {company_name}", "days": 1},
        {"title": f"[TASK] Verify regulatory compliance — {company_name}", "days": 2},
        {"title": f"[TASK] Validate 3-year forecast — {company_name}", "days": 3},
        {"title": f"[TASK] Request due diligence documents — {company_name}", "days": 3},
        {"title": f"[TASK] Legal review of deal conditions — {company_name}", "days": 5},
        {"title": f"[TASK] Final acquisition decision — {company_name}", "days": 7},
    ]
    try:
        service = _get_calendar_service()
        created_tasks = []
        for item in checklist:
            due = (datetime.utcnow() + timedelta(days=item["days"])).strftime("%Y-%m-%d")
            event = {
                "summary": item["title"],
                "description": f"VEDA Due Diligence Task | Company: {company_name} | Industry: {industry}",
                "start": {"date": due},
                "end":   {"date": due},
                "colorId": "6",
            }
            created = service.events().insert(
                calendarId="rudraeng27@gmail.com", body=event
            ).execute()
            created_tasks.append({
                "task_id": created["id"],
                "title":   item["title"],
                "due":     due,
                "status":  "needsAction",
            })
        return {"created": True, "tasks_created": len(created_tasks), "tasks": created_tasks}
    except Exception as e:
        return {"created": False, "error": str(e)}


@app.get("/tasks/list")
async def list_tasks():
    try:
        service = _get_calendar_service()
        now = datetime.utcnow().isoformat() + "Z"
        result = service.events().list(
            calendarId="rudraeng27@gmail.com",
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
            q="[TASK]",
        ).execute()
        tasks = [
            {
                "task_id": e.get("id"),
                "title":   e.get("summary", "").replace("[TASK] ", ""),
                "due":     e.get("start", {}).get("date", ""),
                "status":  "needsAction",
            }
            for e in result.get("items", [])
        ]
        return {"tasks": tasks, "total": len(tasks)}
    except Exception as e:
        return {"tasks": [], "error": str(e)}


@app.get("/health")
def health():
    return {
        "service": "VEDA MCP Server v2",
        "tools":   ["github", "calendar", "tasks"],
        "github_configured": bool(GITHUB_TOKEN),
        "version": "2.0.0 — Enhanced GitHub signals",
    }