from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from gedgo.models import Gedcom, Family, Person, BlogPost, Documentary
from gedgo.views.util import render, process_comments
from gedgo.views.visualizations import timeline, json_tree


@login_required
def gedcom(request, gedcom_id):
    g = get_object_or_404(Gedcom, id=gedcom_id)
    post = BlogPost.objects.all().order_by("-created").first()
    noun = g.title or ("Gedcom #%d" % g.id)

    return render(
        request,
        'gedgo/gedcom.html',
        {
            'gedcom': g,
            'post': post,
            'form': process_comments(request, noun)
        }
    )


@login_required
def family(request, family_id, gedcom_id):
    g = get_object_or_404(Gedcom, id=gedcom_id)
    f = get_object_or_404(Family, gedcom=g, pointer=family_id)
    noun = "%s (%s)" % (f.family_name, f.pointer)

    return render(
        request,
        'gedgo/family.html',
        {
            'gedcom': g,
            'family': f,
            'form': process_comments(request, noun)
        }
    )


@login_required
def person(request, gedcom_id, person_id):
    g = get_object_or_404(Gedcom, id=gedcom_id)
    p = get_object_or_404(Person, gedcom=g, pointer=person_id)
    noun = "%s (%s)" % (p.full_name, p.pointer)

    context = {
        'person': p,
        'posts': BlogPost.objects.filter(tagged_people=p),
        'gedcom': g,
        'tree': json_tree(p),
        'form': process_comments(request, noun)
    }
    context['events'], context['hindex'] = timeline(p)

    return render(request, 'gedgo/person.html', context)


@login_required
def documentaries(request):
    documentaries = Documentary.objects.all().order_by('-last_updated')

    return render(
        request,
        "gedgo/documentaries.html",
        {'documentaries': documentaries}
    )
