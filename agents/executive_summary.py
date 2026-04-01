"""
VEDA — Sub-Agent 4: Executive Summary
Synthesises all agent outputs into a boardroom-ready report.
"""

import json
import re
from utils.vertex_helper import ask_gemini


class ExecutiveSummaryAgent:

    def run(self, job_id: str, company_name: str,
            code_results: dict, reg_results: dict, market_results: dict) -> dict:
        print(f"[ExecutiveSummary] Generating report for: {company_name}")
        prompt = self._build_prompt(company_name, code_results, reg_results, market_results)
        raw    = ask_gemini(prompt)
        result = self._parse(raw)
        result["job_id"] = job_id
        print(f"[ExecutiveSummary] Recommendation: {result.get('recommendation')}")
        return result

    def _build_prompt(self, company_name, code, reg, market) -> str:
        return f"""
You are the Managing Partner of a leading M&A advisory firm.
Synthesise the due diligence findings into a final investment recommendation.

Company: {company_name}

CODE AUDIT:
- Tech Debt Score: {code.get('tech_debt_score')}/100
- Security Flags: {code.get('security_flags', [])}
- Summary: {code.get('code_quality_summary', '')}

REGULATORY:
- Compliance Score: {reg.get('compliance_score')}/100
- Red Flags: {reg.get('red_flags', [])}
- Summary: {reg.get('compliance_summary', '')}

MARKET FORECAST:
- Market Fit Score: {market.get('market_fit_score')}/100
- Price Range: {market.get('recommended_acquisition_price_range_inr_cr', {})}
- Summary: {market.get('forecast_summary', '')}

Respond ONLY with a valid JSON object (no markdown, no extra text):

{{
  "recommendation": "<PROCEED | PROCEED WITH CONDITIONS | DO NOT PROCEED>",
  "confidence_level": "<HIGH | MEDIUM | LOW>",
  "overall_rating": "<STRONG BUY | BUY | HOLD | AVOID>",
  "key_strengths": [<top 3 reasons to proceed>],
  "key_concerns": [<top 3 reasons for caution>],
  "conditions_for_deal": [<pre-closing conditions if applicable>],
  "executive_summary": "<5-7 sentence professional summary for board>",
  "one_line_verdict": "<single crisp sentence capturing the deal>"
}}
"""

    def _parse(self, raw: str) -> dict:
        try:
            clean = re.sub(r"```json|```", "", raw).strip()
            return json.loads(clean)
        except Exception:
            return {
                "recommendation": "UNKNOWN",
                "confidence_level": "LOW",
                "overall_rating": "HOLD",
                "key_strengths": [],
                "key_concerns": [],
                "conditions_for_deal": [],
                "executive_summary": raw[:500],
                "one_line_verdict": "Analysis incomplete.",
            }