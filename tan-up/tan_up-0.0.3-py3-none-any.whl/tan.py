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
import pyperclip

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


