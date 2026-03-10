"""User model operations for MongoDB."""

from datetime import datetime
from bson import ObjectId
from database import get_db


class User:
    collection_name = "users"

    @classmethod
    def collection(cls):
        return get_db()[cls.collection_name]

    @classmethod
    def create(cls, username, email, password_hash=None):
        now = datetime.utcnow()
        doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": now,
            "updated_at": now,
        }
        result = cls.collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @classmethod
    def get_by_id(cls, user_id):
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        return cls.collection().find_one({"_id": oid})

    @classmethod
    def get_by_email(cls, email):
        return cls.collection().find_one({"email": email})
