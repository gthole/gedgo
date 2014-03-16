from gedgo import REDIS
import json
import time
import re

IGNORE_PATTERNS = [
    r'^/gedgo/media/',
    r'^/gedgo/\d+/(?:timeline|pedigree)'
]
IGNORE_PATTERNS = [re.compile(p) for p in IGNORE_PATTERNS]


class SimpleTrackerMiddleware(object):
    """
    Lightweight user page view tracking.
    """

    def process_response(self, request, response):
        # Don't process if REDIS isn't configured or non-200 response
        if REDIS is None or response.status_code != 200:
            return response

        # Only track non-superuser visitors
        if request.user is None or request.user.is_superuser \
                or not request.user.username:
            return response

        for pattern in IGNORE_PATTERNS:
            if pattern.match(request.path_info):
                return response

        # Increment counters and record pageview.
        # This is pretty fast, but could be done in a celery task to reduce
        # per-page overhead.
        id_ = request.user.id
        _increment_key('gedgo_page_view_count')
        _increment_key('gedgo_user_%d_page_view_count' % id_)

        page_view = {
            'ip': request.META['REMOTE_ADDR'],
            'path': request.path_info,
            'time': int(time.time())
        }
        REDIS.lpush('gedgo_user_%d_page_views' % id_, json.dumps(page_view))
        REDIS.ltrim('gedgo_user_%d_page_views' % id_, 0, 100)

        return response


def _increment_key(key_name):
    try:
        pvc = int(REDIS.get(key_name))
    except TypeError:
        pvc = 0
    REDIS.set(key_name, pvc + 1)
