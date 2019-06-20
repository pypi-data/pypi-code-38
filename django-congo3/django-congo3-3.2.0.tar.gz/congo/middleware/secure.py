# -*- coding: utf-8 -*-
from congo.conf import settings
from django.http.response import HttpResponsePermanentRedirect
from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin

class ForceCsrfCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        get_token(request)

        # @OG SECURE_SSL_REDIRECT - zmienic na djangowe rozwiazanie
