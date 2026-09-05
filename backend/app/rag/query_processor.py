import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from difflib import get_close_matches


@dataclass
class QueryResult:
    original_query: str
    normalized_query: str
    intent: str
    confidence: float
    entities: Dict
    retrieval_queries: List[str]
    advisory_topics: List[str]
    dataset_filters: List[str]


class QueryProcessor:

    # ==========================================================
    # Crop Names
    # ==========================================================

    CROP_ALIASES = {

        "rice": [
            "rice",
            "paddy",
            "dhaan",
            "paddy crop",
            "nel"
        ],

        "wheat": [
            "wheat",
            "gehun"
        ],

        "maize": [
            "maize",
            "corn",
            "makka"
        ],

        "cotton": [
            "cotton"
        ],

        "tomato": [
            "tomato"
        ],

        "potato": [
            "potato"
        ],

        "banana": [
            "banana"
        ],

        "mango": [
            "mango"
        ],

        "onion": [
            "onion"
        ],

        "chilli": [
            "chilli",
            "chili",
            "mirchi"
        ],

        "soybean": [
            "soybean",
            "soya"
        ],

        "groundnut": [
            "groundnut",
            "peanut"
        ],

        "millet": [
            "millet",
            "millets"
        ],

        "barley": [
            "barley"
        ],

        "coffee": [
            "coffee"
        ],

        "tea": [
            "tea"
        ],

        "sugarcane": [
            "sugarcane",
            "cane"
        ]
    }

    # ==========================================================
    # Growth Stages
    # ==========================================================

    GROWTH_STAGES = {

        "land preparation": [
            "land preparation",
            "field preparation",
            "prepare land",
            "prepare field",
            "plough",
            "ploughing",
            "plowing"
        ],

        "seed treatment": [
            "seed treatment",
            "treat seed"
        ],

        "nursery": [
            "nursery",
            "seedling",
            "seedlings"
        ],

        "sowing": [
            "sowing",
            "sow",
            "seed sowing"
        ],

        "transplanting": [
            "transplant",
            "transplanting"
        ],

        "vegetative": [
            "vegetative",
            "vegetative stage",
            "growth stage"
        ],

        "tillering": [
            "tillering"
        ],

        "flowering": [
            "flower",
            "flowers",
            "flowering",
            "bloom",
            "blooming"
        ],

        "fruiting": [
            "fruit",
            "fruiting"
        ],

        "grain filling": [
            "grain filling"
        ],

        "harvest": [
            "harvest",
            "harvesting"
        ]
    }

    # ==========================================================
    # Synonyms
    # ==========================================================

    SYNONYMS = {

        # Nutrient Names

        "nitrogen": "N",
        "nitrogen level": "N",

        "phosphorus": "P",
        "phosphorous": "P",
        "phosporous": "P",
        "phosphate": "P",

        "potassium": "K",
        "potash": "K",

        # Weather

        "temp": "temperature",
        "heat": "temperature",

        # Water

        "watering": "irrigation",
        "watering schedule": "irrigation",

        # Pests

        "bug": "pest",
        "bugs": "pest",

        "worm": "pest",
        "worms": "pest",

        "insect": "pest",
        "insects": "pest",

        "hopper": "pest",

        # Disease

        "yellowing": "yellow",

        # General

        "plant": "crop",
        "cultivate": "grow"
    }

    # ==========================================================
    # Intent Keywords
    # ==========================================================

    INTENTS = {

        "crop_recommendation": [
            "recommend",
            "suggest",
            "grow",
            "crop",
            "cultivate"
        ],

        "fertilizer":[
            "fertilizer",
            "urea",
            "dap",
            "npk",
            "potash",
            "compost",
            "vermicompost",
            "farmyard manure",
            "biofertilizer",
            "zinc",
            "boron",
            "micronutrient"
        ],

        "pest_control": [
            "pest",
            "borer",
            "locust",
            "hopper"
        ],

        "disease": [
            "yellow",
            "spot",
            "spots",
            "fungus",
            "blight",
            "rot",
            "powder",
            "wilt",
            "disease"
        ],

        "insurance_claim": [
            "insurance",
            "pmfby",
            "bima",
            "fasal bima",
            "claim",
            "compensation",
            "damage",
            "loss",
            "flood",
            "cyclone",
            "drought",
            "hailstorm",
            "surveyor",
            "patta",
            "chitta"
        ],

        "pest_words": {
            "aphid",
            "whitefly",
            "thrips",
            "mite",
            "armyworm",
            "borer",
            "hopper",
            "bug",
            "bugs",
            "worm",
            "worms",
            "insect",
            "insects"
        },

        "weather": [
            "temperature",
            "humidity",
            "rain",
            "rainfall",
            "weather"
        ],

        "irrigation": [
            "irrigation",
            "water"
        ],

        "yield": [
            "yield",
            "production"
        ],

        "harvest": [
            "harvest",
            "harvesting"
        ],

        "management": [
            "management",
            "cultivation",
            "practice",
            "stage",
            "flowering",
            "vegetative",
            "transplant",
            "nursery",
            "sowing",
            "land preparation",
            "irrigation schedule"
        ],

        "market": [
            "market",
            "price",
            "prices",
            "rate",
            "rates",
            "cost",
            "mandi",
            "sell",
            "selling",
            "value"
        ]
    }

    # ==========================================================
    # Dataset Mapping
    # ==========================================================

    DATASET_MAP = {

        "crop_recommendation": [
            "crop",
            "fertilizer",
            "management"
        ],

        "fertilizer": [
            "fertilizer",
            "crop",
            "management"
        ],

        "pest_control": [
            "pest",
            "disease",
            "management"
        ],

        "disease": [
            "disease",
            "pest",
            "management"
        ],

        "weather": [],

        "irrigation": [
            "management"
        ],

        "harvest": [
            "management"
        ],

        "yield": [
            "management",
            "crop",
            "fertilizer"
        ]
    }

    # ==========================================================
    # Advisory Topics
    # ==========================================================

    ADVISORY = {

        "crop_recommendation": [
            "soil",
            "weather",
            "fertilizer",
            "irrigation",
            "yield",
            "disease",
            "pests"
        ],

        "fertilizer": [
            "dosage",
            "application",
            "watering"
        ],

        "pest_control": [
            "pesticide",
            "prevention",
            "fertilizer",
            "weather"
        ],

        "disease": [
            "treatment",
            "prevention",
            "watering",
            "fertilizer"
        ],

        "weather": [
            "crop",
            "irrigation"
        ],

        "yield": [
            "fertilizer",
            "weather",
            "irrigation"
        ]
    }
    # ==========================================================
    # Normalize Query
    # ==========================================================

    @classmethod
    def normalize(cls, question: str) -> str:

        text = question.lower().strip()

        # Remove punctuation except = . :
        text = re.sub(r"[^\w\s=:.]", " ", text)

        text = re.sub(r"\s+", " ", text)

        # Replace synonyms
        for key, value in cls.SYNONYMS.items():
            text = re.sub(
                rf"\b{re.escape(key)}\b",
                value.lower(),
                text
            )

        return text


    # ==========================================================
    # Crop Detection
    # ==========================================================

    @classmethod
    def detect_crop(cls, text: str):

        for crop, aliases in cls.CROP_ALIASES.items():

            for alias in aliases:

                if re.search(rf"\b{re.escape(alias)}\b", text):

                    return crop

        return None
    
    @classmethod
    def detect_growth_stages(cls, text):

        detected = []

        for stage, aliases in cls.GROWTH_STAGES.items():
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", text):
                    detected.append(stage)
                    break

        return list(dict.fromkeys(detected))

    # ==========================================================
    # Numeric Extraction
    # ==========================================================

    @staticmethod
    def extract_number(text, label):

        patterns = [

            rf"{label}\s*[:=]?\s*(\d+\.?\d*)",

            rf"{label}\s+(\d+\.?\d*)"

        ]

        for pattern in patterns:

            match = re.search(pattern, text)

            if match:

                return float(match.group(1))

        return None


    # ==========================================================
    # Symptom Detection
    # ==========================================================

    @staticmethod
    def detect_symptoms(text):

        symptoms = [

            "yellow",
            "yellowing",

            "spot",
            "spots",

            "blight",

            "rot",

            "powder",

            "powdery",

            "wilt",
            "wilting",

            "curl",
            "curling",

            "mosaic",

            "necrosis",

            "lesion",
            "lesions",

            "leaf burn",

            "dry",

            "drying",

            "borer",

            "hopper",

            "armyworm",

            "aphid",

            "whitefly",

            "thrips",

            "mite",

            "bug",

            "bugs",

            "worm",

            "worms",

            "insect",

            "insects"
        ]

        found = []

        for symptom in symptoms:

            if re.search(rf"\b{re.escape(symptom)}\b", text):

                found.append(symptom)

        return list(set(found))


    STATES = [
        "tamil nadu", "kerala", "karnataka", "andhra pradesh", "telangana",
        "maharashtra", "punjab", "haryana", "uttar pradesh", "bihar",
        "west bengal", "gujarat", "rajasthan", "madhya pradesh", "odisha",
        "assam", "delhi", "chhattisgarh", "jharkhand", "uttarakhand", "himachal pradesh"
    ]

    @classmethod
    def detect_location(cls, text: str):
        for state in cls.STATES:
            if re.search(rf"\b{re.escape(state)}\b", text):
                return state.title()
        match = re.search(r"\b(?:in|at|for)\s+([a-zA-Z\s]+)", text)
        if match:
            candidate = match.group(1).strip()
            if candidate and candidate not in cls.CROP_ALIASES and candidate not in ["rice", "wheat", "maize", "cotton"]:
                return candidate.title()
        return None

    # ==========================================================
    # Entity Extraction
    # ==========================================================

    @classmethod
    def extract_entities(cls, text):

        location = cls.detect_location(text)

        entities = {

            "crop": cls.detect_crop(text),
            "location": location,
            "state": location,
            "growth_stage": cls.detect_growth_stages(text),
            "N": cls.extract_number(text, "n"),
            "P": cls.extract_number(text, "p"),
            "K": cls.extract_number(text, "k"),
            "temperature": cls.extract_number(text, "temperature"),
            "humidity": cls.extract_number(text, "humidity"),
            "ph": cls.extract_number(text, "ph"),
            "rainfall": cls.extract_number(text, "rainfall"),
            "symptoms": cls.detect_symptoms(text)
        }

        return entities

    # ==========================================================
    # Intent Detection
    # ==========================================================

    @classmethod
    def detect_intent(cls, text: str, entities: Dict):

        scores = {}

        for intent, keywords in cls.INTENTS.items():

            if isinstance(keywords, set):
                continue

            score = 0

            for keyword in keywords:

                if re.search(rf"\b{re.escape(keyword)}\b", text):
                    score += 1

            scores[intent] = score

        # Explicit fertilizer keywords boost fertilizer intent
        fertilizer_keywords = [
            "fertilizer",
            "fertilizers",
            "fertilize",
            "urea",
            "dap",
            "npk",
            "potash",
            "compost",
            "vermicompost",
            "manure",
            "biofertilizer",
            "micronutrient",
            "nutrient",
            "nutrients"
        ]

        if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in fertilizer_keywords):
            scores["fertilizer"] += 4

        # Explicit market/price keywords boost market intent
        market_keywords = [
            "market",
            "price",
            "prices",
            "rate",
            "rates",
            "cost",
            "mandi",
            "sell",
            "selling"
        ]

        if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in market_keywords):
            scores["market"] = scores.get("market", 0) + 4

        # NPK values strongly indicate crop recommendation if fertilizer is not explicitly asked
        if (
            entities["N"] is not None and
            entities["P"] is not None and
            entities["K"] is not None
        ):
            if scores["fertilizer"] <= 1:
                scores["crop_recommendation"] += 5
            else:
                scores["fertilizer"] += 2

        # Crop + symptoms usually indicate pest/disease
        if entities["crop"] and entities["symptoms"]:

            disease_words = {
                "yellow",
                "yellowing",
                "spot",
                "spots",
                "blight",
                "rot",
                "powder",
                "powdery",
                "wilt",
                "wilting",
                "curl",
                "curling",
                "mosaic",
                "necrosis",
                "lesion",
                "lesions"
            }

            pest_words = cls.INTENTS["pest_words"]

            if any(symptom in disease_words for symptom in entities["symptoms"]):
                scores["disease"] += 4
            elif any(symptom in pest_words for symptom in entities["symptoms"]):
                scores["pest_control"] += 4

        best_intent = max(scores, key=scores.get)

        total = sum(scores.values())

        confidence = (
            scores[best_intent] / total
            if total > 0 else 0.50
        )

        return best_intent, round(confidence, 2)


    # ==========================================================
    # Retrieval Query Builder
    # ==========================================================

    @classmethod
    def build_retrieval_queries(
        cls,
        text: str,
        entities: Dict,
        intent: str
    ):

        queries = []

        crop = entities.get("crop")
        crop_aliases = []
        if crop and crop in cls.CROP_ALIASES:
            crop_aliases = cls.CROP_ALIASES[crop]
        elif crop:
            crop_aliases = [crop]

        # ---------- Crop Recommendation ----------

        if (
            entities["N"] is not None and
            entities["P"] is not None and
            entities["K"] is not None
        ):

            queries.append(
                f"N {int(entities['N'])} "
                f"P {int(entities['P'])} "
                f"K {int(entities['K'])}"
            )

        # ---------- Crop and Aliases ----------

        for alias in crop_aliases:
            queries.append(alias)

        # ---------- Crop Aliases + Intent Combinations ----------

        if crop_aliases:
            intent_term = intent.replace("_", " ")
            for alias in crop_aliases[:3]:
                queries.append(f"{alias} {intent_term}")
                if intent == "fertilizer" or "fertilizer" in text:
                    queries.append(f"{alias} fertilizer")

        # ---------- Crop + Symptoms ----------

        if crop_aliases and entities.get("symptoms"):

            for alias in crop_aliases[:2]:
                for symptom in entities["symptoms"]:
                    queries.append(
                        f"{alias} {symptom}"
                    )

        # ---------- Crop + Growth Stage ----------

        if crop_aliases and entities.get("growth_stage"):

            for alias in crop_aliases[:2]:
                for stage in entities["growth_stage"]:
                    queries.append(
                        f"{alias} {stage}"
                    )
                    queries.append(
                        f"{alias} {stage} management"
                    )

        # ---------- Weather ----------

        if entities["temperature"] is not None:
            queries.append(
                f"temperature {entities['temperature']}"
            )

        if entities["humidity"] is not None:
            queries.append(
                f"humidity {entities['humidity']}"
            )

        if entities["rainfall"] is not None:
            queries.append(
                f"rainfall {entities['rainfall']}"
            )

        # ---------- Generic Intent ----------

        queries.append(
            intent.replace("_", " ")
        )

        # Remove duplicates while preserving order
        queries = list(dict.fromkeys(queries))

        return queries

    # ==========================================================
    # Main Processing Function
    # ==========================================================

    @classmethod
    def process(cls, question: str) -> QueryResult:

        normalized = cls.normalize(question)

        entities = cls.extract_entities(normalized)

        intent, confidence = cls.detect_intent(
            normalized,
            entities
        )

        retrieval_queries = cls.build_retrieval_queries(
            normalized,
            entities,
            intent
        )

        advisory_topics = cls.ADVISORY.get(intent, [])

        dataset_filters = cls.DATASET_MAP.get(intent, [])

        return QueryResult(

            original_query=question,

            normalized_query=normalized,

            intent=intent,

            confidence=confidence,

            entities=entities,

            retrieval_queries=retrieval_queries,

            advisory_topics=advisory_topics,

            dataset_filters=dataset_filters
        )