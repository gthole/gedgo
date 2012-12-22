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

	months = month_list()

	return render_to_response("gedgo/blogpost_list.html",
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
		return render_to_response('gedgo/blogpost.html',
			{'post': post, 'form': form},
			context_instance=RequestContext(request, site_context(request)))
	else:
		form = CommentForm()

	return render_to_response("gedgo/blogpost.html",
		{'post': post, 'form': form},
		context_instance=RequestContext(request, site_context(request)))


def month_list():
	"Month archive list"

	# TODO: Re-do this with an optimized SQL look-up:
	# e.g. select created from BlogPost.objects.all()
	# then map and gatherby twice.  Makes much more sense than this weirdness,
	# which hits the database for every intervening month between the first
	# post and now.

	if not BlogPost.objects.count():
		return []

	# set up vars
	now = datetime.now()
	year, month = (now.year, now.month)
	first = BlogPost.objects.order_by("created")[0]
	fyear = first.created.year
	fmonth = first.created.month
	months = []

	# loop over years and months
	for y in range(year, fyear - 1, -1):
		start, end = 12, 0
		if y == year:
			start = month
		if y == fyear:
			end = fmonth - 1

		for m in range(start, end, -1):
			if BlogPost.objects.filter(created__year=y, created__month=m):
				months.append((y, m, datetime(2012, m, 1).strftime('%B')))
	return months
