from django.conf import settings
from django.http import Http404

from os import path
from os import listdir

from gedgo.views.util import serve_content, render

from django.contrib.auth.decorators import login_required


@login_required
def research(request, pathname):
    try:
        root = settings.RESEARCH_FILES_ROOT
    except:
        raise Http404

    r = path.join(root, pathname)

    if path.isfile(r):
        return serve_content(r)
    elif path.isdir(r):
        dir_contents = [
            (path.isdir(path.join(r, c)), c) for c in listdir(r)
            if not c.startswith('.')
        ]

        if pathname and not pathname.startswith('/'):
            pathname = '/' + pathname
        pathname = path.normpath(pathname)
        if pathname == '.':
            pathname = ''

        levels = pathname.split('/')  # Is there a better way than this?

        current_level = 'Research Files'
        if len(pathname) > 2:
            current_level = levels[-1]

        return render(
            request,
            'research.html',
            {
                'contents': dir_contents,
                'levels': levels,
                'path': pathname,
                'current_level': current_level
            }
        )
    else:
        raise Http404
