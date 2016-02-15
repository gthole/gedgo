from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.module_loading import import_string

from os import path
import mimetypes

from gedgo.views.util import render


storage = None
if getattr(settings, 'GEDGO_RESEARCH_FILE_STORAGE', None):
    storage = import_string(settings.GEDGO_RESEARCH_FILE_STORAGE)(
        location=settings.GEDGO_RESEARCH_FILE_ROOT)


@login_required
def research(request, pathname):
    if storage is None:
        raise Http404

    name = pathname.strip('/')

    # Serve the content through xsendfile or directly.
    try:
        if '.' in name:
            return HttpResponseRedirect(storage.url(name))
        else:
            directories, files = storage.listdir(name)
            directories = [__process(name, d, True) for d in directories]
            files = [__process(name, f, False) for f in files]

            # Build a depth tree of the directories above this one for
            # navigation
            levels = [('Research Files', '')]
            if name:
                lp = ''
                for l in name.split('/'):
                    lp = '%s/%s' % (lp, l)
                    levels.append((l, lp))

            return render(
                request,
                'research.html',
                {
                    'directories': directories,
                    'files': files,
                    'levels': levels
                }
            )
    except Exception as e:
        raise e
        raise Http404


def __process(name, p, is_dir=False):
    type_ = 'folder_open' if is_dir else _get_type(p)
    return {
        'type': type_,
        'path': path.join(name, p),
        'name': p,
        'preview': type_ == 'image'
    }

# glyphicon name mappings
MIMETYPE_MAPPING = {
    'video': 'facetime-video',
    'audio': 'volume-up',
    'image': 'picture'
}


def _get_type(c):
    guess, _ = mimetypes.guess_type(c)
    if guess and guess.split('/')[0] in MIMETYPE_MAPPING:
        return MIMETYPE_MAPPING[guess.split('/')[0]]
    return 'file'
