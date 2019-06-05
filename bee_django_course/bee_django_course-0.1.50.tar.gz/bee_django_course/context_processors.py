#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.conf import settings


def get_user_name(request):
    if not request.user.is_authenticated():
        name = '匿名用户'
    else:
        if settings.COURSE_USER_NAME:
            name = getattr(request.user, settings.COURSE_USER_NAME)
            if not name:
                name = request.user.username
        else:
            name = request.user.username

    context = {
        'user_name': name,
    }

    return context
