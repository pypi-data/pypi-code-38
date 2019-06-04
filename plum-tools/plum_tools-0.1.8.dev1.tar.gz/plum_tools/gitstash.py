# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: gitstash
#         Desc: 外部传入一个branch，保存本地未提交的修改，然后切换到branch，将上次该branch保存的未提交的结果stash pop出来
#               命令: gitstash master
#               描述: 在当前路径下切换到master分支
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-07 16:29
#=============================================================================
"""
import os
import sys
import argparse

from .conf import GitCommand
from .conf import Constant
from .utils.utils import cd
from .utils.utils import run_cmd
from .utils.git import check_repository_modify_status
from .utils.git import check_repository_stash
from .utils.git import get_current_branch_name
from .utils.printer import print_warn
from .exceptions import RunCmdError


class GitCheckoutStash(object):
    """切换分支前储藏文件
    """

    def __init__(self, current_branch, new_branch):
        """初始化信息

        :param current_branch: 当前分支名
        :type current_branch str
        :example current_branch master

        :param new_branch: 新的分支名
        :type new_branch str
        :example new_branch release-1.0.0
        """
        self._current_branch = current_branch
        self._current_path = os.getcwd()  # 当前执行命令的路径
        self._new_branch = new_branch
        self._mark = "-"
        self._stash_uuid = "%s%s%s" % (self._current_branch, self._mark, Constant.stash_uuid)

    def _stash(self):
        """储藏文件
        """
        # 分支有修改,先进行stash储藏
        is_modify, _ = check_repository_modify_status(self._current_path)
        if is_modify:
            cmd = GitCommand.stash_save % self._stash_uuid
            with cd(self._current_path):
                run_cmd(cmd)

    def _check_branch(self):
        """检查分支是否一致

        :rtype bool
        :return
            True: 当前分支和要切换的分支一致
            False: 当前分支和要切换的分支不一致
        """
        return self._current_branch == self._new_branch

    def _checkout(self):
        """切换分支
        """
        # 切换到新分支
        cmd = GitCommand.git_checkout % self._new_branch
        with cd(self._current_path):
            run_cmd(cmd)

    def _apply(self):
        """恢复储藏的文件
        """
        # 检查切换后的分支是否有储藏文件
        is_stash, stash_out = check_repository_stash(self._current_path)
        if not is_stash:
            return
        for line in stash_out.splitlines():
            stash_string, _ = line.split(":", 1)
            stash_save = "%s%s%s" % (self._new_branch, self._mark, Constant.stash_uuid)
            if stash_save.strip() in line:
                cmd = GitCommand.stash_pop % stash_string
                with cd(self._current_path):
                    run_cmd(cmd)

    def checkout(self):
        """储藏文件切换分支
        """
        # 不需要切换
        if self._check_branch():
            return
        self._stash()
        self._checkout()
        self._apply()


def main():
    """程序主入口
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="branch",
                        action="store",
                        help="specify branch")
    args = parser.parse_args()
    new_branch = args.branch
    try:
        current_branch = get_current_branch_name()
    except RunCmdError:
        print_warn("当前目录不是一个git仓库")
        sys.exit(1)
    stash = GitCheckoutStash(current_branch, new_branch)
    stash.checkout()
