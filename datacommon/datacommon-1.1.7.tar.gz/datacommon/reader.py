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
            return getJsonData(filename, encoding=encoding)
        return getJsonData(filename, encoding=encoding)
    elif suffix == 'XML':
        return getXmlData(filename)
    elif suffix == 'TXT':
        with open(filename, 'rb') as f:
            encoding = guessTextEncode(f.read())
        if encoding:
            return getTxtData(filename, encoding=encoding)
        return getTxtData(filename, encoding=encoding)
    else:
        raise KeyError("无法解析的数据格式！")


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


def getTxtData(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as f:
        content = f.read()
    return content


from lxml import etree


def getXmlData(filename, encoding='utf-8'):
    data = []
    docTree = etree.parse(filename, etree.XMLParser())
    root = docTree.getroot()
    items = root.getchildren()
    for item in items:
        data.append([i.text for i in item.getchildren()])
    return data


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
