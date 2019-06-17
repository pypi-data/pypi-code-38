# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: prn
#         Desc: 上传文件到服务器
#               命令: prn -s plum -p plum
#               描述: 上传 ~/..yml 中指定项目的文件到ssh_config中配置的服务器
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-07 17:26
#=============================================================================
"""
import os
import argparse
import sys

from .conf import PathConfig
from .utils.printer import print_error
from .utils.sshconf import merge_ssh_config
from .utils.utils import run_cmd
from .utils.utils import get_file_abspath
from .utils.utils import YmlConfig
from .utils.printer import print_ok
from .exceptions import RunCmdError


def get_project_conf(project, src, dest, delete, exclude):
    """查询项目信息

    :param project 指定的项目名
    :type project str
    :example project plum

    :param src 本地路径
    :type src str
    :example src /tmp

    :param dest 远程机器路径
    :type dest str
    :example dest /tmp

    :param exclude 需要过滤的目录
    :type exclude str
    :example exclude [".git"]

    :param delete 是否删除远程机器目录下非本次上传的文件
    :type delete int
    :example delete 0 0|1  0: 不删除 1: 删除

    :rtype data dict
    :return data 项目的配置信息
    {
        "src": 本地路径,
        "dest": 上传后的目录路径,
        "exclude": 需要过滤不上传的目录,
        "delete": 是否删除远程机器目录下非本次上传的文件
    }
    :example data {
        "src": "/tmp",
        "dest": "/tmp",
        "exclude": [".git"],
        "delete": 0
    }
    """
    yml_data = YmlConfig.parse_config_yml(PathConfig.plum_yml_path)
    data = {}
    try:
        data = yml_data["projects"][project]
    except KeyError:
        if not (src and dest):
            print_error("yml文件: %s 中没有配置项目: %s 的信息" % (PathConfig.plum_yml_path, project))
            sys.exit(1)

    # 设置默认值
    data.setdefault("exclude", [])
    data.setdefault("delete", 0)

    # 从命令行中更新对应值
    if src:
        data["src"] = src
    if dest:
        data["dest"] = dest
    if delete is not None:  # 默认值为None
        data["delete"] = delete
    if exclude:
        data["exclude"] = exclude

    # 对本地路径取绝对路径
    data["src"] = get_file_abspath(data["src"])
    return data


class SyncFiles(object):
    """上传文件到服务器
    """

    def __init__(self, hostname, user, port, identityfile, src, dest, exclude, delete, is_download):
        """文件上传功能

        :param hostname 主机ip
        :type hostname str
        :example hostname 10.10.100.1

        :param user ssh登陆使用的用户名
        :type user str
        :example user 10.10.100.1

        :param port ssh登陆使用的端口号
        :type port int
        :example port 22

        :param identityfile 私钥文件路径
        :type identityfile str
        :example identityfile ~/.ssh/id_rsa

        :param src 本地路径
        :type src str
        :example src /tmp

        :param dest 远程机器路径
        :type dest str
        :example dest /tmp

        :param exclude 需要过滤的目录
        :type exclude list
        :example exclude [".git"]

        :param delete 是否删除远程机器目录下非本次上传的文件
        :type delete int
        :example delete 0 0|1  0: 不删除 1: 删除

        :param is_download 是否是下载文件，默认是上传
        :type is_download bool
        :example is_download False
        """
        self._hostname = hostname
        self._user = user
        self._port = port
        self._identity_file = identityfile
        self._src = src
        self._dest = dest
        self._exclude = exclude
        self._delete = delete
        self._is_download = is_download

    def _get_sync_option(self):
        """组合出同步文件的命令
        """
        option = ["rsync -rtv"]
        known_host = "UserKnownHostsFile=/dev/null"
        host_key = "StrictHostKeyChecking no"
        timeout = "ConnectTimeout=2"
        # 指定端口
        if self._port:
            ssh_cmd = "ssh -p %d" % self._port
        else:
            ssh_cmd = "ssh"
        option.append("'--rsync-path=mkdir -p %s && rsync'" % os.path.dirname(self._dest))
        option.append("-e '%s -i %s -o \"%s\" -o \"%s\" -o \"%s\"'" % (
            ssh_cmd, self._identity_file, known_host, host_key, timeout))
        if self._delete:
            option.append(" --delete")
        for item in set(self._exclude):
            option.append("--exclude %s" % item)
        return " ".join(option)

    def translate(self):
        """文件上传功能
        """
        # pv = "|pv -lep -s 117 >/dev/null"
        pv = ""

        if self._is_download:
            self._src, self._dest = self._dest, self._src

        # 本地端目录结尾需要有 /
        if not self._src.endswith("/"):
            self._src += "/"
        # 目标端目录结尾不能有 /
        if self._dest.endswith("/"):
            self._dest = self._dest[:-1]

        # 从远端下载文件到本地
        if self._is_download:
            src = "%s@%s:%s%s" % (self._user, self._hostname, self._src, pv)
            dest = self._dest
            text = "从 %s@%s 服务器(端口: %s) 下载目录 %s 到本地 %s" % (
                self._user, self._hostname, self._port, self._src, self._dest)
        # 从本地上传文件到远端
        else:
            src = self._src
            dest = "%s@%s:%s%s" % (self._user, self._hostname, self._dest, pv)
            text = "上传目录 %s 到 %s@%s 服务器(端口: %s) %s 目录" % (
                self._src, self._user, self._hostname, self._port, self._dest)

        rsync = self._get_sync_option()
        cmd = "%s %s %s" % (rsync, src, dest)
        try:
            run_cmd(cmd)
            print_ok("%s成功" % text)
        except RunCmdError as e:
            print_error("%s失败, 失败原因: %s" % (text, e.err_msg))


def sync_files(host_list, host_type, user, port, identity_file, projects_conf, is_download):
    """上传文件到服务器上

    :param host_list 服务器列表
    :type host_list list
    :example host_list [1, 2]

    :param host_type 主机类型
    :type host_type str
    :example host_type [1, 2]

    :param user ssh登陆用户名
    :type user str
    :example user root

    :param port ssh登陆端口
    :type port int
    :example port 22

    :param user ssh登陆用户名
    :type user str
    :example user root

    :param identity_file ssh登陆私钥文件路径
    :type identity_file str
    :example identity_file ~/.ssh/id_rsa

    :param projects_conf 需要上传的项目配置列表
    :type projects_conf list(dict)
    :example pro_conf [{
        "src": "/tmp",
        "dest": "/tmp",
        "exclude": [".git"],
        "delete": 0
    }]

    :param is_download 是否是下载文件，默认是上传
    :type is_download bool
    :example is_download False
    """
    for host in host_list:
        ssh_conf = merge_ssh_config(host, host_type, user, port, identity_file)
        ssh_conf.update({"is_download": is_download})
        for pro_conf in projects_conf:
            pro_conf.update(ssh_conf)
            sync = SyncFiles(**pro_conf)
            sync.translate()


def main():
    """程序主入口
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--servers",
                        required=True,
                        action="store",
                        dest="servers",
                        nargs="+",
                        help="specify server")
    parser.add_argument("-p", "--projects",
                        required=False,
                        action="store",
                        dest="projects",
                        nargs="+",
                        default=["default"],
                        help="specify project")

    parser.add_argument("-t", "--type",
                        action="store",
                        required=False,
                        dest="type",
                        default="default",
                        help="host type")
    parser.add_argument("--download",
                        action="store_true",
                        required=False,
                        dest="download",
                        default=False,
                        help="Download the file locally")
    parser.add_argument("-i", "--identityfile",
                        action="store",
                        required=False,
                        dest="identity_file",
                        default="",
                        help="ssh login identityfile path")
    parser.add_argument("-u", "--username",
                        action="store",
                        required=False,
                        dest="user",
                        default="",
                        help="ssh login username")
    parser.add_argument("--port",
                        action="store",
                        required=False,
                        dest="port",
                        type=int,
                        default=0,
                        help="ssh login port")
    parser.add_argument("-l", "--local",
                        action="store",
                        required=False,
                        dest="local",
                        default="",
                        help="local path")
    parser.add_argument("-r", "--remote",
                        action="store",
                        required=False,
                        dest="remote",
                        default="",
                        help="remote path")
    parser.add_argument("-d", "--delete",
                        action="store",
                        required=False,
                        dest="delete",
                        type=int,
                        default=None,
                        help="delete remote path other file")
    parser.add_argument("-e", "--exclude",
                        action="store",
                        nargs="+",
                        required=False,
                        dest="exclude",
                        default=[],
                        help="exclude file")

    args = parser.parse_args()
    host_list, host_type, projects, is_download = args.servers, args.type, args.projects, args.download

    user, port, identity_file = args.user, args.port, args.identity_file

    src, dest, delete, exclude = args.local, args.remote, args.delete, args.exclude

    projects_conf = [get_project_conf(project, src, dest, delete, exclude) for project in projects]
    sync_files(host_list, host_type, user, port, identity_file, projects_conf, is_download)
