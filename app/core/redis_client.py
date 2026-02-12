import redis
from core.config import settings

# Redis connection
redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)