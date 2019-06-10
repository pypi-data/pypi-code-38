from threading import local

_active = local()


def get_request():
    """
    Utility that gets the current request
    """

    if hasattr(_active, "request"):

        return _active.request
    else:
        return None


def get_user():
    """
    Utility that safely gets the current logged user (when using
    GlobalRequestMiddleware).
    """
    request = get_request()

    if request and request.user.is_authenticated:
        return request.user

    return None


def get_agent():
    """
    Utility that safely gets the current requestor's user agent (when using
    GlobalRequestMiddleware).
    """
    request = get_request()

    if request and request.META:
        return request.META.get("HTTP_USER_AGENT")

    return None


class GlobalRequestMiddleware(object):
    """
    Midlware that attaches the current request into the local thread and makes
    it available via #get_request() function.

    MIDDLEWARE_CLASSES = (
        ...
        'orion.middleware.GlobalRequestMiddleware'
        ...
    )

    @author: Ivanir Joao Kreuzberg
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        _active.request = request
        return None
