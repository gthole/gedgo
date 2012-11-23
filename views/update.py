from gedgo.models import Gedcom
from celery import task

from django.shortcuts import redirect

@login_required
def update(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)

	if request.method == 'POST':
		form = UpdateForm(request.POST, request.FILES)
		if form.is_valid():

			# Need to distribute-task this
			tmp = open(settings.MEDIA_ROOT + 'documents/tmp.ged','r+')
			tmp.write(request.FILES['gedcom_file'].read())
			tmp.close()

			# Redirect to the document list after POST
			return redirect('/gedgo/' + str(g.id) )
		else:
			return redirect('/gedgo/')
	else:
		form = UpdateForm()

	# Render list page with the documents and the form
	return render_to_response(
		'gedgo/update.html',
		{'form': form, 'gedcom': g},
		context_instance=RequestContext(request)
		
@task()
def cel_task(gedcom, file):
	gedgo.update.update(g, settings.MEDIA_ROOT + 'documents/tmp.ged')