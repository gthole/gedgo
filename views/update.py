from gedgo.models import Gedcom
from gedgo.forms import UpdateForm
from gedgo.tasks import async_update

from os.path import isfile

from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.conf import settings


@login_required
def update_view(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)

	tmpname = settings.MEDIA_ROOT + 'documents/tmp.ged'
	message = ''

	if isfile(tmpname):
		form = ''
		message = 'This gedcom is currently being updated already.  `Please check back later.'
	elif request.method == 'POST':
		form = UpdateForm(request.POST, request.FILES)
		# check for temp file
		if form.is_valid():

			# TODO: Replace tmp file with a database value setting or dj-celery check,
			# and skip open/write/close cycle, feeding document value in directly.
			# Should have validation of file name, file contents before proceeding.
			tmp = open(tmpname, 'w+')
			tmp.write(request.FILES['gedcom_file'].read())
			tmp.close()

			async_update.delay(g, tmpname)

			# Redirect to the document list after POST
			form = ''
			message = 'Upload successful.  Gedcom updating.'
		else:
			form = UpdateForm()
			message = 'Did you correctly upload a gedcom file?'

	else:
		form = UpdateForm()

	# Render list page with the documents and the form
	return render_to_response(
		'gedgo/update.html',
		{'form': form, 'message': message, 'gedcom': g},
		context_instance=RequestContext(request))
