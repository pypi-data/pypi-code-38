#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'StopWords'
__author__ = 'JieYuan'
__mtime__ = '2019-05-16'
"""
from ...pipe import get_module_path

import jieba.posseg as jp


class WordExtractor(object):

    def __init__(self):
        self.stopwords = self.stopwords()

    def words(self, sent, flags=None):
        """
        :flags mode: ['v', 'vn']
        """
        for p in jp.cut(sent.lower()):
            if p.flag in flags:
                yield p.word

    def noun(self, sent, with_flag=False):
        for p in jp.cut(sent.lower()):
            if 'n' in p.flag and len(p.word) > 1 and p.word not in self.stopwords:
                yield p if with_flag else p.word

    def stopwords(self):
        with open(get_module_path('./stop_words.txt', __file__), encoding='utf8') as f:
            return set(f.read().split())