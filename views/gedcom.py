from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response

from gedgo.models import Gedcom, BlogPost
from gedgo.forms import CommentForm, comment_action, UpdateForm

from django.conf import settings

import gedgo.update


@login_required
def gedcom(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	post = BlogPost.objects.all().order_by("-created")
	if post:
		post = post[0]

	if request.method == 'POST':
		form = comment_action(request, 'Gedcom #' + str(g.id))
		return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()

	return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form},
		context_instance=RequestContext(request))


@login_required
def update(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)

	if request.method == 'POST':
		form = UpdateForm(request.POST, request.FILES)
		if form.is_valid():

			# Need to distribute-task this
			tmp = open(settings.MEDIA_ROOT + 'documents/tmp.ged', 'r+')
			tmp.write(request.FILES['gedcom_file'].read())
			tmp.close()
			gedgo.update.update(g, settings.MEDIA_ROOT + 'documents/tmp.ged')

			# Redirect to the document list after POST
			return redirect('/gedgo/' + str(g.id) + '/I66')
		else:
			return redirect('/gedgo/1/I68')
	else:
		form = UpdateForm()

	# Render list page with the documents and the form
	return render_to_response(
		'gedgo/update.html',
		{'form': form, 'gedcom': g},
		context_instance=RequestContext(request)
	)
