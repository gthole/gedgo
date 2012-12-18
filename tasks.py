from gedgo.update import update

from celery import task

from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail

from os import remove


@task(name='gedgo.tasks.async_update')
def async_update(gedcom, target):
	start = datetime.now()
	errstr = ''
	try:
		update(gedcom, target)
	except Exception as e:
		errstr = 'There was an error!\n' + e.strerror
	remove(target)  # Delete temporary file.
	end = datetime.now()
	send_mail(
			'Update finished!',
			'Started:  ' + start.strftime('%B %d, %Y at %I:%M %p') + '\n' +
			'Finished: ' + end.strftime('%B %d, %Y at %I:%M %p') + '\n\n' +
			errstr,
			'noreply@example.com',
			[settings.SERVER_EMAIL],
		)
