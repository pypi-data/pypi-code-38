# -*- coding: utf-8 -*-
# author: pengr

from datacommon.util import createInstance
from datacommon.constants import non
import hashlib

# 对相应的类容执行函数


class DataSet(object):

    def __init__(self, data, nrows=None, ncols=None):
        # 初始化数据集必须为二维列表
        self.__nrows = len(data) if not nrows else nrows
        self.__ncols = len(data[0]) if not ncols else ncols
        self.__data = data
        fill_flag = False
        if not ncols:
            for row in data:
                fill_flag = True if len(
                    row) != self.__ncols else False or fill_flag
                if len(row) > self.__ncols:
                    self.__ncols = len(row)
        if fill_flag:
            self.__fill(self.__nrows, self.__ncols)

    def runUDF(self, UDfunc, *cols, **kwargs):
        moduleName = kwargs['module'] if 'module' in kwargs else 'datacommon.udfs'
        UDfunc = createInstance(moduleName, UDfunc)
        cols = self.__check(cols)
        items = []
        for row in self.__data:
            params = []
            for col in cols:
                params.append(row[col])
            items.append(UDfunc.evaluate(*params, **kwargs))
        new_task = DataSet(items)
        return new_task

    def filterNonData(self, col):
        items = []
        for item in self.__data:
            if item[col] != non:
                items.append(item[col])

        new_task = DataSet(items)
        return new_task

    def distinct(self, *cols):
        cols = self.__check(cols)
        tempSet = set()
        repestIndex = set()
        for rowIndex in range(len(self.__data)):
            row = self.__data[rowIndex]
            digest = self.__digest([row[col] for col in cols])
            if digest in tempSet:
                repestIndex.add(rowIndex)
            else:
                tempSet.add(digest)
        new_task = DataSet([self.__data[i] for i in range(len(self.__data)) if i not in repestIndex])
        return new_task

    def count(self, *cols):
        cols = self.__check(cols)
        res = [0 for col in cols]
        for item in self.__data:
            for idx in range(len(cols)):
                res[idx] = res[idx]+1 if item[cols[idx]
                                              ] != non else res[idx]

        new_task = DataSet([res])
        return new_task

    def min(self, *cols):
        cols = self.__check(cols)
        res = [non for col in cols]
        for item in self.__data:
            for idx in range(len(cols)):
                res[idx] = item[cols[idx]] if res[idx] == non or item[cols[idx]
                                                                      ] < res[idx] else res[idx]

        new_task = DataSet([res])
        return new_task

    def max(self, *cols):
        cols = self.__check(cols)
        res = [non for col in cols]
        for item in self.__data:
            for idx in range(len(cols)):
                res[idx] = item[cols[idx]] if res[idx] == non or item[cols[idx]
                                                                      ] > res[idx] else res[idx]

        new_task = DataSet([res])
        return new_task

    @property
    def data(self):
        return self.__data

    @property
    def nrows(self):
        return self.__nrows

    @property
    def ncols(self):
        return self.__ncols

    def __str__(self):
        res = '<DataSet object \'s data>: {}行, {}列\n'.format(
            self.__nrows, self.__ncols)
        for item in self.__data:
            res += ', '.join([str(i) for i in item]) + '\n'
        return res

    def __check(self, param_cols):
        if param_cols and len(param_cols) > 0:
            return param_cols
        return [i for i in range(self.__ncols)]

    def __digest(self, obj):
        md5 = hashlib.md5()
        md5.update(obj.__str__().encode('utf-8'))
        return md5.hexdigest()[8:-8]

    def __fill(self, nrows, ncols):
        while len(self.__data) < nrows:
            self.__data.append([])
        for row_item in self.__data:
            while len(row_item) < ncols:
                row_item.append(non)


if __name__ == '__main__':
    numberData = [
        [1, 2, 3, 4, 5],
        [2, 4, 6, 8, 10],
        [3, 6, 9, 12, 4]
    ]

    stringData = [
        ['asda', 'asda', 'dwqwe', 'qweq'],
        ['weqcas', 'defsw', 'deqwa', 'ewqwq'],
        ['weqcas', 'defsw', 'deqwa', 'ewqwq']
    ]

    nonTestData = [
        ['asda'],
        ['weqcas', 'defsw', 'deqwa', 'ewqwq'],
        [non, 'none', 'null']
    ]

    task3 = DataSet(stringData)
    print(task3.distinct())

    # task1 = DataSet(numberData)
    # task1.min(1, 3)
    # print(task1)

    # task2 = DataSet(nonTestData)
    # task2.count(0, 1, 2, 3)
    # print(task2)
    # print(task2.count(0, 1, 2, 3).runUDF('PerfectionUDF', nrows=task2.nrows))
