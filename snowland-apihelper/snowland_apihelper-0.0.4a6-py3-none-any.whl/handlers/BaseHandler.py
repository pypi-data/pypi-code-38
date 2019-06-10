#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: BaseHandler.py
# @time: 2018/6/19 10:22
# @Software: PyCharm

import tornado.web
from apihelper.api import BaseApi
from tornado.escape import json_encode
from apihelper.response.BaseResponse import response_json
from copy import deepcopy


class BaseHandler(tornado.web.RequestHandler):
    def get(self, target: BaseApi =None):
        assert target
        kwargs = {str(k): str(v[0], encoding='utf8') for k, v in self.request.query_arguments.items()}
        res_dict = deepcopy(response_json)
        res_dict['data'] = deepcopy(target.action(self, **kwargs))
        respon_json = json_encode(res_dict)
        self.write(respon_json)
        self.finish()

    def post(self, target: BaseApi =None):
        assert target
        kwargs = {str(k): str(v[0], encoding='utf8') for k, v in self.request.query_arguments.items()}
        res_dict = deepcopy(response_json)
        res_dict['data'] = deepcopy(target.action(self, **kwargs))
        respon_json = json_encode(res_dict)
        self.write(respon_json)
        self.finish()

