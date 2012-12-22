from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect

from gedgo.models import Gedcom, Person, BlogPost
from gedgo.views.util import site_context

from re import findall


@login_required
def search(request):
	if 'q' in request.GET and request.GET['q']:
		q = request.GET['q']

		g = Gedcom.objects.all()
		if len(g) > 0:
			g = g[0]

		people = Person.objects.all()
		posts = BlogPost.objects.all()

		for term in findall('\w+', q):  # Throw away non-word characters.
			people = people & (Person.objects.filter(last_name__icontains=term) |
								Person.objects.filter(first_name__icontains=term) |
								Person.objects.filter(suffix__icontains=term))
			posts = posts & (BlogPost.objects.filter(title__icontains=term) |
								BlogPost.objects.filter(body__icontains=term))

		if (len(people) == 1) & (len(posts) == 0):
			person = people[0]
			return redirect('/gedgo/' + str(person.gedcom.id) + '/' + person.pointer)

		return render_to_response('gedgo/search_results.html',
			{'people': people, 'gedcom': g, 'posts': posts, 'query': q},
			context_instance=RequestContext(request, site_context(request)))
	else:
		return render_to_response('gedgo/search_results.html',
			{'people': Person.objects.none(), 'gedcom': g, 'posts': BlogPost.objects.none()},
			context_instance=RequestContext(request, site_context(request)))
