from gedgo.models import Gedcom
from gedgo.forms import UpdateForm
from gedgo.tasks import async_update

from os.path import isfile

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.conf import settings


@login_required
def update_view(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)

	if request.method == 'POST':
		form = UpdateForm(request.POST, request.FILES)
		# check for temp file
		if form.is_valid():

			# Need to distribute-task this
			tmpname = settings.MEDIA_ROOT + 'documents/tmp.ged'
			if isfile(tmpname):
				return redirect('/gedgo/')  # Needs to return a "wait" message.

			tmp = open(tmpname, 'w+')
			tmp.write(request.FILES['gedcom_file'].read())
			tmp.close()

			async_update.delay(g, tmpname)

			# Redirect to the document list after POST
			return redirect('/gedgo/' + str(g.id))  # Needs to return a success message.
		else:
			return redirect('/gedgo/')  # Needs to return an error message.

	else:
		form = UpdateForm()

	# Render list page with the documents and the form
	return render_to_response(
		'gedgo/update.html',
		{'form': form, 'gedcom': g},
		context_instance=RequestContext(request))
