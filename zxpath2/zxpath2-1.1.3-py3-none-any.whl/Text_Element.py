# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    Text_Element.py
   Author :       Zhang Fan
   date：         2018/11/3
   Description :
-------------------------------------------------
"""
__author__ = 'Zhang Fan'

from zxpath2 import base_library


class Text_Element(str):

    def __init__(self, value=''):
        self.base = value
        self.name = 'text'
        super().__init__()

    @property
    def string(self):
        return self

    @property
    def text(self):
        return self

    @property
    def is_element(self):
        return base_library.is_element(self.base)

    @property
    def is_node_element(self):
        return False

    @property
    def is_text_element(self):
        return base_library.is_text_element(self.base)

    @property
    def is_comment(self):
        return False

    def get_string(self):
        return self

    def get_text(self):
        return self

    def __getattr__(self, name):
        return None

    def __deepcopy__(self, *args, **kw):
        return self.base
