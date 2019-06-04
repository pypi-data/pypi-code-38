# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: utils
#         Desc: 项目中工具包
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-05 22:02
#=============================================================================
"""

from __future__ import print_function

import os
import re
import platform
import sys
import signal
import subprocess

import yaml

from schema import Schema
from schema import SchemaError
from schema import Optional

from ..conf import PathConfig
from ..conf import OsCommand
from .printer import print_text
from .printer import print_error
from ..exceptions import RunCmdError
from ..exceptions import RunCmdTimeout
from ..exceptions import SystemTypeError


class cd(object):
    """进入目录执行对应操作后回到目录
    """

    def __init__(self, new_path):
        """初始化

        :param new_path: 目标目录
        :type new_path str
        :example new_path "/tmp"

        >>> with cd("/tmp"):
        ...     print(run_cmd("pwd"))
        "/tmp"
        """
        self._new_path = new_path
        self._current_path = None

    def __enter__(self):
        self._current_path = os.getcwd()
        os.chdir(self._new_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._current_path)


class YmlConfig(object):
    """解析yml配置
    """
    _yml_data = {}

    @classmethod
    def parse_config_yml(cls, yml_path):
        """解析配置程序依赖的配置yml文件

        :param yml_path 项目依赖的yml配置文件路径
        :type yml_path str
        :example yml_path ~/.plum_tools.yml

        :rtype dict
        :return yml配置文件内容
        """
        if cls._yml_data:
            return cls._yml_data
        yml_schema = Schema({
            "default_ssh_conf": {
                "user": str,
                "port": int,
                "identityfile": str
            },
            "ipmi_interval": int,
            lambda x: x.startswith("host_type_"): str,
            "projects": {
                str: {
                    "src": str,
                    "dest": str,
                    Optional("exclude"): list,
                    Optional("delete"): int,
                }
            }
        })
        try:
            with open(yml_path) as f:
                try:
                    data = yml_schema.validate(yaml.safe_load(f.read()))
                except SchemaError as e:
                    print_error("yml文件: %s 格式错误, %s, 请参照以下格式进行修改" % (PathConfig.plum_yml_path, e.args[0]))
                    with open(os.path.join(PathConfig.root, PathConfig.plum_yml_name)) as fp:
                        text = fp.read()
                    print_text(text)
                    sys.exit(1)
                else:
                    cls._yml_data = data
                    return cls._yml_data
        except IOError:
            print_error("yml文件: %s 不存在" % PathConfig.plum_yml_path)
            sys.exit(1)


def run_cmd(cmd, is_raise_exception=True, timeout=None):
    """执行系统命令

    :param cmd 系统命令
    :type cmd str
    :example cmd hostname

    :param is_raise_exception 执行命令失败是否抛出异常
    :type is_raise_exception bool
    :example is_raise_exception False

    :param timeout 超时时间
    :type timeout int
    :example timeout 1

    >>> run_cmd("echo 1")
    '1\\n'

    >>> run_cmd("ls -l /tmp") #doctest: +ELLIPSIS
    'lrwxr-xr-x@ 1 root  wheel...'

    >>> run_cmd("aaa")
    Traceback (most recent call last):
    RunCmdError: run `aaa` fail

    >>> run_cmd("bbb")
    Traceback (innermost last):
    RunCmdError: run `bbb` fail

    :rtype str
    :return 命令执行结果
    :example hostname

    :raise RunCmdError 命令执行失败
    :raise RunCmdTimeout 命令执行超时
    """

    def raise_timeout_exception(*_):
        """通过抛出异常达到超时效果
        """
        raise RunCmdTimeout("run `%s` timeout, timeout is %s" % (cmd, timeout))

    # 设置指定时间后出发handler
    if timeout:
        signal.signal(signal.SIGALRM, raise_timeout_exception)
        signal.alarm(timeout)

    p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out_msg = p.stdout.read()
    err_msg = p.stderr.read()
    exit_code = p.wait()

    # 解除触发handler
    if timeout:
        signal.alarm(0)

    if is_raise_exception and exit_code != 0:
        message = "run `%s` fail" % cmd
        raise RunCmdError(message, out_msg=out_msg, err_msg=err_msg)
    return out_msg


def get_file_abspath(path):
    """文件的相对路径

    :param path 文件路径
    :type path str
    :example path ~/.ssh/id_rsa

    :rtype abs_path str
    :return abs_path 文件绝对路径
    :example abs_path /home/seekplum/.ssh/id_rsa
    """

    def replace_path(old_path):
        """替换路径中的空格
        """
        return old_path.replace(r" ", r"\ ")

    # 系统直接可以找到
    if os.path.exists(path):
        return path

    # 通过系统命令stat查找真实路径
    path = replace_path(path)
    cmd = OsCommand.stat_command % path
    output = run_cmd(cmd)

    # 获取操作系统类型
    system_type = platform.system()
    if system_type == "Linux":
        pattern = re.compile(r'File: "(.*)"')
    # mac系统
    elif system_type == "Darwin":
        pattern = re.compile(r'"\s+\d+\s+\d+\s+\d+(.*)$')
    else:
        raise SystemTypeError("此项功能仅支持 Linux / Darwin(mac)")
    match = pattern.search(output)
    abs_path = replace_path(match.group(1).strip())
    return abs_path
