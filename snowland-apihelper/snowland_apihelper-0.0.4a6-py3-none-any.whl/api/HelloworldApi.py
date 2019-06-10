#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: HelloworldApi.py
# @time: 2018/6/19 10:55
# @Software: PyCharm

from apihelper.api.BaseApi import BaseApi


class HelloWorld(BaseApi):
    def action(self, username="", *args, **kwargs):
        return username + ", hello, world!"
