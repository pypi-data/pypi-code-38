#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/11


class SimpleNode(object):
    def __int__(self, id: str=None, group: str=None, type: str=None, resourceId: str=None, tags: str=None):
        self.__id = id
        self.__group = group
        self.__type = type
        self.__resourceId = resourceId
        self.__tags = tags

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value: str):
        self.__id = value

    @property
    def group(self):
        return self.__group

    @group.setter
    def group(self, value: str):
        self.__group = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value: str):
        self.__type = value

    @property
    def resourceId(self):
        return self.__resourceId

    @resourceId.setter
    def resourceId(self, value: str):
        self.__resourceId = value

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, value: str):
        self.__tags = value