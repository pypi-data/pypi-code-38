# -*- coding: utf-8 -*-
# author: pengr


class NonData():
    # 空数据对象
    __fillvalue = '<NonData object>'

    @property
    def fillvalue(self):
        return self.__fillvalue

    @fillvalue.setter
    def fillValue(self, value):
        self.__fillvalue = value

    def __str__(self):
        return self.__fillvalue


class LastColumn():

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


non = NonData()
