# -*- coding: utf-8 -*-
# author: pengr

from . import util
from .constants import non
import re


class BaseUDF(object):
    # 用户自定义函数
    # 结果数据集格式为二维列表
    def evaluate(self, *args, **kwargs):
        raise NotImplementedError()


class TestUDF(BaseUDF):
    # UDF测试用例
    def evaluate(self, *args, **kwargs):
        print('test udf and params is arg: '+args)


class IsNonDataUDF(BaseUDF):
    # 统计数据集中空数据条目/所占比例
    def evaluate(self, *items):
        res = []
        for item in items:
            if util.isBlank(item):
                res.append(non)
            else:
                res.append(item)
        return res


class PerfectionUDF(BaseUDF):
    # 统计数据集中空数据条目/所占比例
    def evaluate(self,  *items, nrows):
        res = [count/nrows for count in items]
        res.append(sum(res)/len(res))
        return res


class GetDateColumns(BaseUDF):
    # 判断列是否为日期列

    __dateKey = ['update', 'create', 'time', '时间', '日期', 'date']

    def evaluate(self, *cols):
        res = set()
        for col in cols:
            if not col:
                continue
            for key in self.__dateKey:
                if key in str(col):
                    res.add(cols.index(col))
            if isinstance(col, int) and 1971 < col < 2050:
                res.add(cols.index(col))
            if re.search('^(^(\d{4}|\d{2})(\-|\/|\.)\d{1,2}\3\d{0,2})|(^\d{4}年\d{1,2}月\d{0,2}日*)', str(col)):
                res.add(cols.index(col))
        return [list(res)]


class IsTruthDateFormatUDF(BaseUDF):

    # 统计日期格式

    def evaluate(self, *cols, format):
        res = []
        for col in cols:
            if util.isDateTrueFormat(col, format=format):
                res.append(col)
            else:
                res.append(non)
        return res


class DropInvalidColumnsUDF(BaseUDF):
    # 取出无效数据列
    def evaluate(self, *items):
        last = len(items)-1
        while util.isBlank(items[last]) and last >= 0:
            last -= 1
        res = list(items[:last])
        return res


# if __name__ == '__main__':
#     print(100)
#     for i in range(10,0, -1):
#         print(i)
