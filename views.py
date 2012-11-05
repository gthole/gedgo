from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from gedgo.models import Person, Gedcom, BlogPost, Document
from gedgo.forms import CommentForm, comment_action
from gedgo.visualizations import timeline

from re import findall


# --- Gedcom 

@login_required
def gedcom(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	post = BlogPost.objects.all().order_by("-created")
	if post:
		post = post[0]
	
	if request.method == 'POST':
		form = comment_action(request, 'gedcom ' + gedcom.id)
		return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()
	
	return render_to_response('gedgo/gedcom.html', {'gedcom': g, 'post': post, 'form': form}, 
		context_instance=RequestContext(request))

@login_required
def gedcom_redirect(request):
	return redirect('/gedgo/1/')


@login_required
def person(request, gedcom_id, person_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	p = get_object_or_404(Person, gedcom=g, pointer=person_id)
	posts = BlogPost.objects.filter(tagged_people=p)
	events, hindex = timeline(p)
	
	if request.method == 'POST':
		form = comment_action(request, p.full_name() + '(' + p.pointer + ')')
		return render_to_response('gedgo/person.html', 
			{'person':p, 'posts': posts, 'gedcom': g, 'events': events, 'hindex': hindex, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()
	
	
	return render_to_response('gedgo/person.html', 
		{'person':p, 'posts': posts, 'gedcom': g, 'events': events, 'hindex': hindex, 'form': form},
		context_instance=RequestContext(request))


@login_required
def documentaries(request, gedcom_id):
	g = get_object_or_404(Gedcom, id=gedcom_id)
	documentaries = Document.objects.filter(kind='DOCUV').order_by('-last_updated')
	
	return render_to_response("gedgo/documentaries.html", 
		{'documentaries': documentaries, 'gedcom': g, 'user': request.user},
		context_instance=RequestContext(request))

@login_required
def documentaries_redirect(request):
	return redirect('/gedgo/1/documentaries/')
	

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



# --- Blog 



@login_required
def blog(request, gedcom_id):
	"Blog front page - listing posts by creation date."
	g = get_object_or_404(Gedcom, id=gedcom_id)
	posts = BlogPost.objects.all().order_by("-created")
	paginator = Paginator(posts, 2)
	
	try: page = int(request.GET.get("page", '1'))
	except ValueError: page = 1
	
	try:
		posts = paginator.page(page)
	except (InvalidPage, EmptyPage):
		posts = paginator.page(paginator.num_pages)
	
	return render_to_response("gedgo/blogpost_list.html", 
		{'posts': posts, 'gedcom': g, 'user': request.user},
		context_instance=RequestContext(request))


@login_required
def blog_redirect(request):
	return redirect('/gedgo/1/blog/')


@login_required
def blogpost(request, post_id, gedcom_id):
	"Single post."
	# TODO: Blog comments.
	g = get_object_or_404(Gedcom, id=gedcom_id)
	post = get_object_or_404(BlogPost, id=post_id)
	
	return render_to_response("gedgo/blogpost.html", 
		{'post': post, 'gedcom': g, 'user': request.user},
		context_instance=RequestContext(request))