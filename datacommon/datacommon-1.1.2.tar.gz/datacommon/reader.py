# -*- coding: utf-8 -*-
# author: pengr

from .util import guessTextEncode


def getFileData(filename,):
    suffix = filename.split('.')[-1].upper()
    if suffix == 'XLS' or suffix == 'XLSX':
        return getXlsData(filename)
    elif suffix == 'CSV':
        with open(filename, 'rb') as f:
            encoding = guessTextEncode(f.read())
        if encoding:
            return getCsvData(filename, encoding=encoding)
        return getCsvData(filename)
    elif suffix == 'JSON':
        with open(filename, 'rb') as f:
            encoding = guessTextEncode(f.read())
        if encoding:
            return getCsvData(filename, encoding=encoding)
        return getJsonData(filename, encoding=encoding)


import csv


def getCsvData(filename, encoding='utf-8', delimiter=','):
    # csv文件中许多无效列
    with open(filename, encoding=encoding) as f:
        items = [row for row in csv.reader(f, delimiter=delimiter)]
    return items


import xlrd


def getXlsData(filename):
    items = []
    data = xlrd.open_workbook(filename)
    table = data.sheets()[0]
    nrows = table.nrows
    for row in range(nrows):
        items.append(table.row_values(row))
    return items


import json


def getJsonData(filename, encoding='utf-8'):
    fp = open(filename, 'r', encoding=encoding)
    return json.load(fp)


if __name__ == '__main__':
    filename = '..\guizhou\source\贵州省PPP推进会推介项目表\贵州省PPP推进会推介项目表.csv'
    xlsfilename = '..\guizhou\source\部门决算及“三公”经费决算信息公开表\贵州省投资促进局2016年度部门预算及“三公”经费预算.xlsx'
    # data = getCsvData(filename)
    data = getFileData(xlsfilename)

    print(data)

    from .dataSet import DataSet

    ds1 = DataSet(data)
    cols = [i for i in range(9)]
    date_cols = ds1.runUDF('GetDateColumns').distinct()
    print(date_cols)
    x = ds1.runUDF('IsNonDataUDF', *cols).count(*cols)
    print(x)
