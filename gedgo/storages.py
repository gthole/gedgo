from django.core.files.storage import Storage, FileSystemStorage
from django.utils._os import safe_join
from django.conf import settings
from django.utils.module_loading import import_string

from cStringIO import StringIO
import os
from dropbox.dropbox import Dropbox
from dropbox.files import FileMetadata, FolderMetadata, ThumbnailFormat, \
    ThumbnailSize


class DropboxStorage(Storage):
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
        except:
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
        meta, resp= self.client.files_download(self.path(name))
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

    def preview(self, name, size='w64h64'):
        return StringIO(self.client.files_get_thumbnail(
            self.path(name),
            format=ThumbnailFormat('jpeg', None),
            size=ThumbnailSize(size, None)
        )[1].content)


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


research_storage = import_string(settings.GEDGO_RESEARCH_FILE_STORAGE)(
    location=settings.GEDGO_RESEARCH_FILE_ROOT)

gedcom_storage = import_string(settings.GEDGO_GEDCOM_FILE_STORAGE)(
    location=settings.GEDGO_GEDCOM_FILE_ROOT)
