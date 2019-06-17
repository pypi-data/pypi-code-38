# -*- coding:utf-8 -*-

"""
 Verion: 1.0
 Since : 3.6
 Author: zhangjian
 Site: https://iliangqunru.bitcron.com/
 File: tan
 Time: 6/13/2019
 
 Add New Functional tan

 =============================

 Reference at https://github.com/flaggo/pydu/blob/master/pydu/platform.py
"""
import os
import sys
import subprocess
import threading

import time

import pyperclip
import argparse
from colorama import init, Fore, Back, Style

WINDOWS = os.name == 'nt'
LINUX = sys.platform.startswith('linux')
POSIX = os.name == 'posix'
DARWIN = sys.platform.startswith('darwin')
SUNOS = sys.platform.startswith('sunos')
SMARTOS = os.uname()[3].startswith('joyent_') if SUNOS else False
FREEBSD = sys.platform.startswith('freebsd')
NETBSD = sys.platform.startswith('netbsd')
OPENBSD = sys.platform.startswith('openbsd')
AIX = sys.platform.startswith('aix')


def tan():
    if WINDOWS:
        subprocess.call(['explorer', os.curdir], stderr=None, stdout=None)

    elif LINUX:
        subprocess.call(['xdg-open', '--', os.curdir], stderr=None, stdout=None)

    elif DARWIN:
        subprocess.call(['open', '--', os.curdir], stderr=None, stdout=None)

    else:
        print("Unknown Operation System ")


def tan_cli():
    try:
        assert sys.version_info.major >= 3
        assert sys.version_info.minor >= 6
    except Exception as ex:
        print("Tan only support 3.6+!")
        return

    threading.Thread(target=tan, args=()).start()


def tancp_cli():
    try:
        assert sys.version_info.major >= 3
        assert sys.version_info.minor >= 6
    except Exception as ex:
        print("Tan only support 3.6+!")
        return
    pyperclip.copy(os.path.abspath(os.curdir))


def msg_align(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    re = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        re += placeholder
        slen += 1
    return re


def tanls_cli():
    try:
        assert sys.version_info.major >= 3
        assert sys.version_info.minor >= 6
    except Exception as ex:
        print("Tan only support 3.6+!")
        return

    abs_path = os.path.abspath(os.curdir)
    if not os.path.isdir(abs_path):
        return

    title_msg = msg_align(Fore.BLUE + "FileName", 70) + msg_align(Fore.GREEN + "FileSize", 35)
    print(title_msg)

    for file in os.listdir(abs_path):
        abs_file_path = os.path.join(abs_path, file)

        data_msg = Fore.BLUE + abs_file_path
        item_msg = msg_align(data_msg, 70)

        if os.path.isfile(abs_file_path):
            file_size = os.path.getsize(abs_file_path)

            begin_msg = "{fore}{data_msg}".format(
                fore=Fore.GREEN,
                data_msg=data_msg)

            last_msg = "{fore}{size}".format(
                fore=Fore.GREEN,
                size=file_size)

            last_msg = msg_align(last_msg, 15) + "bytes"
            item_msg = msg_align(begin_msg, 70) + msg_align(last_msg, 20)
        print(item_msg)
