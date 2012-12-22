from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from gedgo.models import Documentary
from gedgo.views.util import site_context


@login_required
def documentaries(request):
	dv = site_context(request)
	dv['documentaries'] = Documentary.objects.all().order_by('-last_updated')

	return render_to_response("gedgo/documentaries.html", dv,
		context_instance=RequestContext(request))
