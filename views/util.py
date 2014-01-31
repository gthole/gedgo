from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext

from gedgo.models import BlogPost, Documentary
from gedgo.forms import CommentForm

from os import path
import mimetypes


@login_required
def media(request, file_base_name):
    """
    Authenticated view to serve media content if necessary
    """
    filename = path.join(settings.MEDIA_ROOT, file_base_name)
    return serve_content(filename)


def process_comments(request, noun):
    if request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            form.email_comment(noun)
            messages.success(
                request,
                'Your comment has ben sent.  Thank you!'
            )
        else:
            messages.error(
                request,
                "We're sorry, your comment was not sent."
            )
    else:
        form = CommentForm()
    return form


def render(request, template, context):
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request, site_context(request))
    )


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
        response['Content-Disposition'] = "attachment; filename=%s;" % (
            path.basename(filename))
    return response


def logout_view(request):
    logout(request)
    return redirect("/gedgo/")
