"""
Custom storage for Documents to allow dynamic MEDIA_ROOT paths
"""
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousOperation
from django.utils._os import safe_join
from anaf.core.conf import settings
import os


class FileStorage(FileSystemStorage):

    def path(self, name):
        try:
            path = safe_join(getattr(settings, 'MEDIA_ROOT'), name)
        except ValueError:
            raise SuspiciousOperation(
                "Attempted access to '{0!s}' denied.".format(name))
        return os.path.normpath(path)
