from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext

from gedgo.models import BlogPost, Documentary
from gedgo.forms import CommentForm

def process_comments(request, noun):
    """
    Returns a tuple of (form, redirect_response) depending on whether a
    new comment has been posted or not.
    """
    if not request.POST:
        return CommentForm(), None

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
        getattr(settings, 'GEDGO_RESEARCH_FILE_ROOT', None),
        basestring
    )
    show_file_uploads = getattr(
        settings, 'GEDGO_ALLOW_FILE_UPLOADS', True) is True
    site_title = settings.GEDGO_SITE_TITLE
    user = request.user

    return {
        'show_blog': show_blog,
        'show_documentaries': show_documentaries,
        'show_researchfiles': show_researchfiles,
        'show_file_uploads': show_file_uploads,
        'site_title': site_title,
        'user': user
    }


def logout_view(request):
    logout(request)
    return redirect("/gedgo/")
