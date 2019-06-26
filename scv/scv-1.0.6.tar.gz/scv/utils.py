# -*- coding: UTF-8 -*-

import os, sys, platform, subprocess

def is_windows_system():
    return 'Windows' in platform.system()

def is_unix_system():
    return 'Linux' in platform.system() or 'Darwin' in platform.system()

def check_file_exists(filename):
    return os.path.exists(filename)

def check_file_exists_with_value(filename):
    if not os.path.exists(filename):
        return False
    with open(filename) as file:
        content = file
        file.close()
        return content

def cmd_with_check_os(cmd):
    '执行命令'
    return not os.system(cmd)

def cmd_with_check_os_value(cmd):
    '执行命令 与 返回内容'
    return subprocess.Popen(cmd, shell=True).wait()

def which(program):
    '获得命令路径'
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def is_virtual():
    '虚拟环境'
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))