
from __future__ import absolute_import

from gedgo.gedcom_update import update
from gedgo import REDIS
import os
from celery import Celery
from django.conf import settings
from datetime import datetime
from django.core.mail import send_mail
import traceback
import requests
import json


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery()
app.config_from_object(settings)


@app.task
def async_update(gedcom, file_name):
    start = datetime.now()

    errstr = ''
    try:
        update(gedcom, file_name)
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
        [email for _, email in settings.ADMINS]
    )


@app.task
def geo_resolve_ip(ip_address):
    if REDIS is None:
        return
    try:
        response = requests.get('ipinfo.io/%s/json' % ip_address)
        j = response.json()
        j['requested'] = datetime.utcnow().isoformat()
        REDIS.set('gedgo_ip_%s', json.dumps(j))
    except (requests.exceptions.RequestsException, ValueError):
        return
