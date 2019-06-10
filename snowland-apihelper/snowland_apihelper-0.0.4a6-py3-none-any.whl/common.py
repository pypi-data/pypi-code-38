#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: common.py
# @time: 2019/5/5 16:47
# @Software: PyCharm


__author__ = 'A.Star'

ERROR_CODE_UNKNOWN = -1  # 未知错误
ERROR_CODE_OPERATION_FAILED = 0  # 操作失败
ERROR_CODE_OPERATION_SUCCESS = 1  # 操作成功
ERROR_CODE_PARTNER_ERROR = 2  # 参数有误
ERROR_CODE_TOKEN_ERROR = 3  # token失效
ERROR_CODE_DATABASE_ERROR = 4  # 数据库错误
ERROR_CODE_LOGINED_ERROR = 5  # 该账户已在其他设备登录，已退出
ERROR_CODE_ACCOUNT_LOCKED_ERROR = 6  # 账户被锁定、禁用|
ERROR_CODE_IP_TRY_TIME_LIMITED_ERROR = 7  # 同一终端登录失败次数超过限制|
ERROR_CODE_ACCOUNT_TRY_TIME_LIMITED_ERROR = 8  # 同一账户登录失败次数超过限制|
ERROR_CODE_USER_NOT_FOUND = 9  # 不存在此用户
ERROR_CODE_SERVER_ERROR = 99  # 后台处于维护状态


DEFAULT_SIGNED_VALUE_VERSION = 3  # cookie 默认签名版本号
DEFAULT_SIGNED_VALUE_MIN_VERSION = 2  # cookie 默认最小签名版本号
