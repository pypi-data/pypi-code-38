# -*- coding: utf-8 -*-
from __future__ import print_function
import six
import os
import re
import subprocess
from io import open
import ipaddress
import socket
import click
import psutil


def get_self_pids():
    """
    """
    if os.name == "nt" and __name__ != "__main__":
        return [os.getpid(), os.getppid()]
    else:
        return [os.getpid()]

def get_cmdline_or_name(p):
    try:
        return p.cmdline()
    except psutil.AccessDenied:
        return [p.name()]

def get_ip(ip):
    """获化为ipaddress对象。
    """
    if isinstance(ip, (ipaddress.IPv4Address,  ipaddress.IPv6Address)):
        return ip
    if isinstance(ip, int):
        return ipaddress.IPv4Address(ip)
    ip = six.ensure_text(ip)
    if ":" in ip:
        return ipaddress.IPv6Address(ip)
    else:
        return ipaddress.IPv4Address(ip)


def get_nics(nic):
    """根据网络接口名称获取接口对象。nics可能为None、字符串、字符串列表。
    """
    all_nics = psutil.net_if_addrs()
    nics = {}
    if not nic:
        nics = all_nics
    elif isinstance(nic, (list, tuple, set)):
        for name in nic:
            nics[name] = all_nics[name]
    else:
        nic = six.ensure_str(nic)
        nics[nic] = all_nics[nic]
    return nics


def get_ips(nics):
    """从网络接口对象列表中提取网络地址列表。
    """
    ips = set()
    for nic in nics:
        for addr in nic:
            if addr.family in (socket.AF_INET, socket.AF_INET6):
                ips.add(get_ip(addr.address))
    return list(ips)


def checkip(ip, nic=None):
    """搜索指定IP。不指定nic则在全部网络接口上搜索。
    
    返回搜索结果及搜索到的网络接口名称。
    """
    ip = get_ip(ip)
    nics = get_nics(nic)
    for name, nic in nics.items():
        for addr in nic:
            if addr.family in (socket.AF_INET, socket.AF_INET6):
                if get_ip(addr.address) == ip:
                    return True, name
    return False, None


def checkport(port, proto="tcp", nic=None):
    """搜索指定监听端口。不指定nic则在全部网络接口上搜索。不指定proto默认为tcp，即tcp4+tcp6。

    返回搜索结果及监听的网络地址列表。
    """
    found = False
    found_ips = []
    nics = get_nics(nic)
    ips = get_ips(nics.values())
    connections = psutil.net_connections(kind=proto)
    for connection in connections:
        if connection.status == "LISTEN":
            if connection.laddr.port == port:
                if connection.laddr.ip == "0.0.0.0" or connection.laddr.ip == "::" or get_ip(connection.laddr.ip) in ips:
                    found = True
                    found_ips.append(connection.laddr.ip)
    return found, found and found_ips or None


def checkproc_by_pid(pid):
    """判断指定PID的进程是否运行。
    """
    try:
        p = psutil.Process(pid=pid)
        return True, p.cmdline()
    except psutil.NoSuchProcess:
        return False, None

def checkproc_by_pidfile(pidfile):
    """判断pidfile中记录的进程是否运行。
    """
    if not os.path.exists(pidfile):
        return False, None, None
    pidstr = ""
    with open(pidfile, "r", encoding="utf-8") as fobj:
        pidstr = fobj.read().strip()
    pid = int(pidstr)
    try:
        p = psutil.Process(pid=pid)
        return True, pid, p.cmdline()
    except psutil.NoSuchProcess:
        return False, None, None


def checkproc_by_command(command):
    """根据进程cmdline进行正则匹配判断指定进程是否正在运行。
    """
    found = False
    ps = []
    self_pids = get_self_pids()
    for p in psutil.process_iter():
        if p.pid in self_pids:
            continue
        cmdline = subprocess.list2cmdline(get_cmdline_or_name(p))
        if re.findall(command, cmdline):
            found = True
            ps.append(p)
    if not found:
        return False, None
    else:
        return True, ps


def cmd_checkip_core(ip, nic=None):
    found, nic = checkip(ip, nic)
    if found:
        print("查找结果：", "FOUND")
        print("　IP地址：", ip)
        print("网络接口：", nic)
        os.sys.exit(0)
    else:
        print("查找结果：", "NOT FOUND")
        print("　IP地址：", ip)
        os.sys.exit(1)

def cmd_checkport_core(port, proto="tcp", nic=None):
    found, ip = checkport(port, proto, nic)
    if found:
        print("查找结果：", "FOUND")
        print("　　端口：", port)
        print("　IP地址：", ip)
        os.sys.exit(0)
    else:
        print("查找结果：", "NOT FOUND")
        print("　　端口：", port)
        os.sys.exit(1)


def cmd_checkproc_by_pid(pid):
    running, cmdline = checkproc_by_pid(pid)
    if running:
        print("查找结果：", "FOUND")
        print("　进程号：", pid)
        print("启动命令：", subprocess.list2cmdline(cmdline))
        os.sys.exit(0)
    else:
        print("查找结果：", "NOT FOUND")
        print("　进程号：", pid)
        os.sys.exit(1)


def cmd_checkproc_by_pidfile(pidfile):
    running, pid, cmdline = checkproc_by_pidfile(pidfile)
    if running:
        print("查找结果：", "FOUND")
        print("进程文件：", pidfile)
        print("　进程号：", pid)
        print("启动命令：", subprocess.list2cmdline(cmdline))
        os.sys.exit(0)
    else:
        print("result:", "NOT FOUND")
        print("pidfile:", pidfile) 
        os.sys.exit(1)

def cmd_checkproc_by_command(command):
    running, ps = checkproc_by_command(command)
    if running:
        print("　查找结果：", "FOUND")
        print("命令行正则：", command)
        for p in ps:
            print("-"*60)
            print("　　进程号：", p.pid)
            print("　启动命令：", subprocess.list2cmdline(get_cmdline_or_name(p)))
        os.sys.exit(0)
    else:
        print("　查找结果：", "NOT FOUND")
        print("命令行正则：", command)
        os.sys.exit(1)

def cmd_checkproc_core(pid=None, pidfile=None, command=None):
    c = 0
    for o in [pid, pidfile, command]:
        if not o is None:
            c += 1
    if c != 1:
        print("错误：要求pid、pidfile、command参数有且只能有一个。")
        os.sys.exit(2)
    if not pid is None:
        cmd_checkproc_by_pid(pid)
    elif not pidfile is None:
        cmd_checkproc_by_pidfile(pidfile)
    else:
        cmd_checkproc_by_command(command)


@click.group()
def main():
    """检查系统状态。
    """
    pass


@main.command(name="checkip")
@click.option("-i", "--nic", multiple=True, required=False, help="在指定网络接口上查找监听端口，默认为在全部网络接口上查找。可以多次使用，表示在多个网络接口上查找。")
@click.argument("ip", nargs=1, required=True)
def cmd_checkip(nic, ip):
    """检查指定的IP地址是否存在。
    """
    cmd_checkip_core(ip, nic)


@main.command(name="checkport")
@click.option("-i", "--nic", multiple=True, required=False, help="在指定网络接口上查找监听端口，默认为在全部网络接口上查找。可以多次使用，表示在多个网络接口上查找。")
@click.option("-p", "--proto", default="tcp", required=False, help="监听端口的协议，如：tcp, tcp4, udp, udp4, inet, inet4, inet6, tcp6, udp6等，默认为tcp。")
@click.argument("port", type=int, nargs=1, required=True)
def cmd_checkport(nic, proto, port):
    """检查指定端口是否被监听。
    """
    cmd_checkport_core(port, proto, nic)


@main.command(name="checkproc")
@click.option("-i", "--pid", type=int, required=False, help="根据PID判断进程是否存活。")
@click.option("-f", "--pidfile", required=False, help="根据PID文件判断进程是否存活。")
@click.option("-c", "--command", required=False, help="检查启动命令正则匹配判断进程是否存活。")
def cmd_checkproc(pid, pidfile, command):
    """检查指定进程是否存活。

    注意：要求pid、pidfile、command参数有且只有一个。
    """
    cmd_checkproc_core(pid, pidfile, command)


if __name__ == "__main__":
    main()
