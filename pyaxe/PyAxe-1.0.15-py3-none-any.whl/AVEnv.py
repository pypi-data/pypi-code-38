#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import argparse

#===============================================================================
# 命令行参数解析
#===============================================================================
def _parseArgs():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('VEnvDir', help='待创建的虚拟环境目录')
    argParser.add_argument('--DevelopPackages', help='处于开发中的包路径列表', action='append')
    return argParser.parse_args()
g_Args = _parseArgs()


#===============================================================================
# 常量
#===============================================================================
VENV_DIR = g_Args.VEnvDir
VENV_DIR_PATH = os.path.abspath(VENV_DIR)
VENV_PYTHON_COMMAND = os.path.join(VENV_DIR_PATH, 'Scripts', 'python')
EASY_INSTALL_PTH = os.path.join(VENV_DIR_PATH, 'Lib', 'site-packages', 'easy-install.pth')

#===============================================================================
# 实用类和函数
#===============================================================================
class ChangeDir:
    def __init__(self, target):
        self.old_cwd = os.getcwd()
        self.target = target

    def __enter__(self):
        print('>>> cd ' + self.target)
        os.chdir(self.target)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        print('>>> cd ' + self.old_cwd)
        os.chdir(self.old_cwd)


#===============================================================================
# 主要功能函数
#===============================================================================
def getEasyInstallPthContent():
    if not os.path.exists(EASY_INSTALL_PTH):
        return ''
    with open(EASY_INSTALL_PTH) as fp:
        return fp.read()


#===============================================================================
# main
#===============================================================================
def main():
    if not os.path.exists(VENV_DIR):
        print(">>> 创建虚拟环境")
        if os.name == 'nt':
            cmd = 'py -3 -m venv %s' % VENV_DIR
        else:
            cmd = 'pyvenv %s' % VENV_DIR
        code = os.system(cmd)
        if code != 0:
            print('ERROR：创建虚拟环境失败：cmd=%s' % cmd)
            sys.exit(1)

    easyInstallPthContent = getEasyInstallPthContent()
    for package in g_Args.DevelopPackages:
        if os.path.abspath(os.path.normpath(package)).lower() in easyInstallPthContent:
            continue

        print(">>> 安装开发包：%s" % package)
        with ChangeDir(package):
            cmd = '%s setup.py develop' % VENV_PYTHON_COMMAND
            code = os.system(cmd)
            if code != 0:
                print('ERROR：安装 %s 失败：cmd=%s' % (package, cmd))
                sys.exit(2)

if __name__ == '__main__':
    main()