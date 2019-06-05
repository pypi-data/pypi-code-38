import re
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

from djangoldp_account.errors import WebFingerError

ACCT_RE = re.compile(
    r'(?:acct:)?(?P<userinfo>[\w.!#$%&\'*+-/=?^_`{|}~]+)@(?P<host>[\w.:-]+)')


class Acct(object):
    def __init__(self, acct):
        m = ACCT_RE.match(acct)
        if not m:
            raise ValueError('invalid acct format')
        (userinfo, host) = m.groups()
        self.userinfo = userinfo
        self.host = host


class WebFingerEndpoint(object):
    """
    WebFinger endpoint
    See https://tools.ietf.org/html/rfc7033
    """
    client_class = Client

    def __init__(self, request):
        self.request = request
        self.params = {}
        self.acct = None

        self._extract_params()
        self.client = self.client_class(client_authn_method=CLIENT_AUTHN_METHOD)

    def _extract_params(self):
        # Because in this endpoint we handle both GET
        # and POST request.
        query_dict = (self.request.POST if self.request.method == 'POST'
                      else self.request.GET)

        self.params['resource'] = query_dict.get('resource', None)
        self.params['rel'] = query_dict.get('rel', '')

    def validate_params(self):
        """
        A resource must be set.
        """

        if self.params['resource'] is None:
            raise WebFingerError('invalid_request')

        try:
            self.acct = Acct(self.params['resource'])
        except ValueError:
            raise WebFingerError('invalid_acct_format')

    def response(self):
        """
        This endpoint only reply to rel="http://openid.net/specs/connect/1.0/issuer"
        :return: a dict representing the Json response
        """

        dict = {
            'subject': self.params['resource'],
            'links': []
        }

        if "http://openid.net/specs/connect/1.0/issuer" in self.params['rel']:
            user = get_user_model().objects.filter(email="{}@{}".format(self.acct.userinfo, self.acct.host)).first()
            if user is not None:
                url = urlparse(user.webid())
                if user.account.issuer is None:
                    href = "{}://{}".format(url.scheme, url.netloc)
                else:
                    href = user.account.issuer

                dict['links'].append({
                    'rel': "http://openid.net/specs/connect/1.0/issuer",
                    'href': href
                })

        return dict
