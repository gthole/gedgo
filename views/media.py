from django.conf import settings
from django.contrib.auth.decorators import login_required

from gedgo.views.util import serve_content


@login_required
def media(request, file_base_name):
	filename = settings.MEDIA_ROOT + file_base_name
	return serve_content(filename)
