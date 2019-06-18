# -*- coding:utf-8 -*-
from rest_framework.authentication import SessionAuthentication as OrgSessionAuthentication
__author__ = 'denishuang'

from rest_framework.settings import api_settings

DACS = api_settings.user_settings.get('DEFAULT_AUTHENTICATION_CLASSES')
USING_JWTA = 'rest_framework_simplejwt.authentication.JWTAuthentication' in DACS

class SessionAuthentication(OrgSessionAuthentication):
    def authenticate_header(self, request):
        return '/accounts/login/'
