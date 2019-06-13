"""CAS authentication backend"""

import logging
from six.moves.urllib_parse import urlencode, urljoin
import requests
from django.contrib.auth import get_user_model


try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree
logger = logging.getLogger('cas')
__all__ = ['CASBackend']


def _internal_verify_cas(ticket, service, cas_url, suffix='proxyValidate'):
    """Verifies CAS 2.0 and 3.0  XML-based authentication ticket.

    Returns username on success and None on failure.
    """

    params = {'ticket': ticket, 'service': service}

    url = (urljoin(cas_url, suffix) + '?' + urlencode(params))

    response = requests.get(url, verify=False).text
    logger.debug('url is {}\nresponse is {}'.format(url, response))
    tree = ElementTree.fromstring(response)

    if tree[0].tag.endswith('authenticationSuccess'):
        return tree[0][0].text
    return None


_verify = _internal_verify_cas


class CASBackend(object):
    """CAS authentication backend"""

    supports_object_permissions = False
    supports_inactive_user = False

    def authenticate(self, *args, ticket=None, service=None, cas_url=None):
        """Verifies CAS ticket and gets or create User object
            NB: Use of PT to identify proxy
        """

        email = _verify(ticket, service, cas_url)
        user_model = get_user_model()
        if not email:
            return None
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            logger.debug('email:{} 所对应用户不存在'.format(email))
            return None
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
