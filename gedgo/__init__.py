from django.conf import settings
import redis as Redis

redis = None
if hasattr(settings, 'GEDGO_REDIS_SERVER'):
    redis = Redis.StrictRedis(host=settings.GEDGO_REDIS_SERVER)
    redis.ping()
