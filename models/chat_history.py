"""Chat history model operations for MongoDB."""

from datetime import datetime
from database import get_db


class ChatHistory:
    collection_name = "chat_history"

    @classmethod
    def collection(cls):
        return get_db()[cls.collection_name]

    @classmethod
    def create(cls, user_identifier, message, response, context=None, model=None, generation_time=None, success=True, error_details=None):
        doc = {
            "user_identifier": user_identifier,
            "message": message,
            "response": response,
            "context": context or {},
            "model": model,
            "generation_time": generation_time,
            "success": success,
            "error_details": error_details,
            "created_at": datetime.utcnow(),
        }
        cls.collection().insert_one(doc)
        return doc
