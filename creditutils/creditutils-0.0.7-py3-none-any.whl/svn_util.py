# -*- coding:UTF-8 -*-

'''
Created on 2014年12月8日

@author: caifh
'''
import subprocess
# import traceback
import re
import os
import creditutils.file_util as myfile
import filecmp

_SVN_PATH = 'svn'
_SVN_USERNAME=None
_SVN_PASSWORD=None

def set_user_info(username, password):
    global _SVN_USERNAME
    global _SVN_PASSWORD
    
    _SVN_USERNAME = username
    _SVN_PASSWORD = password

def set_svn_path(svn_path):
    if svn_path:
        global _SVN_PATH
        _SVN_PATH = svn_path

def checkout(url, _dir=None, revision=None):
    try:
        args = []
        args.append(_SVN_PATH)
        args.append('checkout')
        if _SVN_USERNAME and _SVN_PASSWORD:
            args.append('--username')
            args.append(_SVN_USERNAME)
            args.append('--password')
            args.append(_SVN_PASSWORD)
        
        if revision:
            url_info = '{}@{}'.format(url, revision)
        else:
            url_info = url
            
        args.append(url_info)
        
        if _dir:
            args.append(_dir)
        
        subprocess.check_call(args)
        
        return True
    except subprocess.CalledProcessError:
        raise

# 撤消修改
def revert(_dir='.'):
    try:
        args = []
        args.append(_SVN_PATH)
        args.append('revert')
        if _SVN_USERNAME and _SVN_PASSWORD:
            args.append('--username')
            args.append(_SVN_USERNAME)
            args.append('--password')
            args.append(_SVN_PASSWORD)
        args.append('-R')
        args.append(_dir)
        
        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        raise

def update(_dir='.', revision=None):
    try:
        args = []
        args.append(_SVN_PATH)
        args.append('update')
        
#         print('svn user: ', _SVN_USERNAME)
#         print('svn pwd: ', _SVN_PASSWORD)
        if _SVN_USERNAME and _SVN_PASSWORD:
            args.append('--username')
            args.append(_SVN_USERNAME)
            args.append('--password')
            args.append(_SVN_PASSWORD)

        if revision:
            args.append('-r')
            args.append(str(revision))
        
        args.append(_dir)
        
        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        # 打印异常堆栈信息
#         excep_str = traceback.format_exc()
#         print(excep_str)
        raise

# 为文件添加svn控制
def add(paths):
    try:
        args = []
        args.append(_SVN_PATH)
        args.append('add')
        if _SVN_USERNAME and _SVN_PASSWORD:
            args.append('--username')
            args.append(_SVN_USERNAME)
            args.append('--password')
            args.append(_SVN_PASSWORD)
#         args.append('-q')

        if paths:
            for item in paths:
                args.append(item)
        
        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        # 打印异常堆栈信息
#         excep_str = traceback.format_exc()
#         print(excep_str)
        raise

# 提交已经在svn控制中的文件
def commit(msg, paths=None):
    try:
        args = []
        args.append(_SVN_PATH)
        args.append('ci')
        if _SVN_USERNAME and _SVN_PASSWORD:
            args.append('--username')
            args.append(_SVN_USERNAME)
            args.append('--password')
            args.append(_SVN_PASSWORD)
#         args.append('-q')
        args.append('-m')
        args.append(msg)
        
        if paths:
            for item in paths:
                args.append(item)
        else:
            args.append('.')
        
        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        # 打印异常堆栈信息
#         excep_str = traceback.format_exc()
#         print(excep_str)
        raise
            
def get_statuses(dirs):
        svn_statuses = {}
        for item in dirs:
            svn_statuses[item] = status(item)
            
        return svn_statuses
        
def status(_dir='.'):
    # example: "svn: warning: W155007: 'D:\temp' is not a working copy"
    _STATUS_PATTERN = '^svn\:\s+warning.*is\s+not\s+a\s+working\s+copy\s*$'
    
    try:
        args = []
        args.append(_SVN_PATH)
        args.append('status')
        if _SVN_USERNAME and _SVN_PASSWORD:
            args.append('--username')
            args.append(_SVN_USERNAME)
            args.append('--password')
            args.append(_SVN_PASSWORD)
        args.append(_dir)
        
        result = subprocess.check_output(args, stderr=subprocess.STDOUT, universal_newlines=True)
#         print('result:' + result)
        
        match = re.match(_STATUS_PATTERN, result, re.I|re.S)
        if match:
            return False
        else:
            return True
    except subprocess.CalledProcessError:
        raise
    
def get_revision(_dir='.'):
    # example: " 8750     8274 guanyf       common\input_verify\lua\landline.lua "
    _STATUS_PATTERN = '^\s*\d+\s+(\d+)\s+\w+\s+[^\s]+\s*$'
    
    try:
        args = []
        args.append(_SVN_PATH)
        args.append('status')
        if _SVN_USERNAME and _SVN_PASSWORD:
            args.append('--username')
            args.append(_SVN_USERNAME)
            args.append('--password')
            args.append(_SVN_PASSWORD)
            
        args.append('-v')
        args.append(_dir)
        
        result = subprocess.check_output(args, stderr=subprocess.STDOUT, universal_newlines=True)
        max_ver = 0
#         print('result:' + result)
        
        if result:
            items = re.split('[\r\n]+', result)
            
            for item in items:
                match = re.match(_STATUS_PATTERN, item, re.I)
                if match:
                    ver = int(match.group(1))
                    if ver > max_ver:
                        max_ver = ver
            
        return str(max_ver)
    except subprocess.CalledProcessError:
        raise
    
# 如果不存在代码，则checkout，存在代码，则执行更新操作
def checkout_or_update(code_root, svn_url, revision=None):
    if not os.path.isdir(code_root):
        checkout(svn_url, code_root, revision)
    else:
        svn_status = status(code_root)
        if svn_status:
            revert(code_root)
            update(code_root, revision)
        else:
            checkout(svn_url, code_root, revision)
            
def update_file(target_file, new_file, msg):
    base_dir = os.path.dirname(target_file)
    
    # 先判断svn目录状态是否正常
    if not status(base_dir):
        info = '{} is not a valid svn source directory!'.format(base_dir)
        raise Exception(info)
        
    if not filecmp.cmp(new_file, target_file, shallow=False):
        myfile.replace_file(new_file, target_file)
        svn_paths = []
        svn_paths.append(target_file)
        commit(msg, svn_paths)
    else:
        print('{} and {} is the same!'.format(new_file, target_file))