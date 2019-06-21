# Created by Q-ays.
# whosqays@gmail.com


import os
from wisdoms.commons import my_code as codes

SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

revert = codes.revert
codes = codes

err_num = {
    "OK": 0,
    "DATAERR": 1,
    "DSANF": 2,
    "PARM": 3,
    "PARGERR": 4,
    "NOadmin": 5,
    "NOAUTH": 6
}

err_msg = {
    "OK": "OK",
    "DATAERR": "数据库错误",
    "DSANF": "第三方服务错误",
    "PARM": "参数错误",
    "PARGERR": "数据错误",
    "NOadmin": "被管理者",
    "NOAUTH": "没有权限"
}

ABC_KEYS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "M", "L", "N", "O", "P", "Q", "R", "S", "T", "U",
            "V", "W", "X", "Y", "Z"]


def success(data=None):
    """
    封装revert方法，返回执行成功code

    :param data:
    :return:
    """
    return revert(codes.SUCCESS, data)
