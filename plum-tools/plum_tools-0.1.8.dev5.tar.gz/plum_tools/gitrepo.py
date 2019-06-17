# -*- coding:UTF-8
"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: exceptions
#         Desc: 查找指定路径下所有被改动的git仓库
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-05 22:02
#=============================================================================
"""
import os
import argparse

from multiprocessing import Pool

from .conf import Constant
from .utils.printer import print_warn
from .utils.printer import print_error
from .utils.git import check_is_git_repository
from .utils.git import check_repository_modify_status
from .utils.git import check_repository_stash


def find_git_project_for_python(path):
    """查找目录下所有的 git仓库

    :param path 要被检查的目录
    :type path str
    :example path "/tmp/git"

    >>> for path in find_git_project_for_python("/tmp"):
    ...    print path


    """
    for root, _, _ in os.walk(path):
        if check_is_git_repository(root):
            yield root


def check_project(path):
    """检查git项目

    :param path 仓库路径
    :type path str
    :example path /tmp/git

    :rtype result dict
    :return result {
        path: 仓库路径
        output: 检查输出信息
        status:
            True 仓库有文件进行了修改或有储藏文件
            False 仓库没有和远程一致。且没有储藏文件
    }
    :example result {
        "path": "/tmp/git",
        "status": False,
        "output": ""
    }
    """
    result = {
        "path": path,
        "status": False,
    }
    # 检查文件是否改动
    status_result, status_out = check_repository_modify_status(path)
    if status_result:
        result["status"] = True
        result["output"] = status_out
        return result

    # 检查是否有文件储藏
    stash_result, stash_out = check_repository_stash(path)
    if stash_result:
        result["status"] = True
        result["output"] = stash_out
    return result


def check_projects(projects, detail):
    """检查指导目录下所有的仓库是否有修改

    当仓库中有内容被修改时，打印黄色警告信息

    :param projects 需要检查的目录列表
    :type projects list
    :example ["/tmp"]

    :param detail 是否显示详细错误信息
    :type detail bool
    :example False
    """
    targets = [path for project_path in projects for path in find_git_project_for_python(project_path)]
    pool = Pool(processes=Constant.processes_number)
    result = pool.map(check_project, targets)
    for item in result:
        # 仓库中文件没有被改动而且没有文件被储藏了
        if not item["status"]:
            continue
        print_warn(item["path"])

        # 打印详细错误信息
        if not detail:
            continue
        print_error(item["output"])


def main():
    """程序主入口
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-p" "--path",
                        action="store",
                        required=False,
                        dest="path",
                        nargs="+",
                        default=[os.environ["HOME"]],
                        help="The directory path to check")
    parser.add_argument("-d" "--detail",
                        action="store_true",
                        required=False,
                        dest="detail",
                        default=False,
                        help="display error details")
    parser.add_argument("-t" "--test",
                        action="store_true",
                        required=False,
                        dest="test",
                        default=False,
                        help="run the test function")
    args = parser.parse_args()
    check_projects(args.path, args.detail)
