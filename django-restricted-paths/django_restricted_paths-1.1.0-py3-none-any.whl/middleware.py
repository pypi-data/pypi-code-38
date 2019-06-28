from django.http import Http404
from django.utils.module_loading import import_string

from .settings import DEBUG, PATHS, VIEW


class RestrictedPathsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if DEBUG is False:
            if not request.user.is_staff:
                for path in PATHS:
                    if request.path.startswith(path):
                        try:
                            ViewClass = import_string(VIEW)
                            view = ViewClass.as_view()
                            return view(request)
                        except (AttributeError, ImportError):
                            raise Http404
        return self.get_response(request)
