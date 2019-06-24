# -*- coding:utf-8 -*- 
__author__ = 'denishuang'


class ResourceRegister(object):
    def __init__(self):
        self.reg_map = {}

    def register(self, content_type, func):
        self.reg_map[content_type] = func

    def verify(self, content_type, user, ids):
        if content_type not in self.reg_map:
            raise KeyError(u'%s not registered yet.' % content_type)
        func = self.reg_map[content_type]
        return func(content_type, user, ids)
