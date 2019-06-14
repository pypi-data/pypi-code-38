#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.contrib.auth import get_user_model
from .utils import get_user_feed

user_model = get_user_model()


# 获取班级同学
def get_classmates(user_id):
    return user_model.objects.order_by('-created_at')


# 获取学生发表日志数
def get_user_feed_count(user, start_dt=None, end_dt=None):
    return get_user_feed(user, start_dt, end_dt).count()

def get_feed_user_name_field():
    return u'publisher__first_name'