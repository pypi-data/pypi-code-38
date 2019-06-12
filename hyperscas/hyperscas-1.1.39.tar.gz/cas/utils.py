import logging

import django
from django.contrib import auth
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseRedirect
from six.moves.urllib_parse import urlencode
from six.moves import urllib_parse as urlparse
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

from .models import SessionServiceTicket
from .cache import cacheByTime
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('cas')


def _logout_url(request, next_page=None):
    """
    Generates CAS logout URL

    :param: request RequestObj
    :param: next_page Page to redirect after logout.

    """

    cas_url = request.domain.auth.url + '/cas/'
    url = urlparse.urljoin(cas_url, 'logout')

    if next_page and getattr(settings, 'CAS_PROVIDE_URL_TO_LOGOUT', True):
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'service': protocol + host + next_page})
    return url


def _redirect_url(request):
    """
    Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.

    :param: request RequestObj

    """

    next = request.GET.get("next", "")

    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)

        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        prefix = protocol + host

        if next.startswith(prefix):
            next = next[len(prefix):]

    return next


def _get_session(samlp):
    """ Recovers the session mapped with the CAS service ticket
    received in the SAML CAS request at CAS logout
    """

    tree = ET.fromstring(samlp)
    if tree[1].tag.endswith('SessionIndex'):
        ticket = tree[1].text
    sst = SessionServiceTicket.get_by_id(ticket)
    if not sst:
        logger.error('cant find sst for ticket %s' % ticket)
        return None
    return sst.get_session()


def getCasKey(email):
    return 'CAS:{}'.format(email)


def single_sign_out(request, next_page=None):
    ticket = request.POST.get('logoutRequest')
    if ticket:
        request.session = _get_session(ticket)
        request.user = auth.get_user(request)
        logger.debug(
            "Got single sign out callback from CAS for user %s session %s",
            request.user, request.session.session_key)
    auth.logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    return HttpResponseRedirect(_logout_url(request, next_page))


def get_user_group_model():
    """
        Return the UserGroup model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.USER_GROUP_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("USER_GROUP_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "USER_GROUP_MODEL refers to model '%s' that has not been installed" % settings.USER_GROUP_MODEL
        )


if django.VERSION < (1, 11):
    def is_authenticated(user):
        return user.is_authenticated()
else:
    def is_authenticated(user):
        return user.is_authenticated
