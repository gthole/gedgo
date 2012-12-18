from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from os import path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404


@login_required
def media(request, file_base_name):
	"""
	http://djangosnippets.org/snippets/365/
	"""
	filename = settings.MEDIA_ROOT + file_base_name
	if not path.exists(filename):
		raise Http404
	wrapper = FileWrapper(file(filename))
	response = HttpResponse(wrapper, content_type='text/plain')
	response['Content-Length'] = path.getsize(filename)
	return response
