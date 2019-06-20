# -*- coding: utf-8 -*-
from congo.utils.text import slugify
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.encoding import force_unicode, smart_str
import csv
import os

def handle_uploaded_file(file_handler, filename):
    file_path = os.path.normpath(force_unicode(smart_str(os.path.join(settings.UPLOAD_ROOT, filename))))
    with open(file_path, 'wb+') as destination:
        for chunk in file_handler.chunks():
            destination.write(chunk)
    return file_path

def unicode_csv_reader(csv_data, **kwargs):
    csv_reader = csv.reader(csv_data, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

def get_uploads_filename(self, instance, filename):
    directory_name = 'uploads'
    random_string = get_random_string(4, allowed_chars = 'abcdef0123456789')
    filename = self.get_filename(slugify(filename))
    return os.path.join(directory_name, random_string[0:2], random_string[2:4], filename)

def is_static_path(request):
    for path in settings.CONGO_STATICFILES_URLS:
        if request.path.startswith(path):
            return True
    return False
