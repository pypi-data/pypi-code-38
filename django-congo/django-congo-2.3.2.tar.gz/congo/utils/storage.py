# -*- coding: utf-8 -*-
from django.core.files.storage import FileSystemStorage as DjangoFileSystemStorage

class FileSystemStorage(DjangoFileSystemStorage):
    def get_available_name(self, name):
        return name

    def _save(self, name, content):
        if self.exists(name):
            return name
        return super(FileSystemStorage, self)._save(name, content)
