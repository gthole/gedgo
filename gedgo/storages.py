from django.core.files.storage import Storage, FileSystemStorage
from django.utils._os import safe_join
from django.conf import settings
from django.utils.module_loading import import_string

import os
from dropbox.client import DropboxClient


class DropboxStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.client = DropboxClient(settings.DROPBOX_ACCESS_TOKEN)
        self.location = kwargs.get('location', settings.MEDIA_ROOT)

    def path(self, name):
        return safe_join(self.location, name)

    def exists(self, name):
        try:
            return isinstance(self.client.metadata(self.path(name)), dict)
        except:
            return False

    def listdir(self, name):
        meta = self.client.metadata(self.path(name))
        return self._list_from_contents(self.path(name), meta['contents'])

    def _list_from_contents(self, path, contents):
        directories, files = [], []
        for entry in contents:
            name = entry['path'][len(path) + 1:]
            if entry['is_dir']:
                directories.append(name)
            else:
                files.append(name)
        return (directories, files)

    def open(self, name, mode='rb'):
        return self.client.get_file(self.path(name))

    def size(self, name):
        return self.client.metadata(self.path(name)).bytes

    def url(self, name):
        return self.client.media(self.path(name))['url']

    def search(self, query, name=''):
        contents = self.client.search(self.path(name), query)
        return self._list_from_contents(self.path(name), contents)

    def preview(self, name):
        return self.client.thumbnail(self.path(name), 's')


class ResearchFileSystemStorage(FileSystemStorage):
    def search(self, query):
        terms = [term for term in query.lower().split()]
        directories, files = [], []
        for root, ds, fs in os.walk(self.location):
            r = root[len(self.location) + 1:]
            for f in fs:
                if all([(t in f.lower()) for t in terms]):
                    files.append(os.path.join(r, f))
        return directories, files

    def preview(self, path):
        raise NotImplementedError


research_storage = import_string(settings.GEDGO_RESEARCH_FILE_STORAGE)(
    location=settings.GEDGO_RESEARCH_FILE_ROOT)

gedcom_storage = import_string(settings.GEDGO_GEDCOM_FILE_STORAGE)(
    location=settings.GEDGO_GEDCOM_FILE_ROOT)
