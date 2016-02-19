from django.core.files.storage import Storage
from django.utils._os import safe_join
from django.conf import settings

import os
from dropbox.client import DropboxClient


class DropboxStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.client = DropboxClient(settings.DROPBOX_ACCESS_TOKEN)
        self.location = kwargs.get('location', settings.MEDIA_ROOT)

    def path(self, name):
        return safe_join(self.location, name)

    def created_time(self, name):
        raise NotImplementedError

    def exists(self, name):
        try:
            return isinstance(self.client.metadata(self.path(name)), dict)
        except:
            return False

    def get_available_name(self, name):
        raise NotImplementedError

    def get_valid_name(self, name):
        raise NotImplementedError

    def listdir(self, path):
        meta = self.client.metadata(self.path(path))
        directories, files = [], []
        for entry in meta['contents']:
            name = os.path.basename(entry['path'])
            if entry['is_dir']:
                directories.append(name)
            else:
                files.append(name)
        return (directories, files)

    def modified_time(self, name):
        raise NotImplementedError

    def open(self, name, mode='rb'):
        return self.client.get_file(self.path(name))

    def save(self, name, content, max_length=None):
        raise NotImplementedError

    def size(self, name):
        return self.client.metadata(self.path(name)).bytes

    def url(self, name):
        return self.client.media(self.path(name))['url']
