"""Profile model operations for MongoDB."""

from datetime import datetime
from database import get_db


class Profile:
    collection_name = "profiles"

    @classmethod
    def collection(cls):
        return get_db()[cls.collection_name]

    @classmethod
    def list_names(cls, user_identifier):
        cursor = cls.collection().find(
            {"user_identifier": user_identifier},
            {"name": 1, "_id": 0}
        ).sort("name", 1)
        return [item["name"] for item in cursor]

    @classmethod
    def upsert(cls, user_identifier, name, settings):
        now = datetime.utcnow()
        cls.collection().update_one(
            {"user_identifier": user_identifier, "name": name},
            {
                "$set": {
                    "settings": settings,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "created_at": now,
                },
            },
            upsert=True,
        )

    @classmethod
    def get(cls, user_identifier, name):
        return cls.collection().find_one(
            {"user_identifier": user_identifier, "name": name},
            {"settings": 1, "_id": 0}
        )

    @classmethod
    def delete(cls, user_identifier, name):
        result = cls.collection().delete_one({"user_identifier": user_identifier, "name": name})
        return result.deleted_count > 0
