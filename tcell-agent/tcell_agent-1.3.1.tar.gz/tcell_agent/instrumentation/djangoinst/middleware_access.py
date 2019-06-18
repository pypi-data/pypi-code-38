from tcell_agent.instrumentation.djangoinst.config import get_django_settings


# Note: DJANGO 1.10 introduced "MIDDLEWARE" and deprecated
#       "MIDDLEWARE_CLASSES". So it is possible to still use
#       "MIDDLEWARE_CLASSES" with Django 1.10. So in order to
#       determine which attribute is being used
#       ("MIDDLEWARE" or "MIDDLEWARE_CLASSES"),
#       settings must be checked to see if it has "MIDDLEWARE"
#       attribute AND if settings.MIDDLEWARE is not empty.
#       If settings.MIDDLEWARE exists but it's empty then
#       it's safe to assume MIDDLEWARE_CLASSES is still in use.
def get_middleware_list():
    settings = get_django_settings()
    if hasattr(settings, "MIDDLEWARE") and settings.MIDDLEWARE:
        return list(settings.MIDDLEWARE)

    return list(settings.MIDDLEWARE_CLASSES)


def get_middleware_index(middleware_list, after=None, before=None, atIdx=None):
    if after:
        return middleware_list.index(after) + 1 if after in middleware_list else len(middleware_list)
    elif before:
        return middleware_list.index(before) if before in middleware_list else 0
    elif atIdx is not None:
        return atIdx

    return len(middleware_list)


def insert_middleware(middleware_class_string, after=None, before=None, atIdx=None):
    settings = get_django_settings()

    middleware_list = get_middleware_list()
    idx = get_middleware_index(middleware_list, after, before, atIdx)
    middleware_list.insert(idx, middleware_class_string)

    if hasattr(settings, "MIDDLEWARE") and settings.MIDDLEWARE:
        settings.MIDDLEWARE = tuple(middleware_list)
    else:
        settings.MIDDLEWARE_CLASSES = tuple(middleware_list)


def is_middleware_enabled(name):
    middleware_list = get_middleware_list()
    return name in middleware_list


def is_csrf_middleware_enabled():
    return is_middleware_enabled("django.middleware.csrf.CsrfViewMiddleware")


def is_security_middleware_enabled():
    return is_middleware_enabled("django.middleware.security.SecurityMiddleware")


def is_session_middleware_enabled():
    return is_middleware_enabled("django.contrib.sessions.middleware.SessionMiddleware")


def is_authentication_middleware_enabled():
    return is_middleware_enabled("django.contrib.auth.middleware.AuthenticationMiddleware")


def is_session_authentication_middleware_enabled():
    return is_middleware_enabled("django.contrib.auth.middleware.SessionAuthenticationMiddleware")
