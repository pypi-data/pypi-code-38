#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: language.py
# @time: 2019/3/22 14:38
# @Software: PyCharm

# 此代码改自 https://gitee.com/garth/django-cms/blob/master/cms/middleware/language.py
# 原项目为BSD-3开源协议

__author__ = 'A.Star'


import datetime
from snowland_djangohelper.settings import LANGUAGE_SESSION_KEY
from django.utils.translation import get_language
from django.conf import settings


class LanguageCookieMiddleware(object):
    def process_response(self, request, response):
        language = get_language()
        if hasattr(request, 'session'):
            session_language = request.session.get(LANGUAGE_SESSION_KEY, None)
            if session_language and not session_language == language:
                request.session[LANGUAGE_SESSION_KEY] = language
                request.session.save()
        if settings.LANGUAGE_COOKIE_NAME in request.COOKIES and \
                        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] == language:
            return response
        max_age = 365 * 24 * 60 * 60  # 10 years
        expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language, expires=expires)
        return response
