# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: pping
#         Desc: ping指定网段所有ip是否能ping通
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-07 10:26
#=============================================================================
"""
import argparse

from multiprocessing import Pool

from .conf import OsCommand
from .conf import Constant
from .exceptions import RunCmdError
from .utils.printer import print_text
from .utils.utils import run_cmd
from .utils.sshconf import get_prefix_host_ip


def ping(ip):
    """ping指定ip是否能ping通

    :param ip 主机ip
    :type ip str
    :example ip 10.10.100.1
    """
    cmd = OsCommand.ping_command % ip
    try:
        run_cmd(cmd)
    except RunCmdError:
        pass
    else:
        return ip


def run(host_type, prefix_host):
    """打印IP段内所有能ping通的ip

    :param host_type ip类型,不同的ip类型，ip前缀不一样
    :type host_type str
    :example host_type default

    :param prefix_host: 主机前缀
    :type prefix_host str
    :example prefix_host 1.1.1
    """
    if not prefix_host:
        prefix_host = get_prefix_host_ip(host_type)

    mark = "."
    if not prefix_host.endswith(mark):
        prefix_host += mark

    pool = Pool(processes=Constant.processes_number)
    targets = ["%s%d" % (prefix_host, i) for i in range(1, 255)]
    result = pool.map(ping, targets)
    for ip in result:
        if ip:
            print_text(ip)


def main():
    """程序主入口
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t" "--type",
                        action="store",
                        required=False,
                        dest="type",
                        default="default",
                        help="host type")
    parser.add_argument("-p" "--prefix-host",
                        action="store",
                        required=False,
                        dest="prefix_host",
                        default=None,
                        help="host prefix")

    args = parser.parse_args()
    run(args.type, args.prefix_host)
