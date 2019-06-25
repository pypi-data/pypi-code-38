#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21


class SqlWrap(object):
    """
    存放sql构造结果包含sql和参数
    sql 是这种 INSERT  INTO `projectdb`(`name`,`group`,`status`) VALUES (:name, :group, :status)
    param 就是与dict对应的参数
    """

    def __init__(self, sql: str, param: dict):
        self._sql = sql
        self._param = param

    @property
    def sql(self):
        return self._sql

    @property
    def param(self):
        return self._param
