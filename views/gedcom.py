from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response

from gedgo.models import Gedcom, BlogPost
from gedgo.forms import CommentForm, comment_action
from gedgo.views.util import site_context


@login_required
def gedcom(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	post = BlogPost.objects.all().order_by("-created")
	if post:
		post = post[0]

	if request.method == 'POST':
		form = comment_action(request, 'Gedcom #' + str(g.id))
		return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form},
			context_instance=RequestContext(request, site_context(request)))
	else:
		form = CommentForm()

	return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form},
		context_instance=RequestContext(request, site_context(request)))
