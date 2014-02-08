from django.conf import settings
from django.http import Http404
from django.contrib.auth.decorators import login_required

from os import path
from os import listdir
import mimetypes

from gedgo.views.util import serve_content, render

# glyphicon name mappings
MIMETYPE_MAPPING = {
    'video': 'facetime-video',
    'audio': 'volume-up',
    'image': 'picture'
}


@login_required
def research(request, pathname):
    try:
        root = path.abspath(settings.RESEARCH_FILES_ROOT)
    except:
        raise Http404

    # Force join the path with the research root to prevent serving
    # private files.
    pathname = pathname.strip('/')
    r = path.join(root, pathname)

    # Don't allow relative path locations outside of the root.
    if '..' in pathname:
        raise Http404

    # Serve the content directly.  TODO: Have a webserver do this.
    if path.isfile(r):
        return serve_content(r)

    elif path.isdir(r) and '.' not in pathname:
        # List the contents of the directory
        contents = [
            (_get_type(r, c), c, _normalize('%s/%s' % (pathname, c)))
            for c in listdir(r) if not c.startswith('.')
        ]

        # Build a depth tree of the directories above this one for navigation
        levels = [('Research Files', '')]
        if pathname:
            lp = ''
            for l in pathname.split('/'):
                lp = _normalize('%s/%s' % (lp, l))
                levels.append((l, lp))

        return render(
            request,
            'research.html',
            {
                'contents': contents,
                'levels': levels
            }
        )
    else:
        raise Http404


def _normalize(p):
    p = path.normpath(p)
    if not p.startswith('/'):
        p = '/' + p
    return p


def _get_type(r, c):
    if path.isdir(path.join(r, c)):
        return 'folder-open'
    guess, _ = mimetypes.guess_type(c)
    if guess and guess.split('/')[0] in ['audio', 'video', 'image']:
        return MIMETYPE_MAPPING[guess.split('/')[0]]
    return 'file'
