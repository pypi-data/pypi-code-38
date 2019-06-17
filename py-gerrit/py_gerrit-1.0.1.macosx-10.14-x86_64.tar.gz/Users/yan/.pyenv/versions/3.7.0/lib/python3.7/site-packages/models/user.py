# -*- coding: utf-8 -*-
# @Time    : 19-5-15 下午5:38
# @Author  : allen.you
from utils.jsonModel import jsonModel


@jsonModel()
class User(object):
    def __init__(self, ):
        self._account_id = ''
        self.username = ''
        self.name = ''
        self.email = ''

    def __repr__(self):
        return self.username
