from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from gedgo.models import Person, Family, Gedcom, BlogPost, Document
from gedgo.forms import CommentForm, comment_action, UpdateForm
from gedgo.visualizations import timeline
import gedgo.update

from re import findall
from datetime import datetime


# --- Gedcom 

@login_required
def gedcom(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	post = BlogPost.objects.all().order_by("-created")
	if post:
		post = post[0]
	
	if request.method == 'POST':
		form = comment_action(request, 'Gedcom #' + str(g.id))
		return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()
	
	return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form}, 
		context_instance=RequestContext(request))


@login_required
def person(request, gedcom_id, person_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	p = get_object_or_404(Person, gedcom=g, pointer=person_id)
	posts = BlogPost.objects.filter(tagged_people=p)
	events, hindex = timeline(p)
	
	if request.method == 'POST':
		form = comment_action(request, p.full_name() + ' (' + p.pointer + ')')
		return render_to_response('gedgo/person.html', 
			{'person':p, 'posts': posts, 'gedcom': g, 'events': events, 'hindex': hindex, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()
	
	
	return render_to_response('gedgo/person.html', 
		{'person':p, 'posts': posts, 'gedcom': g, 'events': events, 'hindex': hindex, 'form': form},
		context_instance=RequestContext(request))


@login_required
def family(request, family_id, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	f = get_object_or_404(Family, gedcom=g, pointer=family_id)
	
	if request.method == 'POST':
		form = comment_action(request, f.family_name() + ' (' + f.pointer + ')')
		return render_to_response('gedgo/family.html', 
			{'family':f, 'gedcom': g, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()
	
	
	return render_to_response('gedgo/family.html', 
		{'family':f, 'gedcom': g, 'form': form},
		context_instance=RequestContext(request))


@login_required
def documentaries(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	documentaries = Document.objects.filter(kind='DOCUV').order_by('-last_updated')
	
	return render_to_response("gedgo/documentaries.html", 
		{'documentaries': documentaries, 'gedcom': g, 'user': request.user},
		context_instance=RequestContext(request))


@login_required
def search(request):
	if 'q' in request.GET and request.GET['q']:
		q = request.GET['q']
		
		g = Gedcom.objects.all()
		if len(g) > 0:
			g = g[0]
		
		people = Person.objects.all()
		posts = BlogPost.objects.all()
		
		for term in findall('\w+', q):  # Throw away non-word characters.
			people = people & (Person.objects.filter(last_name__icontains=term) | 
							   Person.objects.filter(first_name__icontains=term) |
							   Person.objects.filter(suffix__icontains=term))
			posts = posts & (BlogPost.objects.filter(title__icontains=term) |
							 BlogPost.objects.filter(body__icontains=term))
		
		return render_to_response('gedgo/search_results.html', 
			{'people': people, 'gedcom': g, 'posts': posts, 'query': q}, 
			context_instance=RequestContext(request))
	else:
		return render_to_response('gedgo/search_results.html',
			{'people': Person.objects.none(), 'gedcom': g, 'posts': BlogPost.objects.none()}, 
			context_instance=RequestContext(request))


@login_required
def update(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	
	if request.method == 'POST':
		form = UpdateForm(request.POST, request.FILES)
		if form.is_valid():
			
			# Need to distribute-task this
			tmp = open(settings.MEDIA_ROOT + 'documents/tmp.ged','r+')
			tmp.write(request.FILES['gedcom_file'].read())
			tmp.close()
			gedgo.update.update(g, settings.MEDIA_ROOT + 'documents/tmp.ged')
			
			# Redirect to the document list after POST
			return redirect('/gedgo/' + str(g.id) + '/I66')
		else:
			return redirect('/gedgo/1/I68')
	else:
		form = UpdateForm()
	
	# Render list page with the documents and the form
	return render_to_response(
		'gedgo/update.html',
		{'form': form, 'gedcom': g},
		context_instance=RequestContext(request)
	)


# --- Blog 



@login_required
def blog(request, gedcom_id, year, month):
	"Blog front page - listing posts by creation date."
	g = get_object_or_404(Gedcom, id=gedcom_id)
	posts = BlogPost.objects.all().order_by("-created")
	
	if year:
		posts = posts & BlogPost.objects.filter(created__year=year)
	if month:
		posts = posts & BlogPost.objects.filter(created__month=month)
	
	paginator = Paginator(posts, 2)
	
	try: page = int(request.GET.get("page", '1'))
	except ValueError: page = 1
	
	try:
		posts = paginator.page(page)
	except (InvalidPage, EmptyPage):
		posts = paginator.page(paginator.num_pages)
	
	return render_to_response("gedgo/blogpost_list.html", 
		{'posts': posts, 'gedcom': g, 'user': request.user, 'months': month_list()},
		context_instance=RequestContext(request))


@login_required
def blog_list(request, gedcom_id):
	return blog(request, gedcom_id, None, None)


@login_required
def blogpost(request, post_id, gedcom_id):
	"Single post."
	g = get_object_or_404(Gedcom, id=gedcom_id)
	post = get_object_or_404(BlogPost, id=post_id)
	
	if request.method == 'POST':
		form = comment_action(request, post.title + ' (blog post comment)')
		return render_to_response('gedgo/blogpost.html', 
			{'post': post, 'gedcom': g, 'form': form, 'user': request.user},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()
	
	return render_to_response("gedgo/blogpost.html", 
		{'post': post, 'gedcom': g, 'form': form, 'user': request.user},
		context_instance=RequestContext(request))


def month_list():
	"Month archive list"
	
	# TODO: Re-do this with an optimized SQL look-up:
	# e.g. select created from BlogPost.objects.all()
	# then map and gatherby twice.  Makes much more sense than this weirdness,
	# which hits the database for every intervening month between the first 
	# post and now.
	
	if not BlogPost.objects.count(): return []
	
	# set up vars
	now = datetime.now()
	year, month = (now.year, now.month)
	first = BlogPost.objects.order_by("created")[0]
	fyear = first.created.year
	fmonth = first.created.month
	months = []
	
	# loop over years and months
	for y in range(year, fyear-1, -1):
		start, end = 12, 0
		if y == year: start = month
		if y == fyear: end = fmonth-1
		
		for m in range(start, end, -1):
			if BlogPost.objects.filter(created__year=y, created__month=m):
				months.append((y, m, datetime(2012,m,1).strftime('%B')))
	return months
