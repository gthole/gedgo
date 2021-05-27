import os
from django.core.asgi import get_asgi_application
from django_simple_task import django_simple_task_middlware

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

app = get_asgi_application()
application = django_simple_task_middlware(app)
