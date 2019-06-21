# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2017/9/29 0029

import os
import json
import xlrd
__author__ = 'huohuo'
base_dir = os.getcwd()

if __name__ == "__main__":
    pass

url = r'D:\pythonproject\report\data\part2\immune_suggestion.xls'
data = xlrd.open_workbook(url)
