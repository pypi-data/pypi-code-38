# -*- coding: utf-8 -*-
__author__ = '陈章'
__date__ = '2019-04-25 11:27'
import hashlib


class Md5:
    @classmethod
    def get_md5(cls, url):
        if isinstance(url, str):
            url = url.encode('utf-8')
        md5 = hashlib.md5()
        md5.update(url)
        return md5.hexdigest()


get_md5 = Md5.get_md5
