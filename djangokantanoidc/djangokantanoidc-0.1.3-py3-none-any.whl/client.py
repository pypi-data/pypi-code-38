# -*- condig: utf8 -*-
from logging import getLogger
from django.conf import settings
from django.utils import module_loading
from urllib import parse
import requests
import base64
import json
import time
from .errors import IdTokenVerificationError


__all__ = ['client']
logger = getLogger(__name__)


AUTH_SERVER = getattr(settings, 'KAOC_SERVER', '')
CLIENT_ID = getattr(settings, 'KAOC_CLIENT_ID', '')
CLIENT_SECRET = getattr(settings, 'KAOC_CLIENT_SECRET', '')
CONFIG_PATH = '/.well-known/openid-configuration'
client = None


class KaocClient(object):

    def __init__(self, aep, tep, uep):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.authorization_endpoint = aep
        self.token_endpoint = tep
        self.userinfo_endpoint = uep
        if hasattr(settings, 'KAOC_EXTENDER'):
            Extender = module_loading.import_string(settings.KAOC_EXTENDER)
            self.extender = Extender()
        else:
            self.extender = None

    def prepare(self, request):
        if self.extender is None:
            return
        self.extender.prepare(request)

    def build_starturl(self, redirect_uri, stored_nonce, stored_state):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid email',
            'nonce': stored_nonce,
            'state': stored_state,
        }
        if self.extender and hasattr(self.extender, 'acr_values'):
            if self.extender.acr_values():
                params['acr_values'] = self.extender.acr_values()
        return (
            '%s?%s' % (self.authorization_endpoint, parse.urlencode(params))
        )

    def build_nexturl(self, request):
        if self.extender is None:
            return settings.LOGIN_REDIRECT_URL
        else:
            return self.extender.build_nexturl(request)

    def get_sub(self, redirect_uri, code, stored_nonce):
        token = self.__get_token(redirect_uri, code, stored_nonce)
        userinfo = self.__get_userinfo(token)
        return userinfo['sub']

    def __get_token(self, redirect_uri, code, stored_nonce):
        r = requests.post(
            url=self.token_endpoint,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': redirect_uri,
            }
        )
        asobject = r.json()
        id_token = asobject['id_token']
        self.__verify_id_token(id_token, stored_nonce)
        return asobject['access_token']

    def __get_userinfo(self, token):
        r = requests.get(
            url=self.userinfo_endpoint,
            params={'access_token': token}
        )
        return r.json()

    def __verify_id_token(self, id_token, stored_nonce):
        payload = id_token.split('.')[1]
        surplus = len(payload) % 4
        if surplus > 0:
            payload += ('=' * (4 - surplus))
        asobject = json.loads(base64.b64decode(payload.encode()))
        logger.debug('%s', asobject)
        if (self.client_id != asobject['aud']):
            raise IdTokenVerificationError('aud <> client_id')
        if (stored_nonce != asobject['nonce']):
            raise IdTokenVerificationError('nonce <> stored_nonce')
        if (time.time() > asobject['exp']):
            raise IdTokenVerificationError('now > exp')
        if self.extender and hasattr(self.extender, 'verify_id_token'):
            self.extender.verify_id_token(asobject)


def initmod():
    global client
    if not AUTH_SERVER:
        logger.warn('AUTH_SERVER is falsy, Skip initial configration.')
        return
    r = requests.get(
        url=(AUTH_SERVER + CONFIG_PATH),
    )
    asobject = r.json()
    client = KaocClient(
        asobject['authorization_endpoint'],
        asobject['token_endpoint'],
        asobject['userinfo_endpoint']
    )


initmod()
