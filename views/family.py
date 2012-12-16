from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response

from gedgo.models import Gedcom, Family
from gedgo.forms import CommentForm, comment_action


@login_required
def family(request, family_id, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	f = get_object_or_404(Family, gedcom=g, pointer=family_id)

	if request.method == 'POST':
		form = comment_action(request, f.family_name() + ' (' + f.pointer + ')')
		return render_to_response('gedgo/family.html',
			{'family': f, 'gedcom': g, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()

	return render_to_response('gedgo/family.html',
		{'family': f, 'gedcom': g, 'form': form},
		context_instance=RequestContext(request))
