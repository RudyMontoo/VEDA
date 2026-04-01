"""
VEDA — Sub-Agent 1: Code Auditor
Scans GitHub repo via MCP and scores technical debt using Gemini.
"""

import json
import re
import httpx
from utils.config import MCP_SERVER_URL
from utils.vertex_helper import ask_gemini


class CodeAuditorAgent:

    def run(self, job_id: str, repo_url: str, company_name: str) -> dict:
        print(f"[CodeAuditor] Scanning: {repo_url}")
        github_data = self._fetch_repo(repo_url)
        prompt      = self._build_prompt(company_name, repo_url, github_data)
        raw         = ask_gemini(prompt)
        result      = self._parse(raw)
        result["raw_github_data"] = github_data
        result["job_id"]          = job_id
        print(f"[CodeAuditor] Tech debt score: {result.get('tech_debt_score')}")
        return result

    def _fetch_repo(self, repo_url: str) -> dict:
        try:
            resp = httpx.post(
                f"{MCP_SERVER_URL}/github/repo",
                json={"repo_url": repo_url},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"[CodeAuditor] MCP unavailable, using mock: {e}")
            return self._mock(repo_url)

    def _build_prompt(self, company_name: str, repo_url: str, data: dict) -> str:
        return f"""
You are a senior technical due diligence analyst performing a code audit for an M&A transaction.

Company: {company_name}
Repository: {repo_url}

GitHub Data:
- Stars: {data.get('stars', 'N/A')}
- Forks: {data.get('forks', 'N/A')}
- Open Issues: {data.get('open_issues', 'N/A')}
- Open PRs: {data.get('open_prs', 'N/A')}
- Languages: {data.get('languages', {})}
- Last Commit: {data.get('last_commit', 'N/A')}
- Contributors: {data.get('contributors_count', 'N/A')}
- Has Tests: {data.get('has_tests', False)}
- Has CI/CD: {data.get('has_cicd', False)}
- License: {data.get('license', 'None')}
- Size KB: {data.get('size_kb', 'N/A')}

Respond ONLY with a valid JSON object (no markdown, no extra text):

{{
  "tech_debt_score": <integer 0-100, where 100=no debt, 0=critical debt>,
  "security_flags": [<list of security concerns as strings>],
  "strengths": [<list of technical strengths>],
  "risks": [<list of technical risks>],
  "code_quality_summary": "<2-3 sentence professional summary>",
  "recommended_actions": [<list of remediation steps>]
}}
"""

    def _parse(self, raw: str) -> dict:
        try:
            clean = re.sub(r"```json|```", "", raw).strip()
            return json.loads(clean)
        except Exception:
            return {
                "tech_debt_score": 50,
                "security_flags": ["Could not parse response"],
                "strengths": [],
                "risks": ["Analysis incomplete"],
                "code_quality_summary": raw[:300],
                "recommended_actions": [],
            }

    def _mock(self, repo_url: str) -> dict:
        return {
            "repo_url": repo_url,
            "stars": 142, "forks": 23,
            "open_issues": 47, "open_prs": 12,
            "languages": {"Python": 68, "JavaScript": 22, "Shell": 10},
            "last_commit": "2024-11-15",
            "contributors_count": 5,
            "has_tests": True, "has_cicd": False,
            "license": "MIT", "size_kb": 4200,
        }