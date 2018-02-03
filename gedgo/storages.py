from django.core.files.storage import Storage, FileSystemStorage
from django.utils._os import safe_join
from django.conf import settings
from django.utils.module_loading import import_string

import re
import os
from PIL import Image
from cStringIO import StringIO
from dropbox.dropbox import Dropbox
from dropbox.files import FileMetadata, FolderMetadata, ThumbnailFormat, \
    ThumbnailSize


class DropBoxSearchableStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.client = Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        self.location = kwargs.get('location', settings.MEDIA_ROOT)

    def path(self, name):
        return safe_join(self.location, name)

    def exists(self, name):
        try:
            return isinstance(
                self.client.files_get_metadata(self.path(name)),
                (FileMetadata, FolderMetadata)
            )
        except Exception:
            return False

    def listdir(self, name):
        result = self.client.files_list_folder(self.path(name))
        return self._list_from_contents(self.path(name), result.entries)

    def _list_from_contents(self, path, contents):
        directories, files = [], []
        for entry in contents:
            if isinstance(entry, FileMetadata):
                files.append(entry.name)
            if isinstance(entry, FolderMetadata):
                directories.append(entry.name)
        return (directories, files)

    def open(self, name, mode='rb'):
        meta, resp = self.client.files_download(self.path(name))
        return resp.raw

    def size(self, name):
        return self.client.files_get_metadata(self.path(name)).size

    def url(self, name):
        url = self.client.files_get_temporary_link(self.path(name)).link
        return url

    def search(self, query, name='', start=0):
        result = self.client.files_search(self.path(name), query, start)
        directories, files = [], []
        for entry in result.matches:
            if isinstance(entry.metadata, FileMetadata):
                p = entry.metadata.path_display[len(self.location):]
                files.append(p)
            # Ignore directories for now
        return (directories, files)

    def preview(self, name, size='w128h128'):
        file_ = StringIO(self.client.files_get_thumbnail(
            self.path(name),
            format=ThumbnailFormat('jpeg', None),
            size=ThumbnailSize(size, None)
        )[1].content)
        return resize_thumb(file_, size)

    def can_preview(self, name):
        return (
            '.' in name and
            name.rsplit('.', 1)[1].lower() in (
                'jpeg', 'jpg', 'gif', 'png', 'pdf', 'tif', 'tiff',
                'mov', 'avi', 'doc', 'mpg', 'bmp', 'psd'
            )
        )


class FileSystemSearchableStorage(FileSystemStorage):
    def search(self, query):
        terms = [term for term in query.lower().split()]
        directories, files = [], []
        for root, ds, fs in os.walk(self.location):
            r = root[len(self.location) + 1:]
            for f in fs:
                if all([(t in f.lower()) for t in terms]):
                    files.append(os.path.join(r, f))
        return directories, files

    def preview(self, name, size='w128h128'):
        return resize_thumb(self.open(name), size)

    def can_preview(self, name):
        return (
            '.' in name and
            name.rsplit('.', 1)[1].lower() in (
                'jpeg', 'jpg'
            )
        )


def resize_thumb(file_, size='w128h128', crop=None):
    im = Image.open(file_)
    width, height = im.size

    if size in ('w64h64', 'w128h128'):
        if width > height:
            offset = (width - height) / 2
            box = (offset, 0, offset + height, height)
        else:
            offset = ((height - width) * 3) / 10
            box = (0, offset, width, offset + width)
        im = im.crop(box)

    m = re.match('w(\d+)h(\d+)', size)
    new_size = [int(d) for d in m.groups()]

    im.thumbnail(new_size, Image.ANTIALIAS)
    output = StringIO()
    im.save(output, 'JPEG')
    return output


research_storage = import_string(settings.GEDGO_RESEARCH_FILE_STORAGE)(
    location=settings.GEDGO_RESEARCH_FILE_ROOT)

gedcom_storage = import_string(settings.GEDGO_GEDCOM_FILE_STORAGE)(
    location=settings.GEDGO_GEDCOM_FILE_ROOT)

documentary_storage = import_string(settings.GEDGO_DOCUMENTARY_STORAGE)(
    location=settings.GEDGO_DOCUMENTARY_ROOT)
