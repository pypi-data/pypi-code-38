from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.files.storage import Storage
from django.core.files import File
from django.urls import reverse
from django.db import connection

import magic

from io import BytesIO
from .models import DbFile

class DatabaseStorage(Storage):
    model = DbFile

    def _open(self, name, mode='rb'):
        assert mode == 'rb', "open mode must be 'rb'."

        file = self.model.objects.defer("data").get(name=name)
        return File(BytesIO(file.data))

    def _save(self, name, content):
        binary = content.read()
        size = len(binary)
        media_type = magic.from_buffer(binary, mime=True)
        file = self.model(name=name, data=binary, size=size, media_type=media_type)
        file.save()

        return name

    def exists(self, name):
        return self.model.objects.defer("data").filter(name=name).exists()

    def delete(self, name):
        self.model.objects.defer("data").get(name=name).delete()

    def url(self, name):
        return reverse('download', kwargs={'filename': name})

    def size(self, name):
        return self.model.objects.defer("data").get(name=name).size

    def created_time(self, name):
        return self.model.objects.defer("data").get(name=name).created
