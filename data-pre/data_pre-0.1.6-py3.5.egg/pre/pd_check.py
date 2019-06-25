# coding=utf-8
"""
@author: magician
@file: excel.py
@date: 2018/12/17
"""
import pandas as pd


def check_data_type(col_name, value, check_type, **kwargs):
    """
    字符串检查
    :param col_name:       列名
    :param value:          检查元素
    :param check_type:     检查类型
    :param kwargs:
    """
    # TODO datetime 校验
    # TODO pandas 校验
    result = ''
    # print('col_name: ', col_name, 'type: ', type(value), 'check_type: ', check_type)

    if value or value == 0:
        # pandas 时间校验
        if check_type == 'datetime':
            try:
                pd.to_datetime(value)
            except Exception as e:
                print(e)
                result = col_name + '时间类型错误' + ': ' + str(value) + ' '
        else:
            if not isinstance(value, check_type):
                result = col_name + '类型错误' + ': ' + str(value) + ' '
    else:
        result = col_name + '不能为空'

    return result
