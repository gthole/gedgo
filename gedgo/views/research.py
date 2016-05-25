from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

from os import path
import mimetypes

from gedgo.views.util import serve_content, render
from gedgo.storages import research_storage as storage


@login_required
def research_preview(request, pathname):
    """
    Cached preview thumbnails for jpegs (supported by Dropbox)
    """
    name = pathname.strip('/')
    if not can_preview(name):
        raise Http404

    cache_name = path.join('research', 'preview-cache', name)
    if default_storage.exists(cache_name):
        return serve_content(default_storage, cache_name)
    try:
        content = storage.preview(name)
        assert content
        default_storage.save(cache_name, content)
        return serve_content(default_storage, cache_name)
    except:
        raise Http404


@login_required
def research(request, pathname):
    if storage is None:
        raise Http404

    name = pathname.strip('/')

    # Serve the content through xsendfile or directly.
    try:
        if '.' in name:
            return serve_content(storage, name)
        else:
            if request.GET.get('rq') and hasattr(storage, 'search'):
                directories, files = storage.search(request.GET['rq'], name)
            else:
                directories, files = storage.listdir(name)
            directories = [process_file(name, d, True) for d in directories]
            files = [process_file(name, f, False) for f in files]

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
                    'pathname': name,
                    'can_search': hasattr(storage, 'search'),
                    'rquery': request.GET.get('rq', ''),
                    'directories': directories,
                    'files': files,
                    'levels': levels
                }
            )
    except Exception as e:
        raise e
        raise Http404


def can_preview(name):
    return (
        hasattr(storage, 'preview') and
        (name.lower().endswith('.jpeg') or name.lower().endswith('.jpg'))
    )


def process_file(name, p, is_dir=False):
    type_ = 'folder_open' if is_dir else _get_type(p)
    return {
        'type': type_,
        'path': path.join(name, p),
        'name': path.basename(p),
        'preview': can_preview(p)
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
