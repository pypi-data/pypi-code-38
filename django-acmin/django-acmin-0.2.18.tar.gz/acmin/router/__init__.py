from functools import wraps

from django.http import HttpResponse
from django.urls import path as django_patb
from django.views.decorators.csrf import csrf_exempt

from acmin.utils import *

methods = {}


def get_urlpatterns():
    return [
        django_patb(r, get_view(func), name=f"{func.__module__}.{func.__qualname__}")
        for r, func in methods.items()
    ]


def admin_route(path):
    from django.conf import settings
    return route(path, f"{settings.ACMIN_ADMIN_PREFIX}/{settings.ACMIN_APP_NAME}" or "")


def route(path, prefix=""):
    def decorate(func):
        new_path = prefix + path
        if new_path.startswith("/"):
            new_path = new_path[1:]

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        methods[new_path] = wrapper
        return wrapper

    return decorate


def api_route(path, login_required=True):
    def decorate(func):
        new_path = path
        if new_path.startswith("/"):
            new_path = new_path[1:]

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not login_required or args[0].user.is_authenticated:
                result = func(*args, **kwargs)
                if type(result) is not dict:
                    return HttpResponse(status=500, content="Result is not a dict obj")
                return json_response(func(*args, **kwargs))
            else:
                return HttpResponse(status=401)

        methods[new_path] = wrapper

    return decorate


def get_view(func):
    qualname = func.__qualname__
    module_name = func.__module__
    cls = None
    if "." in qualname:
        class_name, _ = qualname.split(".")
        cls = import_class("%s.%s" % (module_name, class_name))

        @csrf_exempt
        def view(request, *args, **kwargs):
            obj = cls()
            obj.request = request
            obj.args = args
            obj.kwargs = kwargs
            return func(obj, *args, **kwargs)
    else:
        def view(request, *args, **kwargs):
            return func(request, *args, **kwargs)

    return view
