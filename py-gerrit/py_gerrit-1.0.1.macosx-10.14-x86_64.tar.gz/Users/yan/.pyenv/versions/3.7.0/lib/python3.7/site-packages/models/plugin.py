# -*- coding: utf-8 -*-
# @Time    : 19-5-15 下午3:47
# @Author  : allen.you
from utils.util.jsonModel import jsonModel


@jsonModel()
class Plugin(object):
    def __init__(self):
        self.id = ''
        self.version = ''
        self.status = ''
        self.filename = ''
        self.index_url = ''


    def __repr__(self):
        return 'Plugin Name: %s, Version: %s' % (self.id, self.version)
