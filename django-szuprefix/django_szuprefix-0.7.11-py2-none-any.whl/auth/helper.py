# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals


def gen_permissions_map(permissions):
    m = {}
    for p in permissions:
        app, pn = p.split('.')
        fs = pn.split('_')
        model = fs[-1]
        action = '_'.join(fs[:-1])
        am = m.setdefault(app, {})
        mm = am.setdefault(model, {})
        mm[action] = 1
    return m
