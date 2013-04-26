from django.conf import settings

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404

from os import path
from os import listdir

from gedgo.views.util import serve_content, site_context

from django.contrib.auth.decorators import login_required


@login_required
def researchfiles(request, pathname):
    try:
        root = settings.RESEARCH_FILES_ROOT
    except:
        raise Http404

    r = path.join(root, pathname)

    if path.isfile(r):
        return serve_content(r)
    elif path.isdir(r):
        dir_contents = filter(lambda c: not c[0] == '.', listdir(r))
        dir_contents = map(lambda c: (path.isdir(path.join(r, c)), c), dir_contents)

        if (len(pathname) > 0) and (not pathname[0] == '/'):
            pathname = '/' + pathname
        pathname = path.normpath(pathname)
        if pathname == '.':
            pathname = ''

        levels = pathname.split('/')  # Is there a better way than this?

        if len(pathname) < 2:
            current_level = 'Research Files'
        else:
            current_level = levels[-1]

        return render_to_response('gedgo/researchfiles.html',
            {'contents': dir_contents, 'levels': levels, 'path': pathname,
            'current_level': current_level},
            context_instance=RequestContext(request, site_context(request)))
    else:
        raise Http404
