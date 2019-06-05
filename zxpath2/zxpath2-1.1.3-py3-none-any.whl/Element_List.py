# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    Element_List.py
   Author :       Zhang Fan
   date：         2018/11/3
   Description :
-------------------------------------------------
"""
__author__ = 'Zhang Fan'


class Element_List(list):

    @property
    def empty(self):
        return len(self) == 0

    def is_empty(self):
        return len(self) == 0

    @property
    def string(self):
        return self.get_string()

    @property
    def text(self):
        return self.get_text()

    @property
    def string_list(self):
        return self.get_string_list()

    @property
    def text_list(self):
        return self.get_text_list()

    def get_string(self, join_str='\t', strip=True):
        return join_str.join(self.get_string_list(strip=strip))

    def get_text(self, join_str='\t', strip=True):
        return join_str.join(self.get_text_list(strip=strip))

    def get_string_list(self, strip=True):
        if not strip:
            return [node.string for node in self if node.string]

        values = []
        for node in self:
            text = node.string.strip()
            if text:
                values.append(text)
        return values

    def get_text_list(self, strip=True):
        if not strip:
            return [node.text for node in self if node.text]

        values = []
        for node in self:
            text = node.text.strip()
            if text:
                values.append(text)
        return values

    def __str__(self):
        return str([str(node) for node in self])
