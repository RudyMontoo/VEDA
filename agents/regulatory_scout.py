"""
VEDA — Sub-Agent 2: Regulatory Scout
Checks compliance using RAG-style knowledge base + Gemini.
"""

import json
import re
from utils.vertex_helper import ask_gemini

COMPLIANCE_KB = {
    "fintech": [
        "RBI Digital Lending Guidelines 2022",
        "SEBI LODR Regulations",
        "Prevention of Money Laundering Act (PMLA)",
        "Payment and Settlement Systems Act",
    ],
    "healthtech": [
        "Digital Information Security in Healthcare Act (DISHA)",
        "IT Act 2000 – Data Privacy",
        "CDSCO Medical Device Rules 2017",
        "Telemedicine Practice Guidelines 2020",
    ],
    "edtech": [
        "National Education Policy 2020",
        "UDISE+ Data Compliance",
        "PDPB Data Localisation Requirements",
    ],
    "saas": [
        "IT Act 2000 Section 43A",
        "PDPB 2023 Obligations",
        "GST Compliance for SaaS",
        "RBI Cloud Outsourcing Guidelines",
    ],
    "default": [
        "Companies Act 2013",
        "PDPB 2023",
        "IT Act 2000",
        "GST Act",
        "FEMA Regulations",
    ],
}


class RegulatoryScoutAgent:

    def run(self, job_id: str, company_name: str, industry: str, description: str = "") -> dict:
        print(f"[RegulatoryScout] Checking: {company_name} ({industry})")
        regulations = self._retrieve(industry)
        prompt      = self._build_prompt(company_name, industry, description, regulations)
        raw         = ask_gemini(prompt)
        result      = self._parse(raw)
        result["applicable_regulations"] = regulations
        result["job_id"] = job_id
        print(f"[RegulatoryScout] Compliance score: {result.get('compliance_score')}")
        return result

    def _retrieve(self, industry: str) -> list:
        key = industry.lower().replace(" ", "")
        for k in COMPLIANCE_KB:
            if k in key:
                return COMPLIANCE_KB[k]
        return COMPLIANCE_KB["default"]

    def _build_prompt(self, company_name, industry, description, regulations) -> str:
        reg_list = "\n".join(f"  - {r}" for r in regulations)
        return f"""
You are a regulatory compliance analyst specialising in Indian corporate law.
You are performing due diligence for a potential acquisition.

Company: {company_name}
Industry: {industry}
Description: {description or "Not provided"}

Applicable Regulations:
{reg_list}

Respond ONLY with a valid JSON object (no markdown, no extra text):

{{
  "compliance_score": <integer 0-100, where 100=fully compliant, 0=critical violations>,
  "regulatory_risks": [<list of specific regulatory risks>],
  "compliant_areas": [<areas where compliance is likely met>],
  "red_flags": [<serious compliance concerns that could block the deal>],
  "compliance_summary": "<2-3 sentence summary for the board>",
  "due_diligence_recommendations": [<list of documents to request from the target>]
}}
"""

    def _parse(self, raw: str) -> dict:
        try:
            clean = re.sub(r"```json|```", "", raw).strip()
            return json.loads(clean)
        except Exception:
            return {
                "compliance_score": 50,
                "regulatory_risks": ["Could not parse response"],
                "compliant_areas": [],
                "red_flags": [],
                "compliance_summary": raw[:300],
                "due_diligence_recommendations": [],
            }