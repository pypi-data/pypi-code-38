# -*- coding:utf-8 -*-

import six
import json


def get_request_para(request, parsers=None, defaults=None):
    para = {}
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            json_str = request.body.decode('utf-8') if six.PY3 else request.body
            json_para = json.loads(json_str, strict=False)
            if isinstance(json_para, dict):
                para.update(json_para)
        except Exception as e:
            pass
    para.update(request.GET.dict())

    if parsers:
        for k, parser in six.iteritems(parsers):
            if callable(parser) and k in para:
                para[k] = parser(para[k])

    if defaults:
        for k, v in six.iteritems(defaults):
            para.setdefault(k, v)

    return para


def get_ip(request):
    if request.META.has_key('HTTP_X_REAL_IP'):
        return request.META['HTTP_X_REAL_IP']
    else:
        return request.META['REMOTE_ADDR']

