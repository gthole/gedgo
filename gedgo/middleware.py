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
        # TODO: Add user tracking
        return response
