#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: manage.py
# @time: 2018/6/19 9:51
# @Software: PyCharm

import tornado.ioloop
import tornado.web
import tornado.httpserver
import os
from apihelper.thirdparty.tornadows import webservices
import warnings
from migrate.versioning import api
import os.path
import datetime
import apihelper
from tornado.options import parse_config_file
from apihelper.oauth import GoogleOAuth2Mixin


class SnowlandOAuth2LoginHandler(tornado.web.RequestHandler,
                                 GoogleOAuth2Mixin):
    raise NotImplementedError

    async def get(self):
        if self.get_argument('code', False):
            access = await self.get_authenticated_user(
                redirect_uri='http://127.0.0.1:10120/auth/google',
                code=self.get_argument('code'))
            user = await self.oauth2_request(
                "https://account.snowland.ltd/oauth2/v1/userinfo",
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
