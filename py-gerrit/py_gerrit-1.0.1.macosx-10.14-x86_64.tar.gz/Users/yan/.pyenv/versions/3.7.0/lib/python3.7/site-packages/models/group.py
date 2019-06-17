# -*- coding: utf-8 -*-
# @Time    : 19-5-21 下午6:14
# @Author  : allen.you
from utils.jsonModel import jsonModel


@jsonModel()
class Option(object):
    def __init__(self):
        pass


@jsonModel(objectMap={'options', Option})
class Group(object):
    def __init__(self):
        self.id = ''
        self.group_id = 0
        self.name = ''
        self.owner = ''
        self.owner_id = ''
        self.url = ''
        self.option = {}
        self.created_on = ''
        self.description = ''

    def __repr__(self):
        return 'Group Owner: %s, created_on: %s' % (self.owner, self.created_on)