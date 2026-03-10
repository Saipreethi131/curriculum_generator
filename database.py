"""MongoDB setup and helpers for the curriculum generator."""

import os
from flask_pymongo import PyMongo
from pymongo import ASCENDING

mongo = PyMongo()


def init_db(app):
    """Initialize MongoDB and create required indexes."""
    app.config.setdefault("MONGO_URI", os.environ.get("MONGO_URI", "mongodb://localhost:27017/curriculum_generator"))
    mongo.init_app(app)

    # Best-effort index creation. If DB is unavailable at startup,
    # route-level operations will still surface meaningful errors.
    try:
        db = mongo.db
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.profiles.create_index([("user_identifier", ASCENDING), ("name", ASCENDING)], unique=True)
        db.curricula.create_index([("user_identifier", ASCENDING), ("created_at", ASCENDING)])
        db.chat_history.create_index([("user_identifier", ASCENDING), ("created_at", ASCENDING)])
    except Exception as exc:
        print(f"Warning: MongoDB index setup failed: {exc}")


def get_db():
    """Get active MongoDB database handle."""
    return mongo.db
