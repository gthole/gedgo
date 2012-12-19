from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response

from gedgo.models import Gedcom, Documentary


@login_required
def documentaries(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	documentaries = Documentary.objects.filter(gedcom=g).order_by('-last_updated')

	return render_to_response("gedgo/documentaries.html",
		{'documentaries': documentaries, 'gedcom': g, 'user': request.user},
		context_instance=RequestContext(request))
