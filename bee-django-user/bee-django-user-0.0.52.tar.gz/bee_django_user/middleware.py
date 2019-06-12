# -*- coding:utf-8 -*-

import re

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
# from bee_django_weixin.exports import token_auth


class RequireLoginMiddleware(object):
    """
    Middleware component that wraps the login_required decorator around
    matching URL patterns. To use, add the class to MIDDLEWARE_CLASSES and
    define LOGIN_REQUIRED_URLS and LOGIN_REQUIRED_URLS_EXCEPTIONS in your
    settings.py. For example:
    ------
    LOGIN_REQUIRED_URLS = (
        r'/topsecret/(.*)$',
    )
    LOGIN_REQUIRED_URLS_EXCEPTIONS = (
        r'/topsecret/login(.*)$',
        r'/topsecret/logout(.*)$',
    )
    ------
    LOGIN_REQUIRED_URLS is where you define URL patterns; each pattern must
    be a valid regex.

    LOGIN_REQUIRED_URLS_EXCEPTIONS is, conversely, where you explicitly
    define any exceptions (like login and logout URLs).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.required = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS)
        self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # No need to process URLs if user already logged in
        if request.user.is_authenticated():
            return None

        # An exception match should immediately return None
        for url in self.exceptions:
            if url.match(request.path):
                return None


        # weixin token auth
        # auth_code = request.META.get('HTTP_AUTHORIZATION', None)
        # if auth_code:
        #     token_user = token_auth(auth_code)
        #     if token_user:
        #         request.token_user = token_user
        #         return None
        #     else:
        #         return JsonResponse(data={
        #             'rc': -1,
        #             'msg': u'授权失败',
        #         })

        # Requests matching a restricted URL pattern are returned
        # wrapped with the login_required decorator
        for url in self.required:
            if url.match(request.path):
                return HttpResponseRedirect(settings.LOGIN_URL)

        # Explicitly return None for all non-matching requests
        return None
