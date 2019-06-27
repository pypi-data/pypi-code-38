#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/28
import json

from libs.utils import JSONEncoder


class Page(object):

    def __init__(self, pageNum=1, pageSize=20, needCount=False, reasonable=True):
        """
        分页查询结果对象
        :param pageNum: 页数
        :param pageSize: 分页大小
        :param needCount: 需不需要进行总数查询
        :param reasonable: 分页合理化
        """
        if reasonable:
            self.pageNum = pageNum if pageNum > 0 else 1
            self.pageSize = pageSize if pageSize > 0 else 20
        else:
            self.pageNum = pageNum
            self.pageSize = pageSize
        # 进不进行count查询
        self.needCount = needCount
        self.result = None
        self.total = None

    @property
    def start_row(self):
        return (self.pageNum-1)*self.pageSize

    @property
    def end_row(self):
        return self.start_row + self.pageSize*self.pageNum

    def need_count(self):
        return self.needCount

    def set_result(self, result: list, total: int):
        self.result = result
        self.total = total

    def to_json(self):
        return {
            'pageNum': self.pageNum,
            'pageSize': self.pageSize,
            'needCount': self.needCount,
            'total': self.total,
            'result': self.result
        }

    @staticmethod
    def no_page(result: list):
        """
        不进行分页时，返回的page对象
        :param result:
        :return:
        """
        page = Page(0, 0, False, False)
        page.set_result(result, -1)
        return page

    def __repr__(self):
        return json.dumps(self.to_json(), cls=JSONEncoder)

