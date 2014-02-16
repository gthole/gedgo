from django.conf import settings
import redis

REDIS = None
if hasattr(settings, 'GEDGO_REDIS_SERVER'):
    REDIS = redis.StrictRedis(host=settings.GEDGO_REDIS_SERVER)
    REDIS.ping()
