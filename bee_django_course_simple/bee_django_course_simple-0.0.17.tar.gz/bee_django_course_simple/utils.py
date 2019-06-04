#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import json,pytz
from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from django.http import HttpResponse
from datetime import datetime
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')




class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")

# ====dt====
# 获取本地当前时间
def get_now(tz=LOCAL_TIMEZONE):
    return datetime.now(tz)


def page_it(request, query_set, url_param_name='page', items_per_page=25):
    paginator = Paginator(query_set, items_per_page)

    page = request.GET.get(url_param_name)
    try:
        rs = paginator.page(page)
    except PageNotAnInteger:
        rs = paginator.page(1)
    except EmptyPage:
        rs = paginator.page(paginator.num_pages)

    return rs

def get_user_model():
    if settings.COIN_USER_TABLE in ["", None]:
        user_model = User
    else:
        app_name = settings.COIN_USER_TABLE.split(".")[0]
        model_name = settings.COIN_USER_TABLE.split(".")[1]
        app = apps.get_app_config(app_name)
        user_model = app.get_model(model_name)
    return user_model


# 获取登录用户
def get_login_user(request):
    if settings.COIN_USER_TABLE in ["", None]:
        return request.user

    token = request.COOKIES.get('cookie_token', '')
    # 没有登录
    if not token:
        return None

    try:
        user_table = get_user_model()
        user = user_table.objects.get(token=token)
        return user
    except:
        return None


# 获取自定义user的自定义name
def get_user_name(user):
    try:
        return getattr(user, settings.COIN_USER_NAME_FIELD)
    except:
        return None

def get_default_name():
    return settings.COIN_DEFAULT_NAME