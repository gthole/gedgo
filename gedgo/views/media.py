from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.conf import settings
from django.shortcuts import redirect

from gedgo.views.research import can_preview
from gedgo.storages import gedcom_storage, research_storage

import mimetypes
from os import path
import sys
sys.stdout = sys.stderr



STORAGES = {
    'research': research_storage,
    'gedcom': gedcom_storage
}


@login_required
def media(request, storage_name, pathname):
    """
    Authenticated media endpoint - accepts a 'size' parameter that will
    generate previews
    """
    name = pathname.strip('/')

    storage = STORAGES.get(storage_name)
    if not storage:
        raise Http404

    size = request.GET.get('size')
    if size:
        return serve_thumbnail(request, storage_name, storage, size, name)
    else:
        return serve_content(storage, name)


def serve_thumbnail(request, storage_name, storage, size, name):
    if not can_preview(storage, name):
        raise Http404

    if size not in ('w64h64', 'w128h128', 'w640h480', 'w1024h768'):
        raise Http404

    cache_name = path.join('preview-cache', storage_name, size, name)

    try:
        if not default_storage.exists(cache_name):
            print 'generating cache: ' + cache_name
            content = storage.preview(name, size)
            assert content
            default_storage.save(cache_name, content)
        return serve_content(default_storage, cache_name)
    except Exception as e:
        print e
        return HttpResponseRedirect(settings.STATIC_URL + 'img/question.jpg')


def serve_content(storage, name):
    """
    Generate a response to server protected content.
    """
    if not storage.exists(name):
        raise Http404

    # Non-filesystem storages should re-direct to a temporary URL
    if not storage.__class__.__name__ == 'FileSystemStorage':
        return HttpResponseRedirect(storage.url(name))

    # Otherwise we use sendfile
    response = HttpResponse()
    response[settings.GEDGO_SENDFILE_HEADER] = '%s%s' % (
        settings.GEDGO_SENDFILE_PREFIX,
        name
    )

    # Set various file headers and return
    base = path.basename(name)
    response['Content-Type'] = mimetypes.guess_type(base)[0]
    response['Content-Length'] = storage.size(name)
    response['Cache-Control'] = 'public, max-age=31536000'
    if response['Content-Type'] is None:
        response['Content-Disposition'] = "attachment; filename=%s;" % (base)
    return response
