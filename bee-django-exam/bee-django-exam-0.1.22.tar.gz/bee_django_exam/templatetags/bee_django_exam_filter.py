#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template
from django.shortcuts import get_object_or_404, reverse
from bee_django_exam.utils import get_user_name, get_user_exam_record
from bee_django_exam.exports import get_user_icon

register = template.Library()


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)


# 本地化时间
# @register.filter
# def local_datetime(_datetime):
#     return filter_local_datetime(_datetime)


# 获取报名学生的姓名
@register.filter
def get_record_user_name(user):
    if not user:
        return None
    return get_user_name(user.id)


@register.filter
def get_icon(user_id):
    return get_user_icon(user_id)


@register.simple_tag
def get_user_exam_record_link(user):
    record = get_user_exam_record(user,-1)
    if record:
        return reverse("bee_django_exam:user_exam_notice", kwargs={"user_record_id": record.id})
    else:
        return ""
