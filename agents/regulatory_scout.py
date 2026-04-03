"""
VEDA — Sub-Agent 2: Regulatory Scout (Enhanced)
Uses detailed industry-specific compliance frameworks for accurate scoring.
"""

import json
import re
from utils.vertex_helper import ask_gemini

# Detailed compliance requirements per industry
COMPLIANCE_FRAMEWORKS = {
    "fintech": {
        "regulations": [
            "RBI Digital Lending Guidelines 2022",
            "SEBI LODR Regulations",
            "Prevention of Money Laundering Act (PMLA)",
            "Payment and Settlement Systems Act 2007",
            "RBI Master Directions on KYC",
            "FEMA Regulations",
            "Consumer Protection Act 2019",
        ],
        "critical_checks": [
            "RBI/SEBI registration or license status",
            "KYC/AML compliance program",
            "Data localisation compliance (RBI)",
            "Escrow account maintenance",
            "Grievance redressal mechanism",
            "Interest rate disclosure norms",
            "Nodal officer appointment",
        ],
        "red_flag_triggers": [
            "Operating without RBI/SEBI license",
            "Missing KYC process",
            "No escrow account",
            "PMLA violations",
            "Data stored outside India",
        ],
        "base_risk": "HIGH",
    },
    "healthtech": {
        "regulations": [
            "Digital Information Security in Healthcare Act (DISHA)",
            "IT Act 2000 – Data Privacy Sections",
            "CDSCO Medical Device Rules 2017",
            "Telemedicine Practice Guidelines 2020",
            "Clinical Establishments Act",
            "Drugs and Cosmetics Act",
        ],
        "critical_checks": [
            "DISHA compliance for patient data",
            "Telemedicine platform registration",
            "Doctor verification process",
            "Data encryption for health records",
            "Consent management system",
            "Medical device approval (if applicable)",
        ],
        "red_flag_triggers": [
            "Storing health data without encryption",
            "No doctor verification",
            "Unapproved medical devices",
            "Missing consent framework",
        ],
        "base_risk": "HIGH",
    },
    "edtech": {
        "regulations": [
            "National Education Policy 2020",
            "UDISE+ Data Compliance",
            "PDPB 2023 (Children's data)",
            "Consumer Protection (E-Commerce) Rules 2020",
            "UGC regulations (if degree programs)",
        ],
        "critical_checks": [
            "COPPA/PDPB compliance for under-18 users",
            "UGC recognition (if degrees offered)",
            "Refund policy compliance",
            "Data retention policies",
            "Content accuracy standards",
        ],
        "red_flag_triggers": [
            "Collecting children's data without parental consent",
            "Offering degrees without UGC recognition",
            "No refund mechanism",
        ],
        "base_risk": "MEDIUM",
    },
    "saas": {
        "regulations": [
            "IT Act 2000 Section 43A (Reasonable Security)",
            "PDPB 2023 Obligations",
            "GST Act (SaaS taxation)",
            "RBI Cloud Outsourcing Guidelines (if serving banks)",
            "Consumer Protection Act 2019",
            "Companies Act 2013",
        ],
        "critical_checks": [
            "PDPB data processing agreement",
            "GST registration and compliance",
            "SLA terms and liability caps",
            "Data breach notification process",
            "Cross-border data transfer mechanisms",
            "SOC2/ISO27001 certification status",
        ],
        "red_flag_triggers": [
            "No privacy policy",
            "No data processing agreement",
            "Missing GST registration",
            "No security certifications",
            "Unlimited liability in contracts",
        ],
        "base_risk": "MEDIUM",
    },
    "ecommerce": {
        "regulations": [
            "Consumer Protection (E-Commerce) Rules 2020",
            "IT Act 2000",
            "PDPB 2023",
            "GST Act",
            "Legal Metrology (Packaged Commodities) Rules",
            "FDI Policy for e-commerce",
        ],
        "critical_checks": [
            "Seller verification process",
            "Grievance officer appointment",
            "Return/refund policy compliance",
            "FDI compliance (inventory vs marketplace model)",
            "GST registration and TCS compliance",
            "Legal metrology compliance",
        ],
        "red_flag_triggers": [
            "FDI violations (inventory model without approval)",
            "No grievance officer",
            "Missing GST TCS compliance",
        ],
        "base_risk": "MEDIUM",
    },
    "deeptech": {
        "regulations": [
            "IT Act 2000",
            "PDPB 2023",
            "Patents Act 1970 (IP protection)",
            "Export Control Regulations (SCOMET)",
            "SEBI regulations (if funded)",
            "Companies Act 2013",
        ],
        "critical_checks": [
            "IP ownership clarity",
            "Export control compliance (dual-use tech)",
            "Patent filing status",
            "Academic IP assignment agreements",
            "PDPB compliance for AI/ML models",
            "Government contract compliance",
        ],
        "red_flag_triggers": [
            "Unclear IP ownership (academic spinout)",
            "Export control violations",
            "No patent protection",
        ],
        "base_risk": "LOW",
    },
    "default": {
        "regulations": [
            "Companies Act 2013",
            "PDPB 2023",
            "IT Act 2000",
            "GST Act",
            "FEMA Regulations",
            "Labour Laws (PF, ESI, Gratuity)",
        ],
        "critical_checks": [
            "Company registration and ROC filings",
            "GST registration",
            "Labour law compliance (PF/ESI)",
            "Data privacy policy",
            "IP ownership agreements",
            "Director KYC compliance",
        ],
        "red_flag_triggers": [
            "ROC filing defaults",
            "GST non-compliance",
            "Labour law violations",
        ],
        "base_risk": "LOW",
    },
}


class RegulatoryScoutAgent:

    def run(self, job_id: str, company_name: str,
            industry: str, description: str = "") -> dict:
        print(f"[RegulatoryScout] Checking: {company_name} ({industry})")

        framework = self._get_framework(industry)
        prompt    = self._build_prompt(company_name, industry, description, framework)
        raw       = ask_gemini(prompt)
        result    = self._parse(raw)

        result["applicable_regulations"]  = framework["regulations"]
        result["critical_checks"]         = framework["critical_checks"]
        result["industry_base_risk"]      = framework["base_risk"]
        result["job_id"]                  = job_id

        print(f"[RegulatoryScout] Compliance score: {result.get('compliance_score')}")
        return result

    def _get_framework(self, industry: str) -> dict:
        key = industry.lower().replace(" ", "").replace("-", "")
        for k in COMPLIANCE_FRAMEWORKS:
            if k in key:
                return COMPLIANCE_FRAMEWORKS[k]
        return COMPLIANCE_FRAMEWORKS["default"]

    def _build_prompt(self, company_name: str, industry: str,
                      description: str, framework: dict) -> str:
        regs   = "\n".join(f"  • {r}" for r in framework["regulations"])
        checks = "\n".join(f"  • {c}" for c in framework["critical_checks"])
        flags  = "\n".join(f"  • {f}" for f in framework["red_flag_triggers"])

        return f"""
You are a regulatory compliance specialist performing M&A due diligence in India.
You are assessing a {industry} company for acquisition.

Company: {company_name}
Industry: {industry}
Industry Risk Level: {framework["base_risk"]}
Description: {description or "Not provided"}

=== APPLICABLE REGULATIONS ===
{regs}

=== CRITICAL COMPLIANCE CHECKS ===
{checks}

=== RED FLAG TRIGGERS ===
{flags}

Based on the company description and industry, assess their compliance posture.
Consider:
1. What licenses/registrations are MANDATORY for this industry?
2. What data protection requirements apply?
3. What are the most likely compliance gaps for an early-stage {industry} company?
4. What would a regulator flag first?

Scoring guide:
- 85-100: Fully compliant, all licenses in place, low regulatory risk
- 70-84: Mostly compliant, minor gaps that are easily remediated
- 50-69: Significant gaps, requires 3-6 months to fix, some deal risk
- 30-49: Major violations, could attract regulatory action, high deal risk
- 0-29: Critical violations, deal-breaking regulatory issues

Respond ONLY with a valid JSON object (no markdown, no extra text):

{{
  "compliance_score": <integer 0-100>,
  "regulatory_risks": [<specific risks with regulation names>],
  "compliant_areas": [<areas likely compliant based on industry description>],
  "red_flags": [<deal-blocking compliance issues>],
  "compliance_summary": "<3-4 sentence assessment for the board>",
  "due_diligence_recommendations": [<specific documents to request>],
  "estimated_remediation_time": "<e.g. 1-2 months | 3-6 months | 6-12 months>",
  "regulatory_deal_blocker": <true|false>
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
                "compliant_areas":  [],
                "red_flags":        [],
                "compliance_summary": raw[:300],
                "due_diligence_recommendations": [],
                "estimated_remediation_time": "Unknown",
                "regulatory_deal_blocker": False,
            }