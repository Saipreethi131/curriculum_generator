"""Curriculum model operations for MongoDB."""

from datetime import datetime
from bson import ObjectId
from database import get_db


class Curriculum:
    collection_name = "curricula"

    @classmethod
    def collection(cls):
        return get_db()[cls.collection_name]

    @classmethod
    def create(cls, user_identifier, program, level, semesters, hours, industry, courses_per_sem, custom_settings, curriculum_data, model, generation_time):
        now = datetime.utcnow()
        doc = {
            "user_identifier": user_identifier,
            "program": program,
            "level": level,
            "semesters": semesters,
            "hours": hours,
            "industry": industry,
            "courses_per_sem": courses_per_sem,
            "custom_settings": custom_settings,
            "curriculum_data": curriculum_data,
            "model": model,
            "generation_time": generation_time,
            "created_at": now,
        }
        result = cls.collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @classmethod
    def list_history(cls, user_identifier, limit=20):
        cursor = cls.collection().find(
            {"user_identifier": user_identifier},
            {
                "program": 1,
                "level": 1,
                "semesters": 1,
                "hours": 1,
                "industry": 1,
                "courses_per_sem": 1,
                "model": 1,
                "generation_time": 1,
                "created_at": 1,
            },
        ).sort("created_at", -1).limit(limit)

        items = []
        for item in cursor:
            item["id"] = str(item.pop("_id"))
            items.append(item)
        return items

    @classmethod
    def get_by_id(cls, curriculum_id, user_identifier):
        try:
            oid = ObjectId(curriculum_id)
        except Exception:
            return None
        doc = cls.collection().find_one({"_id": oid, "user_identifier": user_identifier})
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    def delete_by_id(cls, curriculum_id, user_identifier):
        try:
            oid = ObjectId(curriculum_id)
        except Exception:
            return False
        result = cls.collection().delete_one({"_id": oid, "user_identifier": user_identifier})
        return result.deleted_count > 0
