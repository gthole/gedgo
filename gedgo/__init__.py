from django.conf import settings
import redis as Redis

redis = None
if hasattr(settings, 'GEDGO_REDIS_SERVER'):
    try:
        redis = Redis.StrictRedis(host=settings.GEDGO_REDIS_SERVER)
        redis.ping()
    except Exception as e:
        print e
