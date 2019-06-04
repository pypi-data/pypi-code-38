#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template

from django.contrib.auth.models import User, Group, Permission
from bee_django_user.exports import get_user_leave_status

register = template.Library()


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)


# 组是否有权限
@register.filter
def has_permission(group, permission_name):
    try:
        if group.permissions.get(codename=permission_name):
            return True
        return False
    except:
        return False


# 组是否有权限
@register.filter
def has_manage(user):
    try:
        if user.userprofile.has_group("管理员") or user.userprofile.has_group("客服") or user.userprofile.has_group("助教"):
            return True

    except:
        return False
    return False


# 本地化时间
# @register.filter
# def local_datetime(_datetime):
#     return filter_local_datetime(_datetime)

# 获取学生的请假状态
@register.simple_tag
def get_leave_status(user):
    status = get_user_leave_status(user)
    if status:
        return "请假中"
    return
