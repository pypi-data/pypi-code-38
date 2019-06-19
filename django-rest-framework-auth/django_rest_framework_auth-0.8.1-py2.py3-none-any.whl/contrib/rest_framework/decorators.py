import functools

from rest_framework.request import Request


def sensitive_post_parameters(*parameters):
    """hide sensitive POST paramters from Django's error reporting.

    This decorator should be used for ``rest_framework``'s views if your
    views use sensitive data like `password`, because rest_framework use
    ``rest_framework.request.Request``, **NOT** ``django.http.HttpRequest``
    (*This is not subclassed*)

    (so django's ``sensitive_post_parameters`` cannot be used for
    rest_framework)
    """
    def decorator(view):
        @functools.wraps(view)
        def wrapper(req, *args, **kwargs):
            assert isinstance(req, Request), (
                "sensitive_post_parameters didn't receive an Request. "
            )
            req._request.sensitive_post_parameters = parameters or '__ALL__'
            return view(req, *args, **kwargs)
        return wrapper
    return decorator
