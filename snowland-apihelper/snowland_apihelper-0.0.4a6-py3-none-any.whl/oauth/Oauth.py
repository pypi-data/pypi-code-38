#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: Oauth.py
# @time: 2019/2/11 21:28
# @Software: PyCharm

from __future__ import absolute_import, division, print_function
from base64 import b64encode
import urllib.parse as urllib_parse
import functools
import warnings

# from tornado.concurrent import (Future, _non_deprecated_return_future,
#                                 future_set_exc_info, chain_future,
#                                 future_set_result_unless_cancelled)
from tornado import escape
from tornado.auth import AuthError, OAuth2Mixin


class SnowlandMixin(OAuth2Mixin):
    raise NotImplementedError
    # TODO: 将在之后的版本重写
    warnings.warn('this class is not yet, it returns google oauth now')
    _OAUTH_AUTHORIZE_URL = "https://accounts.snowland.com/o/oauth2/v2/auth"
    _OAUTH_ACCESS_TOKEN_URL = "https://www.snowland.com/oauth2/v4/token"
    _OAUTH_USERINFO_URL = "https://www.snowland.com/oauth2/v1/userinfo"
    _OAUTH_NO_CALLBACKS = False
    _OAUTH_SETTINGS_KEY = b64encode(bytes.fromhex('b1d24c20b223c8e57c3da05ce831964eef9081969cffa9972d5a072e633f2860e2cf8920fdf84e960402254c0fd2d9706e973315580fa39b3eb5c4d4ea5548be'))

    # SM2 public key
    @_auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        """Handles the login for the Google user, returning an access token.

        The result is a dictionary containing an ``access_token`` field
        ([among others](https://developers.google.com/identity/protocols/OAuth2WebServer#handlingtheresponse)).
        Unlike other ``get_authenticated_user`` methods in this package,
        this method does not return any additional information about the user.
        The returned access token can be used with `OAuth2Mixin.oauth2_request`
        to request additional information (perhaps from
        ``https://www.googleapis.com/oauth2/v2/userinfo``)

        Example usage:

        .. testcode::

            class SnowlandOAuth2LoginHandler(tornado.web.RequestHandler,
                                           SnowlandOAuth2Mixin):
                async def get(self):
                    if self.get_argument('code', False):
                        access = await self.get_authenticated_user(
                            redirect_uri='http://your.site.com/auth/google',
                            code=self.get_argument('code'))
                        user = await self.oauth2_request(
                            "https://www.googleapis.com/oauth2/v1/userinfo",
                            access_token=access["access_token"])
                        # Save the user and access token with
                        # e.g. set_secure_cookie.
                    else:
                        await self.authorize_redirect(
                            redirect_uri='http://your.site.com/auth/google',
                            client_id=self.settings['google_oauth']['key'],
                            scope=['profile', 'email'],
                            response_type='code',
                            extra_params={'approval_prompt': 'auto'})

        .. testoutput::
           :hide:

        .. deprecated:: 5.1

           The ``callback`` argument is deprecated and will be removed in 6.0.
           Use the returned awaitable object instead.
        """  # noqa: E501
        http = self.get_auth_http_client()
        body = urllib_parse.urlencode({
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": self.settings[self._OAUTH_SETTINGS_KEY]['key'],
            "client_secret": self.settings[self._OAUTH_SETTINGS_KEY]['secret'],
            "grant_type": "authorization_code",
        })

        fut = http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                         method="POST",
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         body=body)
        fut.add_done_callback(functools.partial(self._on_access_token, callback))

    def _on_access_token(self, future, response_fut):
        """Callback function for the exchange to the access token."""
        try:
            response = response_fut.result()
        except Exception as e:
            future.set_exception(AuthError('Snowland auth error: %s' % str(e)))
            return

        args = escape.json_decode(response.body)
        # future_set_result_unless_cancelled(future, args)
