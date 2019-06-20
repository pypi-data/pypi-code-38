# -*- coding: utf-8 -*-
from congo.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
import collections
import os

class CongoFinder(FileSystemFinder):
    def __init__(self, apps = None, *args, **kwargs):
        self.locations = [
            ('', os.path.join(settings.CONGO_BASE_DIR, 'static')),
        ]

        self.storages = collections.OrderedDict()

        filesystem_storage = FileSystemStorage(location = self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages[self.locations[0][1]] = filesystem_storage
