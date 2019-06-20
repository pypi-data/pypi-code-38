#!/usr/bin/python
# -*- coding: utf-8 -*-

from kdbase.singleton import singleton
from collections import defaultdict

# For unittest only
@singleton
class Manager(object):
    def __init__(self):
        self.__data = defaultdict(dict)

    def clear(self):
        self.__data = defaultdict(dict)

    def put_cols(self, table, row, cols): #(column_family, column, data)
        for column_family, column, content in cols:
            key = '%s:%s' % (table, row)
            subkey = '%s:%s' % (column_family, column)
            self.__data[key][subkey] = content
        return True

    def put_col(self, table, row, column_family, column, content):
        key = '%s:%s' % (table, row)
        subkey = '%s:%s' % (column_family, column)
        self.__data[key][subkey] = content
        return True

    def get_col(self, table, row, column_family, column):
        key = '%s:%s' % (table, row)
        subkey = '%s:%s' % (column_family, column)
        if subkey in self.__data[key]:
            return {subkey: self.__data[key][subkey]}
        else:
            raise IndexError(subkey)

    def get_cols(self, table, row, columns):
        key = '%s:%s' % (table, row)
        ret = {}
        for subkey in columns:
            if subkey in self.__data[key]:
                ret[subkey] = self.__data[key][subkey]

        return ret

    def delete(self, table, row, columns=None):
        assert not columns, 'not implemented'
        key = '%s:%s' % (table, row)
        del self.__data[key]
        return True

def put_cols(table, row, cols): #(column_family, column, data)
    return Manager().put_cols(table, row, cols)

def put_col(table, row, column_family, column, content):
    return Manager().put_col(table, row, column_family, column, content)

def get(table, row, column_family=None, column=None):
    assert False, 'no implemented'

def get_col(table, row, column_family, column):
    return Manager().get_col(table, row, column_family, column)

def get_cols(table, row, columns):
    return Manager().get_cols(table, row, columns)

def delete(table, row, columns=None):
    return Manager().delete(table, row, columns)

def clear():
    return Manager().clear()

def main():
    print get_col('test', 'rowA', 'A', 'B')
    print put_col('test', 'rowA', 'A', 'B', 'contentB')
    print put_col('test', 'rowA', 'A', 'C', 'contentC')
    print get_cols('test', 'rowA', ['A:B', 'A:C'])

if __name__ == '__main__':
    main()
