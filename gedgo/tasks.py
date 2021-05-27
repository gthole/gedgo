from gedgo.gedcom_update import update
from gedgo.models import Gedcom
from django.conf import settings
from datetime import datetime
from django.core.mail import send_mail, send_mass_mail
from django.contrib.auth.models import User
import traceback


def async_update(gedcom_id, file_name, recipient_ids,
                 message, domain, sender_id):
    print('OK!')

    start = datetime.now()
    gedcom = Gedcom.objects.get(id=gedcom_id)

    errstr = ''
    try:
        update(gedcom, file_name, verbose=True)
    except Exception as e:
        print(e)
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

