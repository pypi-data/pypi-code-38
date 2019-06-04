#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

import os
from django.core.exceptions import ValidationError
from utils import get_max_sn
from .models import UserSN


def user_sn_validator(value):
    sn = int(value)
    sn_list = UserSN.objects.filter(is_used=True).order_by('start')
    if not sn_list.exists():
        raise ValidationError(u'缦客号区间设置错误')
    _sn = sn_list.first()
    end = _sn.end
    max_sn = get_max_sn()
    if sn < end and sn > max_sn:
        raise ValidationError(u'超过最大值')
