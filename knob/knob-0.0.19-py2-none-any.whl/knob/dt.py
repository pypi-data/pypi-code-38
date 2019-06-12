# -*- coding:utf-8 -*-

import six
from django.utils import timezone


def local_now():
    return timezone.now().astimezone(timezone.get_default_timezone())


def local_today():
    return local_now().date()
