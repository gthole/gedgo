
from __future__ import absolute_import

from gedgo.gedcom_update import update
from gedgo import redis
from gedgo.models import Gedcom
import os
from celery import Celery
from django.conf import settings
from datetime import datetime
from django.core.mail import send_mail, send_mass_mail
from django.contrib.auth.models import User
import traceback
import requests
import json


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery()
app.config_from_object(settings)


@app.task
def async_update(gedcom_id, file_name, recipient_ids,
                 message, domain, sender_id):
    start = datetime.now()
    gedcom = Gedcom.objects.get(id=gedcom_id)

    errstr = ''
    try:
        update(gedcom, file_name, verbose=False)
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

    # Send mass email to users on successful update only.
    recipients = [User.objects.get(id=id_).email for id_ in recipient_ids]
    recipients = [u for u in recipients if u]

    if (not errstr) and recipients and message:
        scheme = 'https' if settings.CSRF_COOKIE_SECURE else 'http'
        url = '%s://%s/gedgo/%s/' % (scheme, domain, gedcom.id)
        sender = User.objects.get(id=sender_id).email
        subject = 'Update to %s' % gedcom.title
        body = '%s\n\n%s' % (message, url)
        datatuple = ((subject, body, sender, [r]) for r in recipients)

        send_mass_mail(datatuple)


@app.task
def geo_resolve_ip(ip_address):
    if redis is None:
        return
    try:
        response = requests.get('ipinfo.io/%s/json' % ip_address)
        j = response.json()
        j['requested'] = datetime.utcnow().isoformat()
        redis.set('gedgo_ip_%s', json.dumps(j))
    except (requests.exceptions.RequestsException, ValueError):
        return
