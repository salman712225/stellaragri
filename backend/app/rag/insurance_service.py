"""
Crop Insurance Scheme Knowledge Service (PMFBY, RWBCIS & State Relief Schemes)
Provides official, non-hallucinatory scheme guidelines, claim intimation rules,
required documentation, and eligibility criteria.
"""
from typing import Any, Dict, List, Optional


class InsuranceService:
    """
    Official Crop Insurance & PMFBY Knowledge Provider
    """

    SCHEMES = {
        "PMFBY": {
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "authority": "Ministry of Agriculture & Farmers Welfare, Govt of India",
            "portal_url": "https://pmfby.gov.in/",
            "guidelines_url": "https://pmfby.gov.in/guidelines",
            "downloads_url": "https://pmfby.gov.in/downloads",
            "coverage_stages": [
                {
                    "stage": "Prevented Sowing / Planting Risk",
                    "description": "Insured area prevented from sowing/planting due to deficit rainfall or adverse seasonal conditions (up to 25% of sum insured)."
                },
                {
                    "stage": "Standing Crop Loss (Mid-Season Adversity)",
                    "description": "Comprehensive risk insurance covers yield losses due to non-preventable risks: drought, dry spells, flood, inundation, wide spread pest/disease attack, landslide, natural fire, lightning, storm, hailstorm, cyclone."
                },
                {
                    "stage": "Post-Harvest Losses",
                    "description": "Coverage available up to a maximum period of 14 days from harvesting for crops kept in 'cut & spread' condition in the field against cyclone, cyclonic rains, and unseasonal rains."
                },
                {
                    "stage": "Localized Calamities",
                    "description": "Loss/damage resulting from occurrence of identified localized risks: Hailstorm, Landslide, Inundation, Cloud burst, and Natural fire affecting isolated farms in the notified area."
                }
            ],
            "intimation_window_hours": 72,
            "intimation_rule": "Mandatory claim intimation must be submitted within 72 hours of the loss event via Crop Insurance App, Toll-Free Number (14447 / 1800-180-1551), Bank branch, or local Agriculture Department officer.",
            "premium_rates": {
                "kharif_food_oilseeds": "2.0% of Sum Insured",
                "rabi_food_oilseeds": "1.5% of Sum Insured",
                "annual_commercial_horticultural": "5.0% of Sum Insured",
                "subsidy": "Balance premium is shared 50:50 between Central and State Government (90:10 for North Eastern states)."
            },
            "required_documents": [
                {
                    "name": "Land Ownership / Tenancy Record",
                    "aliases": ["7/12 Extract", "Patta / Chitta", "Khasra / Khatauni", "Adangal / Pahani", "Tenancy Agreement"],
                    "description": "Official revenue document proving land ownership or authorized tenancy/sharecropper status."
                },
                {
                    "name": "Sowing Certificate / Crop Sown Declaration",
                    "aliases": ["Vithan Certificate", "Sowing Declaration", "Village Administrative Officer (VAO) Certificate"],
                    "description": "Certified document verifying the crop cultivated and acreage."
                },
                {
                    "name": "Bank Passbook Copy",
                    "aliases": ["Bank Account Details", "Kisan Credit Card (KCC) Statement"],
                    "description": "Copy of bank passbook with clear Account Number and IFSC linked to Aadhaar."
                },
                {
                    "name": "Identity Proof (Aadhaar Card)",
                    "aliases": ["Aadhaar"],
                    "description": "Government-issued Aadhaar identification."
                },
                {
                    "name": "Geo-Tagged Damage Evidence",
                    "aliases": ["Geo-tagged Photos", "Crop Insurance App Upload"],
                    "description": "Photographs or video of the damaged crop with GPS location coordinates enabled."
                }
            ],
            "survey_and_settlement": {
                "process": "Joint loss assessment is conducted by Insurance Company loss assessor along with State Agriculture Department official / Revenue official.",
                "timeline": "Survey completed within 10-15 days of intimation; settlement processed directly to farmer's Aadhaar-seeded bank account via National Crop Insurance Portal (NCIP) DBT."
            }
        },
        "RWBCIS": {
            "name": "Restructured Weather Based Crop Insurance Scheme (RWBCIS)",
            "authority": "Govt of India & State Agriculture Departments",
            "description": "Provides insurance protection to farmers against adverse weather parameters such as deficit or excess rainfall, high or low temperature, humidity, and frost.",
            "intimation_window_hours": 72,
            "claim_trigger": "Claims are settled on the basis of weather data recorded at Reference Weather Stations (RWS) without requiring individual farm survey."
        }
    }

    PERMISSIBLE_LOSS_EVENTS = [
        "flood", "inundation", "cyclone", "unseasonal_rain", "heavy_rainfall",
        "drought", "dry_spell", "hailstorm", "landslide", "pest_attack",
        "disease_outbreak", "natural_fire", "frost", "cold_wave"
    ]

    @classmethod
    def get_scheme_overview(cls, scheme_key: str = "PMFBY") -> Dict[str, Any]:
        return cls.SCHEMES.get(scheme_key.upper(), cls.SCHEMES["PMFBY"])

    @classmethod
    def get_evidence_checklist(cls) -> List[Dict[str, str]]:
        pmfby = cls.SCHEMES["PMFBY"]
        return pmfby["required_documents"]

    @classmethod
    def check_intimation_eligibility(cls, days_since_incident: float) -> Dict[str, Any]:
        """
        Check if the reported loss falls within the mandatory 72-hour (3 days) window.
        """
        hours_elapsed = days_since_incident * 24
        is_within_window = hours_elapsed <= 72

        return {
            "is_within_72h_window": is_within_window,
            "hours_elapsed": round(hours_elapsed, 1),
            "advice": (
                "Claim is within the valid 72-hour intimation window. File claim intimation immediately."
                if is_within_window else
                f"Incident occurred ~{round(days_since_incident, 1)} days ago (>72 hours). Immediate intimation is critical; submit with special delay explanation to the District Agriculture Officer."
            )
        }

    @classmethod
    def format_scheme_context_for_llm(cls) -> str:
        """
        Generates a factual, grounded context block for LLM prompt injections.
        """
        pmfby = cls.SCHEMES["PMFBY"]
        docs = ", ".join([d["name"] for d in pmfby["required_documents"]])
        return (
            f"GOVERNMENT CROP INSURANCE (PMFBY) FACTUAL RULES:\n"
            f"- Applicable Scheme: {pmfby['name']}\n"
            f"- Claim Intimation Window: Mandatory within 72 hours of damage event.\n"
            f"- Required Evidence: {docs}.\n"
            f"- Assessment Method: Physical on-field joint survey by Insurance Assessor & State Agriculture/Revenue official.\n"
            f"- Payout / Settlement Rule: Processed directly to Aadhaar-linked bank account via DBT post-survey.\n"
            f"- STRICT ANTI-OVERPROMISING GUARDRAIL: AI must NEVER guarantee approval or specify payout amounts. Every claim is subject to surveyor verification."
        )
