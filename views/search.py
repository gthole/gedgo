from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db.models import Q

from gedgo.models import Gedcom, Person, BlogPost
from gedgo.views.util import render

import re

TERMS_RE = re.compile('\w+')


@login_required
def search(request):
    g = Gedcom.objects.first()
    context = {
        'people': Person.objects.none(),
        'gedcom': g,
        'posts': BlogPost.objects.none()
    }

    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']

        # Throw away non-word characters.
        terms = TERMS_RE.findall(q)

        for term in terms:
            people = Person.objects.filter(
                Q(last_name__icontains=term) |
                Q(first_name__icontains=term) |
                Q(suffix__icontains=term)
            )
            posts = BlogPost.objects.filter(
                Q(title__icontains=term) |
                Q(body__icontains=term)
            )

        # If there's only a single person, just go directly to the details view
        if people.count() == 1 and not posts.exists():
            person = people.first()
            return redirect(
                '/gedgo/%d/%s' % (person.gedcom.id, person.pointer)
            )

        context['people'] = people
        context['posts'] = posts
        context['query'] = q
    return render(
        request,
        'search_results.html',
        context
    )
