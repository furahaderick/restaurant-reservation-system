"""Store a short rating in PostgreSQL and long-form feedback in MongoDB."""

from datetime import UTC, datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from restaurant_app.config import get_mongo_settings
from restaurant_app.db import get_connection

_mongo_client = None


def get_feedback_collection():
    global _mongo_client
    settings = get_mongo_settings()
    if _mongo_client is None:
        _mongo_client = MongoClient(
            host=settings["host"],
            port=settings["port"],
            serverSelectionTimeoutMS=2000,
        )
    return _mongo_client[settings["database"]]["feedback"]


def add_review(restaurant_id, customer_id, rating, short_comment, detailed_feedback):
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise ValueError("Rating must be a whole number between 1 and 5.")

    # Save the score and short comment in PostgreSQL for reports.
    with get_connection() as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO reviews (restaurant_id, customer_id, rating, short_comment)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (restaurant_id, customer_id, rating, short_comment),
                )
                review_id = cursor.fetchone()[0]

    # Save the flexible, longer text in MongoDB.
    document = {
        "postgres_review_id": review_id,
        "restaurant_id": restaurant_id,
        "customer_id": customer_id,
        "rating": rating,
        "feedback": detailed_feedback,
        "created_at": datetime.now(UTC),
    }
    try:
        get_feedback_collection().insert_one(document)
    except PyMongoError as error:
        # PostgreSQL review remains saved if MongoDB is unavailable. This is a
        # simple cross-database example, not a distributed transaction.
        print(f"Warning: review saved in PostgreSQL, but MongoDB failed: {error}")

    return review_id
