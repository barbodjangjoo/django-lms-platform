import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=getattr(settings, "REDIS_HOST", "redis"),
    port=getattr(settings, "REDIS_PORT", 6379),
    db=1, 
    decode_responses=True
)
