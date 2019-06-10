#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: HelloWorldHandler.py
# @time: 2018/6/19 10:53
# @Software: PyCharm

from apihelper.handlers import BaseHandler
from apihelper.api.HelloworldApi import HelloWorld


class HelloWorldHandler(BaseHandler):
    def get(self):
        BaseHandler.get(self, target=HelloWorld)
