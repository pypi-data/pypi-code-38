# encoding: utf-8

import os
import sys

VERSION = '1.0.1'

EDO_CONFIG_PATH = os.path.normpath(os.path.expanduser(r'~/.edopkgrc'))
SECTION = 'dev'
OC_API = r'https://oc-api.everydo.cn'
ACCOUNT='zopen'
INSTANCE = 'default'
USERNAME='admin'
CLIENT_ID = 'test'
CLIENT_SECRET = '022127e182a934dea7d69s10697s8ac2'
HELP_INFO = u'''
使用edopkg，可以将文件系统中的软件包和易度系统中的软件包同步。
服务器配置文件位于 ''%(PATH)s''
''' % {'PATH':EDO_CONFIG_PATH}
SERVER_HELP = u'查看和设置服务器配置'
CONFIG_HELP = u'添加和修改服务器配置'
CLONE_HELP = u'复制一个软件包'
PULL_HELP = u'下载一个软件包'
PUSH_HELP = u'上传一个软件包'
