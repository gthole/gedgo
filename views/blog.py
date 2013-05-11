from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from gedgo.models import BlogPost
from gedgo.forms import CommentForm, comment_action
from gedgo.views.util import site_context

from datetime import datetime


@login_required
def blog(request, year, month):
    "Blog front page - listing posts by creation date."
    posts = BlogPost.objects.all().order_by("-created")

    if year:
        posts = posts & BlogPost.objects.filter(created__year=year)
    if month:
        posts = posts & BlogPost.objects.filter(created__month=month)

    paginator = Paginator(posts, 2)

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)

    months = set(
        (d.year, d.month, datetime(2012, d.month, 1).strftime('%B'))
        for d in BlogPost.objects.values_list('created', flat=True))

    return render_to_response(
        "gedgo/blogpost_list.html",
        {'posts': posts, 'months': months},
        context_instance=RequestContext(request, site_context(request)))


@login_required
def blog_list(request):
    return blog(request, None, None)


@login_required
def blogpost(request, post_id):
    "Single post."
    post = get_object_or_404(BlogPost, id=post_id)

    if request.method == 'POST':
        form = comment_action(request, post.title + ' (blog post comment)')
        return render_to_response(
            'gedgo/blogpost.html',
            {'post': post, 'form': form},
            context_instance=RequestContext(request, site_context(request)))
    else:
        form = CommentForm()

    return render_to_response(
        "gedgo/blogpost.html",
        {'post': post, 'form': form},
        context_instance=RequestContext(request, site_context(request)))
