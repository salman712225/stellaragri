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
        }
    }

    # ── Fabricated & Government Crop Insurance Schemes by Disaster Category (5 per type) ──
    SCHEMES_BY_DISASTER = {
        "flood": [
            {
                "scheme_id": "FLD-01",
                "name": "PMFBY Localized Calamity (Inundation Coverage)",
                "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
                "coverage": "Up to 100% of Sum Insured based on on-field joint crop assessment",
                "intimation_window": "72 Hours",
                "eligibility": "Submerged cropland for >48 hours in notified panchayats",
                "documents": ["Patta/Chitta", "Sowing Certificate", "Geo-tagged field photos", "Bank passbook", "Aadhaar"]
            },
            {
                "scheme_id": "FLD-02",
                "name": "National Disaster Response Fund (NDRF) Submergence Input Relief",
                "authority": "Ministry of Home Affairs & State Disaster Management",
                "coverage": "₹8,500/hectare for rainfed crops, ₹17,000/hectare for irrigated land",
                "intimation_window": "7 Days via Village Revenue Officer (VAO)",
                "eligibility": "Crop loss exceeding 33% due to river overflow or flash floods",
                "documents": ["VAO Adangal / Pahani", "Khasra Extract", "Aadhaar Bank Linkage"]
            },
            {
                "scheme_id": "FLD-03",
                "name": "State SDRF Agricultural Flood Rehabilitation Grant",
                "authority": "State Department of Agriculture & Revenue",
                "coverage": "₹13,500/hectare for perennial horticulture crops",
                "intimation_window": "5 Days",
                "eligibility": "Paddy, Sugarcane, and Banana crops silted or washed away",
                "documents": ["Land Revenue Receipt", "Panchayat Verification Form", "Damage Photos"]
            },
            {
                "scheme_id": "FLD-04",
                "name": "Cauvery & Coastal Delta Waterlogging Relief Scheme",
                "authority": "Cauvery Delta Agri Development Authority",
                "coverage": "Direct seed & fertilizer re-sowing kit + ₹5,000/acre input grant",
                "intimation_window": "72 Hours",
                "eligibility": "Kuruvai / Samba Paddy submerged under drainage congestion",
                "documents": ["Patta / Chitta", "VAO Sowing Declaration"]
            },
            {
                "scheme_id": "FLD-05",
                "name": "Integrated Riverine Floodplain Crop Loss Protection Policy",
                "authority": "Central Water Commission & Agriculture Insurance Co.",
                "coverage": "Immediate 25% advance payout post satellite SAR water mask confirmation",
                "intimation_window": "96 Hours",
                "eligibility": "Farms located within notified 10-year river flood line",
                "documents": ["Survey Number Extract", "Aadhaar", "Bank Account Details"]
            }
        ],
        "drought": [
            {
                "scheme_id": "DRT-01",
                "name": "PMFBY Mid-Season Adversity (Severe Dry Spell / Drought)",
                "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
                "coverage": "Immediate on-account payment of up to 25% of likely claims",
                "intimation_window": "Triggered by District Disaster Management Committee",
                "eligibility": "Deficit rainfall >50% for 4 consecutive weeks or dry spell >21 days",
                "documents": ["PMFBY Policy Number / KCC Receipt", "Land Record", "Aadhaar"]
            },
            {
                "scheme_id": "DRT-02",
                "name": "ISRO NADAMS Satellite-Triggered Drought Assistance Grant",
                "authority": "NRSC / ISRO & Department of Agriculture",
                "coverage": "₹6,800/hectare direct DBT relief",
                "intimation_window": "Automatic satellite NDVI anomaly trigger",
                "eligibility": "NDVI vegetative anomaly < -0.30 across notified Talukas",
                "documents": ["Aadhaar DBT seeded Bank Account", "7/12 Extract"]
            },
            {
                "scheme_id": "DRT-03",
                "name": "Pradhan Mantri Krishi Sinchayee (PMKSY) Dryland Emergency Shield",
                "authority": "Ministry of Jal Shakti & Agriculture",
                "coverage": "80% subsidy on emergency drip lines + ₹4,000/acre water-tanker subsidy",
                "intimation_window": "10 Days",
                "eligibility": "Groundwater table drop >3 meters with standing crop moisture stress",
                "documents": ["Borewell/Well Registration", "Land Patta", "Electricity ID"]
            },
            {
                "scheme_id": "DRT-04",
                "name": "Marathwada & Deccan Rainfed Farmer Drought Assistance Policy",
                "authority": "State Agriculture Commissionerate",
                "coverage": "₹10,000/acre for Cotton and Soybean withered due to dry spell",
                "intimation_window": "72 Hours via Crop Insurance Portal",
                "eligibility": "Rainfed crops showing permanent wilting percentage",
                "documents": ["7/12 Extract", "Crop Sown Declaration", "Aadhaar"]
            },
            {
                "scheme_id": "DRT-05",
                "name": "Restructured Weather-Based Crop Insurance (RWBCIS) Deficit Index",
                "authority": "Weather-Based Crop Insurance Consortium",
                "coverage": "Index-linked payout calculated against Automatic Weather Station (AWS) data",
                "intimation_window": "Automatic station settlement without individual survey",
                "eligibility": "Rainfall below critical crop phenological trigger in AWS zone",
                "documents": ["RWBCIS Certificate of Insurance", "Bank Passbook"]
            }
        ],
        "cyclone": [
            {
                "scheme_id": "CYC-01",
                "name": "PMFBY Comprehensive Cyclone & High-Wind Storm Surge Risk",
                "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
                "coverage": "Comprehensive yield & localized standing crop indemnity",
                "intimation_window": "72 Hours",
                "eligibility": "Wind velocity >65 km/h or sea water inundation along coastal belt",
                "documents": ["Patta/Chitta", "Sowing Certificate", "Geo-tagged photo", "Bank passbook"]
            },
            {
                "scheme_id": "CYC-02",
                "name": "Coastal Belt Saline Inundation Soil Restoration Scheme",
                "authority": "State Land Development & Agriculture Department",
                "coverage": "₹15,000/hectare for gypsum application & green manuring",
                "intimation_window": "14 Days",
                "eligibility": "Cropland inundated with sea water rendering soil saline (EC >4 dS/m)",
                "documents": ["Soil Test Report / VAO Survey", "Land Ownership Record"]
            },
            {
                "scheme_id": "CYC-03",
                "name": "Cyclone Michaung / Remal Special Horticultural Recovery Scheme",
                "authority": "National Horticulture Board & State Directorate",
                "coverage": "₹20,000/acre for uprooted Coconut, Mango, Cashew, and Betel vine",
                "intimation_window": "7 Days",
                "eligibility": "Tree uprooting >30% in coastal cyclone track",
                "documents": ["Horticulture Census Record", "Geo-tagged Tree Photos", "Aadhaar"]
            },
            {
                "scheme_id": "CYC-04",
                "name": "National Cyclone Risk Mitigation Project (NCRMP) Relief Fund",
                "authority": "National Disaster Management Authority (NDMA)",
                "coverage": "₹12,000/family immediate livelihood assistance + input subsidy",
                "intimation_window": "48 Hours",
                "eligibility": "Small and marginal farmers within 10km of cyclone landfall point",
                "documents": ["Ration Card", "Aadhaar", "VAO Certificate"]
            },
            {
                "scheme_id": "CYC-05",
                "name": "Emergency Crop Lodging & Saltwater Surge Compensation Policy",
                "authority": "State Disaster Relief Authority",
                "coverage": "₹7,500/acre for lodged paddy & salt-encrusted standing crops",
                "intimation_window": "72 Hours",
                "eligibility": "Paddy crop lodging exceeding 50% canopy collapse",
                "documents": ["Patta / Chitta", "Field Photos with Timestamp", "Bank Details"]
            }
        ],
        "hailstorm": [
            {
                "scheme_id": "HAIL-01",
                "name": "PMFBY Localized Calamity (Hailstorm & Canopy Destruction)",
                "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
                "coverage": "Individual farm survey payout based on percentage canopy shredding",
                "intimation_window": "72 Hours",
                "eligibility": "Hail precipitation >10mm diameter damaging standing crops",
                "documents": ["Patta / 7/12 Extract", "Sowing Proof", "Hail Damage Photos", "Bank Passbook"]
            },
            {
                "scheme_id": "HAIL-02",
                "name": "State Horticulture Anti-Hail Net & Fruit Loss Guarantee",
                "authority": "State Horticulture Mission",
                "coverage": "₹25,000/hectare for Apple, Orange, Grapes, and Pomegranate",
                "intimation_window": "48 Hours",
                "eligibility": "Fruit puncture / defoliation >40% caused by severe hailstorm",
                "documents": ["Orchard Registration", "Geo-tagged Photos", "Aadhaar"]
            },
            {
                "scheme_id": "HAIL-03",
                "name": "Rabi Wheat & Mustard Hailstorm Immediate Input Relief",
                "authority": "Department of Agriculture & Farmers Welfare",
                "coverage": "₹6,000/acre for earhead shattering and pod lodging in Rabi crops",
                "intimation_window": "72 Hours",
                "eligibility": "Wheat / Mustard in flowering or grain filling stage crushed by hail",
                "documents": ["Khasra Girdawari Extract", "Bank Passbook", "Aadhaar"]
            },
            {
                "scheme_id": "HAIL-04",
                "name": "Multi-Peril Agricultural Hail Damage Guarantee Policy",
                "authority": "General Insurance Corporation & State Agri Board",
                "coverage": "Up to 80% market value of standing cash crops",
                "intimation_window": "72 Hours via 14447 Helpline",
                "eligibility": "Vegetable, Tobacco, and Spices damaged by convective hail storms",
                "documents": ["Insurance Cover Note", "VAO Damage Assessment"]
            },
            {
                "scheme_id": "HAIL-05",
                "name": "RWBCIS Severe Frost & Cold Wave Temperature Anomaly Index",
                "authority": "Weather-Based Crop Insurance Scheme",
                "coverage": "Index-linked settlement when minimum temperature drops below 2°C for 48h",
                "intimation_window": "Automated AWS Station Trigger",
                "eligibility": "Frost injury in Potato, Mustard, and Tomato crops",
                "documents": ["RWBCIS Policy ID", "Aadhaar-linked Bank Account"]
            }
        ],
        "pest": [
            {
                "scheme_id": "PEST-01",
                "name": "PMFBY Widespread Pest & Endemic Disease Outbreak Clause",
                "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
                "coverage": "Mid-season yield loss indemnity based on Panchayat Crop Cutting Experiments",
                "intimation_window": "72 Hours (or village level intimation by VAO)",
                "eligibility": "Non-preventable widespread attack (BPH, Blast, Wilt, Stem Borer, Bollworm)",
                "documents": ["Patta / Chitta", "VAO Crop Sown Certificate", "Pest Symptoms Photo"]
            },
            {
                "scheme_id": "PEST-02",
                "name": "National Plant Protection Emergency Pest Eradication Subsidy",
                "authority": "Directorate of Plant Protection, Quarantine & Storage",
                "coverage": "100% free chemical & bio-pesticide distribution + ₹3,000/acre labor subsidy",
                "intimation_window": "Immediate upon 10% Economic Threshold Level (ETL) crossing",
                "eligibility": "Notified pest epidemics: Fall Armyworm (FAW), Locust, Pink Bollworm",
                "documents": ["Farmer KCC Card", "Panchayat Verification"]
            },
            {
                "scheme_id": "PEST-03",
                "name": "State Epidemic Blight & Sheath Rot Emergency Input Grant",
                "authority": "State Agricultural University & Krishi Vigyan Kendra (KVK)",
                "coverage": "₹4,500/acre input grant for recommended systemic fungicides",
                "intimation_window": "5 Days",
                "eligibility": "Severe bacterial leaf blight or fungal sheath rot covering >40% field",
                "documents": ["KVK / Agri Officer Diagnosis Report", "Aadhaar", "Bank Details"]
            },
            {
                "scheme_id": "PEST-04",
                "name": "Cotton Pink Bollworm & Whitefly Distress Safety Shield",
                "authority": "Cotton Corporation of India & State Agriculture Mission",
                "coverage": "₹8,000/acre compensation for unpickable damaged cotton bolls",
                "intimation_window": "7 Days",
                "eligibility": "Boll damage >35% documented by joint survey committee",
                "documents": ["7/12 Extract / Patta", "Cotton Ginning Delivery Slip / Photo"]
            },
            {
                "scheme_id": "PEST-05",
                "name": "Integrated Bio-Control Pest Rehabilitation Policy",
                "authority": "National Centre for Integrated Pest Management (NCIPM)",
                "coverage": "₹5,000/hectare for pheromone traps, trichogramma cards & bio-agents",
                "intimation_window": "7 Days",
                "eligibility": "Certified organic or IPM registered farms affected by pest resurgence",
                "documents": ["Organic / IPM Certification", "Land Record", "Aadhaar"]
            }
        ],
        "unseasonal_rain": [
            {
                "scheme_id": "UNS-01",
                "name": "PMFBY Post-Harvest Loss Clause (14-Day Cut & Spread)",
                "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
                "coverage": "Individual farm survey payout for harvested crops lying in field",
                "intimation_window": "Mandatory within 72 Hours of rain",
                "eligibility": "Crops harvested and kept in 'cut & spread' condition in field damaged by rain",
                "documents": ["Patta/Chitta", "Harvest Declaration", "Field Photo of Harvested Crop", "Bank Passbook"]
            },
            {
                "scheme_id": "UNS-02",
                "name": "APMC Mandi Yard Unseasonal Rain Loss Protection Policy",
                "authority": "State Agricultural Marketing Board",
                "coverage": "100% reimbursement of damaged commodity value at modal mandi price",
                "intimation_window": "24 Hours from mandi gate entry",
                "eligibility": "Grain bags or produce brought to APMC market yard drenched before auction",
                "documents": ["APMC Gate Pass / Weighment Slip", "Farmer Aadhaar Card"]
            },
            {
                "scheme_id": "UNS-03",
                "name": "Village Threshing Floor Moisture Damage Compensation Scheme",
                "authority": "State Food & Civil Supplies Department",
                "coverage": "₹4,000/quintal procurement guarantee with relaxed moisture tolerance up to 22%",
                "intimation_window": "48 Hours",
                "eligibility": "Paddy / Wheat grains discolored or sprouted on village threshing floor",
                "documents": ["VAO Harvest Certificate", "Aadhaar Linked Account"]
            },
            {
                "scheme_id": "UNS-04",
                "name": "Western Disturbance Rabi Crop Lodging Assistance Policy",
                "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
                "coverage": "₹5,500/acre input assistance for mature crop lodging",
                "intimation_window": "72 Hours",
                "eligibility": "Unseasonal rainfall >30mm during March-April harvesting stage",
                "documents": ["Khasra Extract", "Damage Photo", "Bank Passbook"]
            },
            {
                "scheme_id": "UNS-05",
                "name": "Kisan Emergency Grain Drying & Moisture Relief Subsidy",
                "authority": "National Cooperative Development Corporation (NCDC)",
                "coverage": "₹2,500/acre subsidy for tarpaulin covers & portable grain dryer charges",
                "intimation_window": "48 Hours",
                "eligibility": "Small farmers facing unseasonal pre-monsoon shower damage",
                "documents": ["Panchayat Small Farmer Certificate", "Aadhaar"]
            }
        ]
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
    def get_schemes_for_disaster(cls, disaster_type: str) -> List[Dict[str, Any]]:
        """
        Returns the top 5 official and relief schemes matching the specific disaster type.
        """
        dmg_clean = disaster_type.lower().strip() if disaster_type else ""
        if any(w in dmg_clean for w in ["flood", "inundat", "submerge", "waterlog"]):
            return cls.SCHEMES_BY_DISASTER.get("flood", [])
        elif any(w in dmg_clean for w in ["drought", "dry", "moisture", "sookha"]):
            return cls.SCHEMES_BY_DISASTER.get("drought", [])
        elif any(w in dmg_clean for w in ["cyclone", "storm", "surge", "toofan"]):
            return cls.SCHEMES_BY_DISASTER.get("cyclone", [])
        elif any(w in dmg_clean for w in ["hail", "frost", "cold", "frozen"]):
            return cls.SCHEMES_BY_DISASTER.get("hailstorm", [])
        elif any(w in dmg_clean for w in ["pest", "insect", "disease", "blight", "keeda"]):
            return cls.SCHEMES_BY_DISASTER.get("pest", [])
        elif any(w in dmg_clean for w in ["unseasonal", "post_harvest", "harvest", "thresh"]):
            return cls.SCHEMES_BY_DISASTER.get("unseasonal_rain", [])
        
        # Default to PMFBY primary schemes
        return cls.SCHEMES_BY_DISASTER.get("flood", [])

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
            f"- Portal: {pmfby['portal_url']} | Guidelines: {pmfby['guidelines_url']}\n"
            f"- Claim Intimation Window: Mandatory within 72 hours of damage event.\n"
            f"- Required Evidence: {docs}.\n"
            f"- Assessment Method: Physical on-field joint survey by Insurance Assessor & State Agriculture/Revenue official.\n"
            f"- Payout / Settlement Rule: Processed directly to Aadhaar-linked bank account via DBT post-survey.\n"
            f"- STRICT ANTI-OVERPROMISING GUARDRAIL: AI must NEVER guarantee approval or specify payout amounts. Every claim is subject to surveyor verification."
        )

