from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext

from gedgo.models import BlogPost, Documentary
from gedgo.forms import CommentForm


def process_comments(request):
    """
    Returns a tuple of (form, redirect_response) depending on whether a
    new comment has been posted or not.
    """
    if not request.POST:
        return CommentForm(), None

    form = CommentForm(request.POST, request.FILES)
    try:
        assert form.is_valid()
        form.instance.user = request.user
        form.save()

        # Email the comment to the site owners.
        form.email_comment(request)
        messages.success(
            request,
            'Your comment has been sent. Thank you!'
        )
    except Exception as e:
        print e
        messages.error(
            request,
            "We're sorry, we couldn't process your comment."
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
