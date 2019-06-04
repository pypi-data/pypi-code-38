# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: git
#         Desc: git相关操作函数
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-07 19:05
#=============================================================================
"""
import os

from ..conf import GitCommand
from .utils import cd
from .utils import run_cmd


def get_current_branch_name():
    """查询当前分支名

    :rtype str
    :return 当前分支名
    """
    return run_cmd(GitCommand.branch_abbrev).strip()


def check_is_git_repository(path):
    """检查目录是否为git 仓库

    :param path 要被检查的目录
    :type path str
    :example path /tmp/git/

    >>> check_is_git_repository("/tmp")
    False

    :rtype bool
    :return
        True `path`目录是一个git仓库
        False `path`目录不是一个git仓库
    """
    git_path = os.path.join(path, ".git")
    if os.path.exists(git_path) and os.path.isdir(git_path):
        return True
    return False


def check_repository_modify_status(repo_path):
    """检查仓库是否有文件修改

    :param repo_path 仓库路径
    :type repo_path str
    :example repo_path /tmp/git

    :rtype result bool
    :return result 检查结果
        True 仓库有文件进行了修改未提交
        False 仓库没有文件进行了修改

    >>> check_repository_modify_status("`pwd`")#doctest: +ELLIPSIS
    (True, '...')

    :rtype output str
    :return output 命令输出
    """
    with cd(repo_path):
        output = run_cmd(GitCommand.status_default)

    result = False

    # 检查是否落后、超前远程分支
    if GitCommand.pull_keyword in output or GitCommand.push_keyword in output:
        result = True
    else:
        with cd(repo_path):
            # 检查本地是否还有文件未提交
            if run_cmd(GitCommand.status_short):
                result = True
    return result, output


def check_repository_stash(repo_path):
    """检查仓库是否在储藏区

    :param repo_path 仓库路径
    :type repo_path str
    :example repo_path /tmp/git

    :rtype result bool
    :return result 检查结果
        True 仓库有文件在储藏区
        False 仓库中储藏区是干净的

    >>> check_repository_stash("`pwd`")
    (False, '')

    :rtype output str
    :return output 命令输出
    """
    with cd(repo_path):
        output = run_cmd(GitCommand.stash_list)
    result = False
    if output:
        result = True
    return result, output
