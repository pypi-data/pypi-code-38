# -*- coding: utf-8 -*-

import inspect

from datetime import datetime

from django.conf import settings
from django.dispatch import receiver
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.signals import user_logged_in, user_logged_out

from bigtiger.core.exceptions import SuspiciousOperation
from bigtiger.contrib.log.signals import user_log_success, user_log_error


def load_backend(path):
    return import_string(path)()


def _get_backend():

    if not hasattr(settings, 'USER_LOG_BACKEND'):
        raise ImproperlyConfigured('USER_LOG_BACKEND')

    path = settings.USER_LOG_BACKEND
    backends = []

    def inn_get_backend():
        if len(backends) == 0:
            backends.append(load_backend(path))
        return backends[0]
    return inn_get_backend


# 使用闭包的目的是延迟加载backend。
get_backend = _get_backend()


def _record_log(user_id, action_flag, action_class, action_object, action_handler, ip, status, status_note):
    try:
        log = {
            'user_id': user_id,
            'action_flag': action_flag,
            'action_time': datetime.now(),
            'action_class': action_class,
            'action_object': action_object,
            'action_handler': action_handler,
            'ip': ip,
            'status': status,
            'status_note': status_note
        }

        backend = get_backend()
        try:
            inspect.getcallargs(backend.record, **log)
        except TypeError:
            return

        backend.record(**log)
    except Exception as e:
        print e


@receiver(user_log_success)
def user_log_success_callback(sender, request, action_class, action_object, action_handler, status_note=None, **kwargs):

    # 注意：用户修改密码成功后要清空session所以获取不到user.
    _record_log(request.user.id or 'None', 1, action_class, action_object,
                action_handler, request.META['REMOTE_ADDR'], 1, status_note)


@receiver(user_log_error)
def user_log_error_callback(sender, request, action_class, action_object, action_handler, status_note=None, **kwargs):

    _record_log(request.user.id, 1, action_class, action_object,
                action_handler, request.META['REMOTE_ADDR'], 2, status_note)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    _record_log(request.user.id, 0, '用户登陆', str(user), 'login',
                request.META['REMOTE_ADDR'], 1, '登陆成功。')


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    _record_log(request.user.id, 0, '用户登陆', str(user), 'logout',
                request.META['REMOTE_ADDR'], 1, '退出登陆成功。')
