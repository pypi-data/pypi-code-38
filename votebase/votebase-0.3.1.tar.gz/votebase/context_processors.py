from django.conf import settings
from django.core.urlresolvers import reverse


def host(request):
    """
    Returns a lazy 'host' context variable.
    """
    return {'host': request.get_host()}


def protocol(request):
    """
    Returns a lazy 'protocol' context variable.
    """
    return {'protocol': 'https://' if request.is_secure() else 'http://'}


def urls(request):
    """
    Returns URL addresses for some views
    """
    return {'surveys_index': reverse('surveys_index')}


def settings_constants(request):
    return {
        'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
    }
