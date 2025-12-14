# app/utils/cache.py
import json
from typing import Any
from app.core.redis_client import redis_client


def cache_get(key: str) -> Any:
    """
    Returns cached value if present, else None.
    """
    raw = redis_client.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except:
        return raw


def cache_set(key: str, value: Any, ttl: int = 3600):
    """
    Cache a value with TTL (default: 1 hour).
    """
    redis_client.set(key, json.dumps(value), ex=ttl)
