from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response

from gedgo.models import Gedcom, BlogPost, Person
from gedgo.forms import CommentForm, comment_action
from gedgo.visualizations import timeline, json_tree


@login_required
def person(request, gedcom_id, person_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	p = get_object_or_404(Person, gedcom=g, pointer=person_id)
	posts = BlogPost.objects.filter(tagged_people=p)
	events, hindex = timeline(p)
	ancestral_tree = json_tree(p)

	if request.method == 'POST':
		form = comment_action(request, p.full_name() + ' (' + p.pointer + ')')
		return render_to_response('gedgo/person.html',
			{'person': p, 'posts': posts, 'gedcom': g, 'events': events,
			'hindex': hindex, 'tree': ancestral_tree, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()

	return render_to_response('gedgo/person.html',
		{'person': p, 'posts': posts, 'gedcom': g, 'events': events,
		'hindex': hindex, 'tree': ancestral_tree, 'form': form},
		context_instance=RequestContext(request))
