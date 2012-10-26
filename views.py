from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.mail import send_mail
from django.conf import settings

from gedgo.models import Person
from gedgo.forms import CommentForm

# Temporary.
css = open(settings.STATIC_URL + 'style.css').read()

def search_form(request):
	return render_to_response('gedgo/search.html')

def search(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        
        people = Person.objects.all()
        for term in q.split(' '):
            people = people & (Person.objects.filter(last_name__icontains=term) | 
                Person.objects.filter(first_name__icontains=term))
        
        return render_to_response('gedgo/search_results.html',
            {'people': people, 'query': q, 'css': css}, context_instance=RequestContext(request))
    else:
        return render_to_response('gedgo/search_results.html',
            {'people': Person.objects.none(), 'css': css}, context_instance=RequestContext(request))

def person(request, person_id):
	p = get_object_or_404(Person, pointer=person_id)
	
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			send_mail(
				'Comment from ' + cd['name'] + ' about ' + p.full_name() + '(' + p.pointer + ')',
				cd['message'],
				cd.get('email', 'noreply@example.com'),
				[settings.SERVER_EMAIL],
			)
		return render_to_response('gedgo/person.html', {'person':p, 'css': css, 'form': form},
			context_instance=RequestContext(request))
	else:
		form = CommentForm()
	
	
	return render_to_response('gedgo/person.html', {'person':p, 'css': css, 'form': form},
		context_instance=RequestContext(request))



