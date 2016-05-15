from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db.models import Q
from django.http import Http404

from gedgo.storages import research_storage
from gedgo.models import Gedcom, Person, BlogPost
from gedgo.views.research import process_file
from gedgo.views.util import render

import os
import re

TERMS_RE = re.compile('\w+')


@login_required
def search(request):
    kind = request.GET.get('kind')
    if kind == 'blog':
        return _blog(request)
    if kind == 'files':
        return _files(request)
    return _people(request)


def _files(request):
    _, files = research_storage.search(request.GET.get('q', ''))
    files = [
        process_file(os.path.dirname(f), os.path.basename(f), False)
        for f in files
    ]
    levels = [('Search: ' + request.GET.get('q', '') + ' ', '')]
    return render(
        request,
        'research.html',
        {
            'directories': [],
            'files': files,
            'levels': levels
        }
    )


def _blog(request):
    raise Http404


def _people(request):
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

        people = Person.objects.all()
        for term in terms:
            people &= Person.objects.filter(
                Q(last_name__icontains=term) |
                Q(first_name__icontains=term) |
                Q(suffix__icontains=term)
            )
            people = people.order_by('-pointer')

        # If there's only a single person, just go directly to the details view
        if people.count() == 1:
            person = people.first()
            return redirect(
                '/gedgo/%d/%s' % (person.gedcom.id, person.pointer)
            )

        context['people'] = people
        context['query'] = q
    return render(
        request,
        'search_results.html',
        context
    )
