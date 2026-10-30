"""Read application settings from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


def get_database_settings():
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", "restaurant_db"),
        "user": os.getenv("POSTGRES_USER", "restaurant_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "restaurant_password"),
    }


def get_redis_url():
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    return f"redis://{host}:{port}/0"


def get_mongo_settings():
    return {
        "host": os.getenv("MONGO_HOST", "localhost"),
        "port": int(os.getenv("MONGO_PORT", "27017")),
        "database": os.getenv("MONGO_DB", "restaurant_feedback"),
    }
