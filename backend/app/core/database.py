import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logger import logger

try:
    import motor.motor_asyncio
    from pymongo.errors import PyMongoError
    HAS_MOTOR = True
except ImportError:
    HAS_MOTOR = False


class Database:
    """
    Asynchronous MongoDB Atlas database with automatic, zero-crash Local JSON storage fallback.
    """
    _mongo_client = None
    _db = None
    _is_connected = False
    _fallback_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "storage",
        "enquiries.json"
    )

    @classmethod
    def _init_local_storage(cls):
        os.makedirs(os.path.dirname(cls._fallback_file), exist_ok=True)
        if not os.path.exists(cls._fallback_file):
            with open(cls._fallback_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    @classmethod
    async def get_db(cls):
        """Initialize or return existing MongoDB client."""
        if cls._db is not None and cls._is_connected:
            return cls._db

        cls._init_local_storage()

        if HAS_MOTOR and settings.MONGODB_URI.strip():
            try:
                cls._mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=4000
                )
                # Ping test
                await cls._mongo_client.admin.command('ping')
                cls._db = cls._mongo_client[settings.MONGODB_DB_NAME]
                cls._is_connected = True
                logger.info("✅ Successfully connected to MongoDB Atlas!")
                return cls._db
            except Exception as e:
                logger.warning(f"⚠️ MongoDB Atlas connection error: {e}. Falling back to persistent local storage.")
                cls._is_connected = False
                cls._db = None

        return None

    @classmethod
    async def get_status(cls) -> Dict[str, Any]:
        """Check database status."""
        db = await cls.get_db()
        return {
            "type": "mongodb_atlas" if (db is not None and cls._is_connected) else "local_json_storage",
            "connected": cls._is_connected,
            "database_name": settings.MONGODB_DB_NAME if cls._is_connected else "local_fallback",
            "atlas_uri_configured": bool(settings.MONGODB_URI.strip())
        }

    # ── CRUD Operations for Farmer Enquiries ──

    @classmethod
    async def save_enquiry(cls, enquiry: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new enquiry from the website."""
        enquiry_record = {
            "id": enquiry.get("id") or str(uuid.uuid4())[:8],
            "farmer_name": enquiry.get("farmer_name", "Farmer"),
            "phone_number": enquiry.get("phone_number", ""),
            "crop": enquiry.get("crop", "Paddy / Rice"),
            "language": enquiry.get("language", "hi-IN"),
            "issue": enquiry.get("issue", "General Farming Query"),
            "call_id": enquiry.get("call_id"),
            "agent_id": enquiry.get("agent_id", 1028),
            "status": enquiry.get("status", "call_initiated"),
            "created_at": enquiry.get("created_at") or datetime.now().isoformat()
        }

        db = await cls.get_db()
        if db is not None and cls._is_connected:
            try:
                await db.enquiries.insert_one(dict(enquiry_record))
                return enquiry_record
            except Exception as e:
                logger.error(f"Error inserting into MongoDB: {e}")

        # Fallback to local storage
        cls._init_local_storage()
        try:
            with open(cls._fallback_file, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = []
                data.insert(0, enquiry_record)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Local storage write error: {e}")

        return enquiry_record

    @classmethod
    async def get_enquiries(
        cls,
        search: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch enquiries list with optional search and status filtering."""
        db = await cls.get_db()
        if db is not None and cls._is_connected:
            try:
                query = {}
                if status and status != "all":
                    query["status"] = status
                if search:
                    regex = {"$regex": search, "$options": "i"}
                    query["$or"] = [
                        {"farmer_name": regex},
                        {"phone_number": regex},
                        {"crop": regex},
                        {"issue": regex}
                    ]

                cursor = db.enquiries.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
                return await cursor.to_list(length=limit)
            except Exception as e:
                logger.error(f"Error reading from MongoDB: {e}")

        # Fallback to local storage
        cls._init_local_storage()
        try:
            with open(cls._fallback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

        if status and status != "all":
            data = [d for d in data if d.get("status") == status]

        if search:
            s = search.lower()
            data = [
                d for d in data
                if s in d.get("farmer_name", "").lower()
                or s in d.get("phone_number", "").lower()
                or s in d.get("crop", "").lower()
                or s in d.get("issue", "").lower()
            ]

        return data[:limit]

    @classmethod
    async def update_enquiry_status(cls, enquiry_id: str, new_status: str) -> bool:
        """Update the status of an enquiry."""
        db = await cls.get_db()
        if db is not None and cls._is_connected:
            try:
                res = await db.enquiries.update_one(
                    {"id": enquiry_id},
                    {"$set": {"status": new_status, "updated_at": datetime.now().isoformat()}}
                )
                return res.modified_count > 0
            except Exception as e:
                logger.error(f"Error updating MongoDB enquiry: {e}")

        # Fallback
        cls._init_local_storage()
        try:
            with open(cls._fallback_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                updated = False
                for item in data:
                    if item.get("id") == enquiry_id:
                        item["status"] = new_status
                        item["updated_at"] = datetime.now().isoformat()
                        updated = True
                        break
                if updated:
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=2)
                    return True
        except Exception as e:
            logger.error(f"Local storage update error: {e}")

        return False

    @classmethod
    async def delete_enquiry(cls, enquiry_id: str) -> bool:
        """Delete an enquiry."""
        db = await cls.get_db()
        if db is not None and cls._is_connected:
            try:
                res = await db.enquiries.delete_one({"id": enquiry_id})
                return res.deleted_count > 0
            except Exception as e:
                logger.error(f"Error deleting from MongoDB: {e}")

        # Fallback
        cls._init_local_storage()
        try:
            with open(cls._fallback_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                new_data = [item for item in data if item.get("id") != enquiry_id]
                if len(new_data) != len(data):
                    f.seek(0)
                    f.truncate()
                    json.dump(new_data, f, indent=2)
                    return True
        except Exception as e:
            logger.error(f"Local storage delete error: {e}")

        return False

    # ── CRUD Operations for Crop Insurance Claims Docket ──
    _claims_fallback_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "storage",
        "claims.json"
    )

    @classmethod
    def _init_claims_storage(cls):
        os.makedirs(os.path.dirname(cls._claims_fallback_file), exist_ok=True)
        if not os.path.exists(cls._claims_fallback_file):
            with open(cls._claims_fallback_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    @classmethod
    async def save_claim(cls, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Save a structured insurance claim intake record."""
        claim_record = {
            "id": claim.get("id") or f"CLM-{int(time.time()*1000)%1000000}",
            "farmer_name": claim.get("farmer_name", "Farmer"),
            "phone_number": claim.get("phone_number", ""),
            "crop": claim.get("crop", "Paddy"),
            "damage_type": claim.get("damage_type", "Flood / Inundation"),
            "affected_acres": claim.get("affected_acres", 2.5),
            "event_date": claim.get("event_date") or datetime.now().strftime("%Y-%m-%d"),
            "location": claim.get("location", "Tamil Nadu"),
            "plausibility_score": claim.get("plausibility_score", 0.88),
            "status": claim.get("status", "pending_surveyor_review"),  # pending_surveyor_review, verified, flagged_mismatch, escalated
            "flags": claim.get("flags", []),
            "evidence_checklist": claim.get("evidence_checklist", [
                {"name": "Patta / Chitta Land Record", "collected": True},
                {"name": "Sowing Certificate", "collected": True},
                {"name": "Aadhaar Card", "collected": True},
                {"name": "Bank Passbook", "collected": True},
                {"name": "Geo-Tagged Damage Photos", "collected": False}
            ]),
            "notes": claim.get("notes", "Auto-logged via Stellar Agri Voice AI claim intake."),
            "created_at": claim.get("created_at") or datetime.now().isoformat()
        }

        db = await cls.get_db()
        if db is not None and cls._is_connected:
            try:
                await db.claims.insert_one(dict(claim_record))
                return claim_record
            except Exception as e:
                logger.error(f"Error inserting claim into MongoDB: {e}")

        # Fallback to local storage
        cls._init_claims_storage()
        try:
            with open(cls._claims_fallback_file, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = []
                data.insert(0, claim_record)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Local storage write error for claim: {e}")

        return claim_record

    @classmethod
    async def get_claims(
        cls,
        search: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch crop insurance claims docket."""
        db = await cls.get_db()
        if db is not None and cls._is_connected:
            try:
                query = {}
                if status and status != "all":
                    query["status"] = status
                if search:
                    regex = {"$regex": search, "$options": "i"}
                    query["$or"] = [
                        {"farmer_name": regex},
                        {"phone_number": regex},
                        {"crop": regex},
                        {"damage_type": regex},
                        {"location": regex}
                    ]
                cursor = db.claims.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
                return await cursor.to_list(length=limit)
            except Exception as e:
                logger.error(f"Error reading claims from MongoDB: {e}")

        # Fallback
        cls._init_claims_storage()
        try:
            with open(cls._claims_fallback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

        if status and status != "all":
            data = [d for d in data if d.get("status") == status]

        if search:
            s = search.lower()
            data = [
                d for d in data
                if s in d.get("farmer_name", "").lower()
                or s in d.get("phone_number", "").lower()
                or s in d.get("crop", "").lower()
                or s in d.get("damage_type", "").lower()
                or s in d.get("location", "").lower()
            ]

        return data[:limit]

    @classmethod
    async def update_claim_status(cls, claim_id: str, new_status: str, notes: Optional[str] = None) -> bool:
        """Update claim resolution/escalation status."""
        update_fields: Dict[str, Any] = {"status": new_status, "updated_at": datetime.now().isoformat()}
        if notes:
            update_fields["notes"] = notes

        db = await cls.get_db()
        if db is not None and cls._is_connected:
            try:
                res = await db.claims.update_one({"id": claim_id}, {"$set": update_fields})
                return res.modified_count > 0
            except Exception as e:
                logger.error(f"Error updating MongoDB claim: {e}")

        # Fallback
        cls._init_claims_storage()
        try:
            with open(cls._claims_fallback_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                updated = False
                for item in data:
                    if item.get("id") == claim_id:
                        item["status"] = new_status
                        if notes:
                            item["notes"] = notes
                        item["updated_at"] = datetime.now().isoformat()
                        updated = True
                        break
                if updated:
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=2)
                    return True
        except Exception as e:
            logger.error(f"Local storage update error for claim: {e}")

        return False
