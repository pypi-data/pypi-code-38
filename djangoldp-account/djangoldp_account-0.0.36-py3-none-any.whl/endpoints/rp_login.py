from urllib.parse import urlparse

import validators
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.urls import reverse
from oic.exception import CommunicationError

from djangoldp.models import Model
from djangoldp_account.auth.backends import ExternalUserBackend
from djangoldp_account.errors import LDPLoginError
from djangoldp_account.models import OPClient
from oic import rndstr
from oic.oic import Client, AuthorizationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

from djangoldp_account.auth.solid import Solid
from djangoldp_account.errors import LDPLoginError
from djangoldp_account.models import OPClient


class RPLoginEndpoint(object):
    """
    RP login endpoint
    This is *not* the OP login endpoint (OP part is managed by django_oidc)
    """
    client_class = Client

    def __init__(self, request):
        self.request = request
        self.params = {}

        self._extract_params()
        self.client = self.client_class(client_authn_method=CLIENT_AUTHN_METHOD)

    def _extract_params(self):
        """
        """
        # Because in this endpoint we handle both GET
        # and POST request.
        query_dict = (self.request.POST if self.request.method == 'POST'
                      else self.request.GET)

        self.params['subject'] = query_dict.get('subject', '')
        self.params['next'] = query_dict.get('next', '')

    def validate_params(self):
        """
        A provider must be set.
        It can be a url (auth provider)
        or email or webId (In those case, provider discovery is necessary)

        See: 2.1 https://github.com/solid/webid-oidc-spec/blob/master/example-workflow.md
        """

        if not validators.url(self.params['subject']) and not validators.email(self.params['subject']):
            raise LDPLoginError('invalid_request')

    def op_login_url(self):
        subject = self.params['subject']
        redirect_uris = [settings.SITE_URL + reverse('oidc_login_callback'), settings.SITE_URL]
        provider_info = None
        try:
            issuer = self.client.discover(subject)
            provider_info = self.client.provider_config(issuer)
        except:
            pass

        if provider_info is None:
            provider_info = self.check_on_known_providers(subject)

        if provider_info is None and subject.startswith("http"):
            # assume that the subject is the provider
            try:
                provider_info = self.client.provider_config(subject)
            except CommunicationError as error:
                pass

        if provider_info is None:
            raise LDPLoginError(error="cannot_get_provider_info")

        existing_op_client = OPClient.objects.filter(issuer=provider_info._dict['issuer']).first()
        if existing_op_client is None:
            try:
                registration_endpoint = provider_info._dict["registration_endpoint"]
                args = {
                    "client_name": settings.SITE_URL,
                    "response_types": ["code"],
                    "redirect_uris": redirect_uris,
                }

                registration_response = self.client.register(
                    registration_endpoint, **args)

                OPClient.objects.create(issuer=provider_info._dict['issuer'],
                                        client_id=self.client.client_id,
                                        client_secret=registration_response['secret'])
            except:
                raise LDPLoginError(error="cannot_register")
        else:
            self.client.client_id = existing_op_client.client_id

        self.request.session['nonce'] = rndstr()
        self.request.session['state'] = rndstr()
        self.request.session['next'] = self.params['next']
        self.request.session['client_id'] = self.client.client_id
        self.request.session['issuer'] = provider_info._dict['issuer']

        args = {
            "client_id": self.client.client_id,
            "response_type": ["code"],
            "scope": ["openid profile webid email"],
            "nonce": self.request.session['nonce'],
            "redirect_uri": redirect_uris[0],
            "state": self.request.session['state']
        }

        auth_req = self.client.construct_AuthorizationRequest(request_args=args)
        return auth_req.request(self.client.authorization_endpoint)

    def check_on_known_providers(self, subject):
        provider_info = None
        for opclient in OPClient.objects.all():
            try:
                provider_info = self.client.discover(subject, urlparse(opclient.issuer).netloc)
                if provider_info is not None:
                    break
            except:
                pass
        return provider_info


class RPLoginCallBackEndpoint(object):
    """
    RL login callback endpoint
    """
    client_class = Client

    def __init__(self, request):
        self.request = request
        self.params = {}

        self.client = self.client_class(client_authn_method=CLIENT_AUTHN_METHOD)
        op_client = OPClient.objects.filter(issuer=self.request.session['issuer']).first()
        if op_client is None:
            raise LDPLoginError(error="wrong_issuer")

        self.client.client_id = op_client.client_id
        self.client.client_secret = op_client.client_secret

        try:
            provider_info = self.client.provider_config(self.request.session['issuer'])
        except:
            raise LDPLoginError(error="cannot_get_provider_info")
        self._extract_params()

    def _extract_params(self):
        query_string = self.request.environ["QUERY_STRING"]

        aresp = self.client.parse_response(AuthorizationResponse, info=query_string, sformat='urlencoded')
        self.params['state'] = aresp['state']
        self.params['code'] = aresp['code']

    def validate_params(self):
        if not self.params["state"] == self.request.session['state']:
            raise LDPLoginError(error='invalid_state')

    def initial_url(self):
        args = {
            "code": self.params["code"],
            "redirect_uri": settings.SITE_URL

        }
        resp = self.client.do_access_token_request(state=self.params["state"],
                                                   request_args=args,
                                                   authn_method="client_secret_basic")

        if 'error' in resp:
            raise LDPLoginError(dict=resp)

        userinfo = self.client.do_user_info_request(method='GET', state=self.params["state"])
        webid = self.extract_web_id(userinfo)
        Solid.confirm_webid(webid, self.client.issuer)
        user = Solid.get_or_create_user(userinfo, webid)
        login(self.request, user, backend='djangoldp_account.auth.backends.ExternalUserBackend')

        return self.request.session['next'] or settings.SITE_URL

    def extract_web_id(self, userinfo):
        """
        See https://github.com/solid/webid-oidc-spec/blob/master/README.md#method-1---custom-webid-claim
        :param userinfo:
        :return:
        """
        if 'webid' in userinfo:
            return userinfo["webid"]
        elif validators.url(userinfo['sub']):
            return userinfo['sub']
        elif 'website' in userinfo:
            return userinfo["website"]
        else:
            raise LDPLoginError('cannot_get_webid')

    def confirm_webid(self, webid):
        """
        See https://github.com/solid/webid-oidc-spec/blob/master/README.md#webid-provider-confirmation
        :param webid:
        :return:
        """
        url = urlparse(self.client.issuer)
        webid_url = urlparse(webid)
        if webid_url.netloc == url.netloc:
            pass
        else:
            raise LDPLoginError('cannot_confirm_webid')
        # TODO : add the other cases

    def login(self, userinfo, webid):
        if webid.startswith(settings.SITE_URL):
            existing_user = Model.resolve_id(userinfo['sub'][len(settings.SITE_URL):])
        else:
            try:
                existing_user = get_user_model().objects.get(username=webid)
            except get_user_model().DoesNotExist:
                existing_user = None
        if existing_user is not None:
            user = existing_user
        else:
            user = get_user_model().objects.create_user(username=webid,
                                                        first_name=userinfo['given_name'],
                                                        last_name=userinfo['family_name'],
                                                        email=userinfo['email'])
        user.account.issuer = self.client.issuer
        user.account.save()

        login(self.request, user, backend='djangoldp_account.auth.backends.ExternalUserBackend')
