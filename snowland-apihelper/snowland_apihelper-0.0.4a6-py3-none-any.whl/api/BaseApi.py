#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: BaseApi.py
# @time: 2018/6/19 10:37
# @Software: PyCharm


from abc import abstractmethod, ABCMeta


class BaseApi(ABCMeta):
    @abstractmethod
    def action(self, *args, **kwargs):
        pass
