"""
VEDA — Primary Agent (Investment Principal)
Orchestrates all 4 sub-agents and broadcasts live progress via WebSocket.
"""

import asyncio
import traceback
from datetime import datetime, timedelta

import vertexai
from vertexai.generative_models import GenerativeModel

from agents.code_auditor import CodeAuditorAgent
from agents.regulatory_scout import RegulatoryScoutAgent
from agents.market_analyst import MarketAnalystAgent
from agents.executive_summary import ExecutiveSummaryAgent
from db.bigquery_client import BigQueryClient
from utils.config import PROJECT_ID, LOCATION


class PrimaryAgent:

    def __init__(self, progress_manager=None):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model          = GenerativeModel("gemini-1.5-pro-002")
        self.bq             = BigQueryClient()
        self.progress       = progress_manager
        self.code_auditor   = CodeAuditorAgent()
        self.reg_scout      = RegulatoryScoutAgent()
        self.market_analyst = MarketAnalystAgent()
        self.exec_summary   = ExecutiveSummaryAgent()

    def run_full_audit(
        self,
        job_id: str,
        company_name: str,
        github_repo_url: str,
        industry: str,
        description: str = "",
        schedule_meeting: bool = False,
        attendee_email: str = "",
    ):
        """Sync wrapper for FastAPI BackgroundTasks."""
        asyncio.run(self._async_run(
            job_id, company_name, github_repo_url,
            industry, description, schedule_meeting, attendee_email
        ))

    async def _async_run(
        self,
        job_id: str,
        company_name: str,
        github_repo_url: str,
        industry: str,
        description: str,
        schedule_meeting: bool,
        attendee_email: str,
    ):
        try:
            self.bq.update_job_status(job_id, "RUNNING", "VEDA audit started")

            # ── Step 1: Code Audit ──────────────────────────────────────
            await self.progress.agent_started(
                job_id, 1, "Code Auditor",
                f"🔍 Scanning GitHub repository: {github_repo_url}"
            )
            self.bq.log_agent_event(job_id, 1, "Code Auditor", "RUNNING",
                f"Scanning {github_repo_url}", 0)

            code_results = self.code_auditor.run(job_id, github_repo_url, company_name)

            await self.progress.agent_completed(
                job_id, 1, "Code Auditor",
                f"✅ Code audit done — Tech Debt Score: {code_results.get('tech_debt_score')}/100",
                data={
                    "tech_debt_score": code_results.get("tech_debt_score"),
                    "security_flags":  code_results.get("security_flags", []),
                    "summary":         code_results.get("code_quality_summary", ""),
                }
            )
            self.bq.log_agent_event(job_id, 1, "Code Auditor", "DONE",
                f"Tech debt score: {code_results.get('tech_debt_score')}", 25,
                code_results)

            # ── Step 2: Regulatory Compliance ───────────────────────────
            await self.progress.agent_started(
                job_id, 2, "Regulatory Scout",
                f"📋 Checking {industry} sector compliance..."
            )
            self.bq.log_agent_event(job_id, 2, "Regulatory Scout", "RUNNING",
                f"Checking compliance for {industry}", 25)

            reg_results = self.reg_scout.run(job_id, company_name, industry, description)

            await self.progress.agent_completed(
                job_id, 2, "Regulatory Scout",
                f"✅ Compliance done — Score: {reg_results.get('compliance_score')}/100",
                data={
                    "compliance_score": reg_results.get("compliance_score"),
                    "red_flags":        reg_results.get("red_flags", []),
                    "summary":          reg_results.get("compliance_summary", ""),
                }
            )
            self.bq.log_agent_event(job_id, 2, "Regulatory Scout", "DONE",
                f"Compliance score: {reg_results.get('compliance_score')}", 50,
                reg_results)

            # ── Step 3: Market Forecast ──────────────────────────────────
            await self.progress.agent_started(
                job_id, 3, "Market Analyst",
                "📈 Running 3-year Bear / Base / Bull simulation..."
            )
            self.bq.log_agent_event(job_id, 3, "Market Analyst", "RUNNING",
                "Running 3-year forecast simulation", 50)

            market_results = self.market_analyst.run(
                job_id, company_name, industry,
                code_results["tech_debt_score"],
                reg_results["compliance_score"],
            )

            await self.progress.agent_completed(
                job_id, 3, "Market Analyst",
                f"✅ Forecast ready — Market Fit: {market_results.get('market_fit_score')}/100",
                data={
                    "market_fit_score": market_results.get("market_fit_score"),
                    "price_range":      market_results.get("recommended_acquisition_price_range_inr_cr"),
                    "summary":          market_results.get("forecast_summary", ""),
                }
            )
            self.bq.log_agent_event(job_id, 3, "Market Analyst", "DONE",
                f"Market fit: {market_results.get('market_fit_score')}", 75,
                market_results)

            # ── Step 4: Executive Summary ────────────────────────────────
            await self.progress.agent_started(
                job_id, 4, "Executive Summary",
                "📝 Generating boardroom-ready report..."
            )
            self.bq.log_agent_event(job_id, 4, "Executive Summary", "RUNNING",
                "Generating executive report", 75)

            summary_results = self.exec_summary.run(
                job_id, company_name, code_results, reg_results, market_results
            )

            # ── Optional: Schedule kickoff meeting ───────────────────────
            if schedule_meeting and attendee_email:
                await self._schedule_kickoff(job_id, company_name, attendee_email)

            # ── Compute overall risk score ────────────────────────────────
            overall_risk = round(
                code_results["tech_debt_score"] * 0.6 +
                reg_results["compliance_score"] * 0.4, 2
            )

            # ── Save full report ─────────────────────────────────────────
            report = {
                "job_id":           job_id,
                "company_name":     company_name,
                "industry":         industry,
                "overall_risk_score": overall_risk,
                "code_audit":       code_results,
                "regulatory":       reg_results,
                "market_forecast":  market_results,
                "executive_summary": summary_results,
                "completed_at":     datetime.utcnow().isoformat(),
            }

            self.bq.save_report(job_id, report)
            self.bq.update_job_status(job_id, "COMPLETED", "VEDA audit complete")
            self.bq.log_agent_event(job_id, 4, "Executive Summary", "DONE",
                f"Verdict: {summary_results.get('one_line_verdict', '')}", 100,
                summary_results)

            await self.progress.agent_completed(
                job_id, 4, "Executive Summary",
                f"✅ Report ready — {summary_results.get('one_line_verdict', '')}",
                data={
                    "recommendation": summary_results.get("recommendation"),
                    "overall_rating": summary_results.get("overall_rating"),
                    "one_line_verdict": summary_results.get("one_line_verdict"),
                }
            )

            await self.progress.audit_completed(job_id, {
                "overall_risk_score": overall_risk,
                "recommendation":     summary_results.get("recommendation"),
                "overall_rating":     summary_results.get("overall_rating"),
                "one_line_verdict":   summary_results.get("one_line_verdict"),
                "report_url":         f"/report/{job_id}",
                "pdf_url":            f"/report/{job_id}/pdf",
            })

        except Exception as e:
            err = traceback.format_exc()
            self.bq.update_job_status(job_id, "FAILED", str(e))
            self.bq.log_error(job_id, error=e, traceback_str=err)
            await self.progress.audit_failed(job_id, str(e))
            raise

    async def _schedule_kickoff(self, job_id: str, company_name: str, attendee_email: str):
        """Schedule a kickoff meeting via MCP Calendar tool."""
        import httpx
        from utils.config import MCP_SERVER_URL
        start = datetime.utcnow() + timedelta(days=1)
        end   = start + timedelta(hours=1)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MCP_SERVER_URL}/calendar/schedule",
                    json={
                        "summary":         f"VEDA Due Diligence Kickoff — {company_name}",
                        "start_datetime":  start.isoformat() + "Z",
                        "end_datetime":    end.isoformat() + "Z",
                        "attendee_email":  attendee_email,
                        "description":     f"Kickoff meeting scheduled by VEDA for {company_name} due diligence.",
                    },
                    timeout=10,
                )
                print(f"[PrimaryAgent] Meeting scheduled: {resp.json()}")
        except Exception as e:
            print(f"[PrimaryAgent] Calendar scheduling failed (non-fatal): {e}")