"""Small Redis cache for table availability."""

import json

import redis

from restaurant_app.config import get_redis_url

_client = None


def get_redis():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(get_redis_url(), decode_responses=True)
    return _client


def make_availability_key(restaurant_id, starts_at, ends_at, party_size):
    # Keep the key readable so it is easy to inspect with redis-cli.
    return (
        f"availability:{restaurant_id}:{starts_at.isoformat()}:"
        f"{ends_at.isoformat()}:{party_size}"
    )


def get_cached_availability(key):
    try:
        value = get_redis().get(key)
        if value is None:
            return None
        return json.loads(value)
    except redis.RedisError:
        # Redis is an optional speed-up; PostgreSQL remains the source of truth.
        return None


def cache_availability(key, tables):
    try:
        get_redis().setex(key, 60, json.dumps(tables))
    except redis.RedisError:
        # Continue to work when Redis is temporarily unavailable.
        pass


def clear_availability_cache(restaurant_id):
    """Clear availability keys after a booking to avoid stale search results."""
    try:
        client = get_redis()
        for key in client.scan_iter(f"availability:{restaurant_id}:*"):
            client.delete(key)
    except redis.RedisError:
        pass
