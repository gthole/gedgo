from gedgo.gedcom_update import update

from celery import task
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
import traceback


@task(name='gedgo.tasks.async_update')
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
