#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: common.py
# @time: 2018/10/29 10:24
# @Software: PyCharm


list_allow_extension = [
    '.py',
    '.jl',
    '.m',
    '.js',
    '.java',
    '.xml',
    '.html',
    '.htm',
    '.css',
    '.txt',
    '.cs',
    '.cpp',
    '.c',
    '.h',
    '.php'
]
list_ignore = [
    '.git',
    '.gitignore',
    '__pycache__/'
    '*.py[cod]',
    # '*$py.class',
    '*.so',
    '.Python'
    'build/',
    'develop-eggs/',
    'dist/',
    'downloads/',
    'eggs/',
    '.eggs/',
    'lib/',
    'lib64/',
    'parts/',
    'sdist/',
    'var/',
    'wheels/',
    '*.egg-info/',
    '.installed.cfg',
    '*.egg',
    'MANIFEST',
    '*.manifest',
    '*.spec',
    'pip-log.txt',
    'pip-delete-this-directory.txt',
    'htmlcov/',
    '.tox/',
    '.coverage',
    '.coverage.*',
    '.cache',
    'nosetests.xml',
    'coverage.xml',
    '*.cover',
    '.hypothesis/',
    '*.mo',
    '*.pot',
    '*.log',
    '.static_storage/',
    '.media/',
    'local_settings.py',
    'instance/',
    '.webassets-cache',
    '.scrapy',
    'docs/_build/',
    'target/',
    '.ipynb_checkpoints',
    '.python-version',
    'celerybeat-schedule',
    '.env',
    '.venv',
    'env/',
    'venv/',
    'ENV/',
    'env.bak/',
    'venv.bak/',
    '.spyderproject',
    '.spyproject',
    '.ropeproject',
    '/site',
    '.mypy_cache/',
    '.idea/'
]
ERROR_CODE_UNKNOWN = -1  # 未知错误
ERROR_CODE_OPERATION_FAILED = 0  # 操作失败
ERROR_CODE_OPERATION_SUCCESS = 1  # 操作成功
ERROR_CODE_PARTNER_ERROR = 2  # 参数有误
ERROR_CODE_TOKEN_ERROR = 3  # token失效
ERROR_CODE_DATABASE_ERROR = 4  # 数据库错误
ERROR_CODE_LOGINED_ERROR = 5  # 该账户已在其他设备登录，已退出
ERROR_CODE_ACCOUNT_LOCKED_ERROR = 6  # 账户被锁定、禁用|
ERROR_CODE_IP_TRY_TIME_LIMITED_ERROR = 7  # 同一终端登录失败次数超过限制|
ERROR_CODE_ACCOUNT_TRY_TIME_LIMITED_ERROR = 8  # 同一账户登录失败次数超过限制
ERROR_CODE_USER_NOT_FOUND = 9  # 无此用户
ERROR_CODE_PERMISSION_ERROR = 10  # 无用户权限
ERROR_CODE_SERVER_ERROR = 99  # 后台处于维护状态|

hex_string = '0123456789abcdef'
hex_string_upper = '0123456789ABCDEF'
alnum_string = 'qwertyuiopasdfghjklzxcvbnm1234567890'
digit_string = '0123456789'

JSON_DEMO = {
    'successful': False,
    'data': None,
    'code': ERROR_CODE_OPERATION_SUCCESS,
    'message': None
}

PAYLOAD_DEMO = {
    "iss": None,  # Issue 发行者
    "sub": None,  # 主题
    "aud": None,  # Audience，观众
    "exp": None,  # Expiration time，过期时间
    "nbf": None,  # Not before
    "iat": None,  # Issued at，发行时间
    "jti": None,  # JWT ID
}
