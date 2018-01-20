from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from gedgo.views.research import process_file
from gedgo.models import Gedcom, Person, BlogPost, Documentary, Document
from gedgo.views.util import render, process_comments


@login_required
def gedcom(request, gedcom_id):
    g = get_object_or_404(Gedcom, id=gedcom_id)
    post = BlogPost.objects.all().order_by("-created").first()

    form, redirect = process_comments(request)
    if redirect is not None:
        return redirect

    return render(
        request,
        'gedcom.html',
        {
            'gedcom': g,
            'post': post,
            'form': form,
            'comment_noun': str(g)
        }
    )


@login_required
def person(request, gedcom_id, person_id):
    g = get_object_or_404(Gedcom, id=gedcom_id)
    p = get_object_or_404(Person, gedcom=g, pointer=person_id)

    form, redirect = process_comments(request)
    if redirect is not None:
        return redirect

    context = {
        'person': p,
        'posts': BlogPost.objects.filter(tagged_people=p),
        'photos': [photo for photo in p.photos if not photo.id == p.key_photo.id],
        'gedcom': g,
        'form': form,
        'comment_noun': str(p)
    }

    return render(request, 'person.html', context)


@login_required
def documentaries(request):
    documentaries = Documentary.objects.all().order_by('-last_updated')

    return render(
        request,
        "documentaries.html",
        {'documentaries': documentaries}
    )


@login_required
def documentary_by_id(request, title):
    documentary = get_object_or_404(Documentary, title=title)

    return render(
        request,
        "documentary_by_id.html",
        {
            'documentary': documentary,
            'can_video': documentary.location.lower().endswith('m4v')
        }
    )


@login_required
def document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    context = {
        'doc': doc,
        'file': process_file('', doc.docfile.name, False)
    }

    return render(request, 'document_preview.html', context)
