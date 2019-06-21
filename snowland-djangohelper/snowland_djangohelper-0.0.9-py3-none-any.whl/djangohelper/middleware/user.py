#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: middleware.py
# @time: 2018/8/13 18:43
# @Software: PyCharm
from django.utils.deprecation import MiddlewareMixin
from django.views.debug import technical_500_response
import sys


class UserBasedExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if request.user.is_superuser:
            return technical_500_response(request, *sys.exc_info())
