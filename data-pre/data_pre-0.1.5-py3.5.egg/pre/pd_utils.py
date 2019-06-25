"""
@author: magician
@file: pd_data.py
@date: 2019/06/05
"""


def check_type(data, dtype):
    """
    ckeck data type
    :param data:  data
    :param dtype: data type
    :return: error
    """
    error = ''
    for item in data:
        if not isinstance(item, type(dtype)):
            error = '{0} data type is error!'.format(item)
            break

    return error
