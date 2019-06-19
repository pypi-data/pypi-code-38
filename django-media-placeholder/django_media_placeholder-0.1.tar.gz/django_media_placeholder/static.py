from django.conf.urls.static import static as django_static
from django.views.static import serve as static_serve

from django_media_placeholder.custom_storage import OverwritingStorage


def serve(request, path, document_root):
    storage = OverwritingStorage()

    if not storage.exists(path):
        storage.get_remote_file(path)
    
    return static_serve(request, path, document_root)


def static(prefix, view=serve, **kwargs):
    return django_static(prefix, view, **kwargs)
