"""
VEDA — MCP Server
Exposes GitHub, Calendar, and Tasks as REST tools.
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="VEDA MCP Server", version="1.0.0")

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


@app.post("/github/repo")
async def scan_repo(request: RepoRequest):
    repo_path = _repo_path(request.repo_url)
    headers   = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        repo_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}", headers=headers, timeout=15
        )
        if repo_resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Repository not found")
        if repo_resp.status_code != 200:
            raise HTTPException(status_code=repo_resp.status_code, detail="GitHub API error")

        repo = repo_resp.json()

        lang_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/languages", headers=headers
        )
        languages = lang_resp.json() if lang_resp.status_code == 200 else {}

        cicd_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/contents/.github/workflows",
            headers=headers,
        )
        has_cicd = cicd_resp.status_code == 200

        test_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/contents/tests",
            headers=headers,
        )
        has_tests = test_resp.status_code == 200

        contrib_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/contributors?per_page=1&anon=true",
            headers=headers,
        )
        contributors = int(contrib_resp.headers.get("x-total-count", 0)) if contrib_resp.status_code == 200 else 0

        pr_resp = await client.get(
            f"https://api.github.com/repos/{repo_path}/pulls?state=open&per_page=1",
            headers=headers,
        )
        open_prs = int(pr_resp.headers.get("x-total-count", 0)) if pr_resp.status_code == 200 else 0

    total = sum(languages.values()) or 1
    lang_pct = {l: round(b / total * 100, 1) for l, b in languages.items()}

    return {
        "repo_url":          request.repo_url,
        "name":              repo.get("name"),
        "description":       repo.get("description"),
        "stars":             repo.get("stargazers_count", 0),
        "forks":             repo.get("forks_count", 0),
        "open_issues":       repo.get("open_issues_count", 0),
        "open_prs":          open_prs,
        "languages":         lang_pct,
        "contributors_count":contributors,
        "has_tests":         has_tests,
        "has_cicd":          has_cicd,
        "last_commit":       repo.get("pushed_at", ""),
        "license":           repo.get("license", {}).get("name") if repo.get("license") else "None",
        "size_kb":           repo.get("size", 0),
        "default_branch":    repo.get("default_branch", "main"),
    }


@app.post("/calendar/schedule")
async def schedule_meeting(request: CalendarRequest):
    return {
        "event_id":  f"evt_{hash(request.summary) % 99999:05d}",
        "summary":   request.summary,
        "start":     request.start_datetime,
        "end":       request.end_datetime,
        "meet_link": "https://meet.google.com/veda-meeting",
        "scheduled": True,
    }


@app.post("/tasks/create")
async def create_task(request: TaskRequest):
    return {
        "task_id": f"task_{hash(request.title) % 99999:05d}",
        "title":   request.title,
        "status":  "TODO",
        "created": True,
    }


@app.get("/health")
def health():
    return {
        "service": "VEDA MCP Server",
        "tools":   ["github", "calendar", "tasks"],
        "github_configured": bool(GITHUB_TOKEN),
    }