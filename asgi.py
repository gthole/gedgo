import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings
from django.core.asgi import get_asgi_application
from django_simple_task import django_simple_task_middlware
from asgi_middleware_static_file import ASGIMiddlewareStaticFile

app = get_asgi_application()
app = ASGIMiddlewareStaticFile(
    app,
    static_url=settings.STATIC_URL,
    static_root_paths=[settings.STATIC_ROOT]
)
application = django_simple_task_middlware(app)
