"""
VEDA — Sub-Agent 3: Market Analyst
3-year Bear/Base/Bull simulation — the winning feature.
"""

import json
import re
from utils.vertex_helper import ask_gemini


class MarketAnalystAgent:

    def run(self, job_id: str, company_name: str, industry: str,
            tech_debt_score: float, compliance_score: float) -> dict:
        print(f"[MarketAnalyst] Running 3-year simulation for: {company_name}")
        market_fit = round(tech_debt_score * 0.55 + compliance_score * 0.45, 2)
        prompt     = self._build_prompt(company_name, industry, tech_debt_score, compliance_score, market_fit)
        raw        = ask_gemini(prompt)
        result     = self._parse(raw)
        result["market_fit_score"] = market_fit
        result["job_id"]           = job_id
        print(f"[MarketAnalyst] Market fit: {market_fit}")
        return result

    def _build_prompt(self, company_name, industry, tech_debt, compliance, market_fit) -> str:
        return f"""
You are a senior investment analyst at a tier-1 venture capital fund.
Build a 3-year growth simulation for a potential M&A target.

Company: {company_name}
Industry: {industry}
Tech Debt Score: {tech_debt}/100
Compliance Score: {compliance}/100
Composite Market Fit Score: {market_fit}/100

Respond ONLY with a valid JSON object (no markdown, no extra text):

{{
  "simulation_year": 3,
  "base_assumptions": {{
    "current_arr_estimate_inr_lakhs": <number>,
    "current_team_size": <number>,
    "primary_growth_driver": "<string>"
  }},
  "scenarios": {{
    "bear": {{
      "probability": "<percentage string>",
      "year1_arr_inr_lakhs": <number>,
      "year2_arr_inr_lakhs": <number>,
      "year3_arr_inr_lakhs": <number>,
      "year3_headcount": <number>,
      "key_risk": "<string>",
      "valuation_multiple": <number>
    }},
    "base": {{
      "probability": "<percentage string>",
      "year1_arr_inr_lakhs": <number>,
      "year2_arr_inr_lakhs": <number>,
      "year3_arr_inr_lakhs": <number>,
      "year3_headcount": <number>,
      "key_driver": "<string>",
      "valuation_multiple": <number>
    }},
    "bull": {{
      "probability": "<percentage string>",
      "year1_arr_inr_lakhs": <number>,
      "year2_arr_inr_lakhs": <number>,
      "year3_arr_inr_lakhs": <number>,
      "year3_headcount": <number>,
      "key_driver": "<string>",
      "valuation_multiple": <number>
    }}
  }},
  "recommended_acquisition_price_range_inr_cr": {{
    "min": <number>,
    "max": <number>
  }},
  "forecast_summary": "<3-sentence boardroom-ready summary>"
}}
"""

    def _parse(self, raw: str) -> dict:
        try:
            clean = re.sub(r"```json|```", "", raw).strip()
            return json.loads(clean)
        except Exception:
            return {
                "market_fit_score": 50,
                "simulation_year": 3,
                "scenarios": {},
                "forecast_summary": raw[:300],
                "recommended_acquisition_price_range_inr_cr": {"min": 0, "max": 0},
            }