
from __future__ import absolute_import

from gedgo.gedcom_update import update
import os
from celery import Celery
from django.conf import settings
from datetime import datetime
from django.core.mail import send_mail
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery()
app.config_from_object(settings)


@app.task
def async_update(gedcom, file_):
    start = datetime.now()

    errstr = ''
    try:
        update(gedcom, file_)
    except:
        errstr = traceback.format_exc()

    end = datetime.now()

    send_mail(
        'Update finished!',
        'Started:  %s\nFinished: %s\n\n%s' % (
            start.strftime('%B %d, %Y at %I:%M %p'),
            end.strftime('%B %d, %Y at %I:%M %p'),
            errstr
        ),
        'noreply@example.com',
        [settings.SERVER_EMAIL],
    )
