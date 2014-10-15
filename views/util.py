from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.core.files.storage import default_storage
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
    Authenticated view to serve media content if necessary,
    it's much better to have a webserver handle this through
    an authenticated proxy
    """
    filename = path.join(settings.MEDIA_ROOT, file_base_name.strip('/'))
    return serve_content(filename)


def process_comments(request, noun):
    """
    Returns a tuple of (form, redirect_response) depending on whether a
    new comment has been posted or not.
    """
    if request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            # Store file uploads
            file_names = []
            if getattr(settings, 'GEDGO_ALLOW_FILE_UPLOADS', True) is True:
                for file_ in request.FILES.getlist('uploads'):
                    upload_path = 'uploaded/%s/%s/%s' % (
                        request.user.username,
                        request.path.strip('/').replace('gedgo/', ''),
                        file_.name
                    )
                    default_storage.save(upload_path, file_)
                    file_names.append(upload_path)
            # Email the comment to the site owners.
            form.email_comment(request.user, noun, file_names)
            messages.success(
                request,
                'Your comment has ben sent.  Thank you!'
            )
        else:
            # Shouldn't happen, since there's almost no server-side validation
            messages.error(
                request,
                "We're sorry, your comment was not sent."
            )
        return None, redirect(request.path)
    else:
        form = CommentForm()
    return form, None


def render(request, template, context):
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request, site_context(request))
    )


def site_context(request):
    """
    Update context with constants and settings applicable across multiple
    templates without allowing `settings` directly in the template rendering.
    This should probably live as a middleware layer instead.
    """
    show_blog = BlogPost.objects.exists()
    show_documentaries = Documentary.objects.exists()
    show_researchfiles = isinstance(
        getattr(settings, 'RESEARCH_FILES_ROOT', None),
        basestring
    )
    show_file_uploads = getattr(
        settings, 'GEDGO_ALLOW_FILE_UPLOADS', True) is True
    site_title = get_current_site(request).name
    user = request.user

    return {
        'show_blog': show_blog,
        'show_documentaries': show_documentaries,
        'show_researchfiles': show_researchfiles,
        'show_file_uploads': show_file_uploads,
        'site_title': site_title,
        'user': user
    }


def serve_content(filename):
    """
    Generate a response to server protected content.
    http://djangosnippets.org/snippets/365/
    http://www.chicagodjango.com/blog/permission-based-file-serving/
    """
    if not path.exists(filename):
        raise Http404
    media_server = getattr(settings, 'GEDGO_MEDIA_SERVER', '').lower()
    if media_server == 'apache':
        response = HttpResponse()
        response['X-Sendfile'] = filename
    elif media_server == 'nginx':
        response = HttpResponse()
        response['X-Accel-Redirect'] = filename
    else:
        wrapper = FileWrapper(file(filename))
        response = HttpResponse(wrapper)
    file_type = mimetypes.guess_type(filename)[0]
    response['Content-Type'] = file_type
    response['Content-Length'] = path.getsize(filename)
    if file_type is None:
        response['Content-Disposition'] = "attachment; filename=%s;" % (
            path.basename(filename))
    return response


def logout_view(request):
    logout(request)
    return redirect("/gedgo/")
