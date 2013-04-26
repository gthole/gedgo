from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from gedgo.models import BlogPost, Documentary
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.shortcuts import redirect
from django.contrib.auth import logout

from os import path

import mimetypes

from django.http import Http404


def site_context(request):
    show_blog = (len(BlogPost.objects.all()) > 0)
    show_documentaries = (len(Documentary.objects.all()) > 0)
    try:
        show_researchfiles = (type(settings.RESEARCH_FILES_ROOT) is str)
    except:
        show_researchfiles = False
    site_title = get_current_site(request).name
    user = request.user

    return {'show_blog': show_blog, 'show_documentaries': show_documentaries,
            'show_researchfiles': show_researchfiles, 'site_title': site_title,
            'user': user}


def serve_content(filename):
    """
    http://djangosnippets.org/snippets/365/
    """
    if not path.exists(filename):
        raise Http404
    wrapper = FileWrapper(file(filename))
    c_type = mimetypes.guess_type(filename)[0]
    response = HttpResponse(wrapper, content_type=c_type)
    response['Content-Length'] = path.getsize(filename)
    if c_type is None:
        response['Content-Disposition'] = "attachment; filename=%s;" % path.basename(filename)
    return response


def logout_view(request):
    logout(request)
    return redirect("/gedgo/")
