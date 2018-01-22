from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

from os import path
import mimetypes

from gedgo.views.util import render
from gedgo.storages import research_storage as storage

import sys
sys.stdout = sys.stderr

FOLDER_CACHE = ('', ([], []))


def build_levels(name):
    # Build a depth tree of the directories above this one for
    # navigation
    levels = [('Research Files', '')]
    if name:
        lp = ''
        for l in name.split('/'):
            lp = '%s/%s' % (lp, l)
            levels.append((l, lp))
    return levels


def get_dir_contents(dirname, rq):
    global FOLDER_CACHE

    if FOLDER_CACHE[:2] == (dirname, rq):
        (_, _, (directories, files)) = FOLDER_CACHE
        return (directories, files)

    if rq and hasattr(storage, 'search'):
        directories, files = storage.search(rq, dirname)
    else:
        directories, files = storage.listdir(dirname)
        directories = [path.join(dirname, d) for d in directories]
        files = [path.join(dirname, f) for f in files]

    directories.sort()
    files.sort()
    FOLDER_CACHE = (dirname, rq, (directories, files))

    return (directories, files)


@login_required
def research(request, pathname):
    if storage is None:
        raise Http404

    dirname = pathname.strip('/')
    basename = request.GET.get('fn')

    directories, files = get_dir_contents(dirname, request.GET.get('rq'))
    levels = build_levels(dirname)

    context = {
        'rq': request.GET.get('rq', ''),
        'can_search': hasattr(storage, 'search'),
        'levels': levels,
        'dirname': dirname
    }

    if request.GET.get('fn'):
        try:
            index = [f[len(dirname):] for f in files].index(basename)
        except:
            raise Http404
        next_file = files[(index + 1) % len(files)]
        prev_file = files[(index - 1) % len(files)]

        context['file'] = process_file(dirname, basename, False)
        context['next_file'] = process_file(dirname, next_file, False)
        context['prev_file'] = process_file(dirname, prev_file, False)

        return render(request, 'research_preview.html', context)
    else:
        directories = [process_file(dirname, d, True) for d in directories]
        files = [process_file(dirname, f, False) for f in files]
        context['directories'] = directories
        context['files'] = files

        return render(request, 'research.html', context)


def process_file(name, p, is_dir=False):
    type_ = 'folder_open' if is_dir else _get_type(p)
    fn = p[len(name):] if p.lower().startswith(name.lower()) else p
    return {
        'type': type_,
        'full_path': path.join(name, path.basename(p)),
        'name': path.basename(p),
        'path': fn,
        'can_video': not is_dir and p.rsplit('.')[1].lower() in ('m4v',),
        'preview': can_preview(storage, p)
    }

# glyphicon name mappings
MIMETYPE_MAPPING = {
    'video': 'video-camera',
    'audio': 'volume-up',
    'image': 'image'
}



def _get_type(c):
    guess, _ = mimetypes.guess_type(c)
    if guess and guess.split('/')[0] in MIMETYPE_MAPPING:
        return MIMETYPE_MAPPING[guess.split('/')[0]]
    return 'file'


def is_ascii(s):
        return all(ord(c) < 128 for c in s)


def can_preview(storage, name):
    """
    Check if the file in question can generate a preview
    """
    return (
        hasattr(storage, 'preview') and
        is_ascii(name) and
        storage.can_preview(name)
    )
