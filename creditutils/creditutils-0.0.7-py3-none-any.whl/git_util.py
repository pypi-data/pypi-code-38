# -*- coding:UTF-8 -*-

'''
Created on 2014年12月8日

@author: caifh
'''
import subprocess
# import traceback
import re
import os

_CMD_PATH = 'git'


def set_cmd_path(cmd_path):
    if cmd_path:
        global _CMD_PATH
        _CMD_PATH = cmd_path


def clone(url, _dir='.', revision=None, branch=None):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)
        args = []
        args.append(_CMD_PATH)
        args.append('clone')
        if branch:
            args.append('-b')
            args.append(branch)
        args.append(url)
        subprocess.check_call(args)

        if revision:
            git_root = get_git_root(dst_dir)
            switch_to_revision(revision, git_root)

        return True
    except subprocess.CalledProcessError:
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)



# 判断工作区是否存在文件修改
def has_change(_dir='.'):
    # example: "nothing to commit, working tree clean"
    _STATUS_WORK_CLEAN_PATTERN = 'working\s+tree\s+clean'
    _STATUS_UNTRACKED_FILES_PATTERN = 'nothing\s+added\s+to\s+commit\s+but\s+untracked\s+files\s+present'
    info = get_status_info(_dir)
    match = re.search(_STATUS_WORK_CLEAN_PATTERN, info, re.I)
    if match:
        return False
    else:
        match = re.search(_STATUS_UNTRACKED_FILES_PATTERN, info, re.I)
        if match:
            return False
        else:
            return True


# 撤消暂存区及工作区修改
def revert(_dir='.'):
    revert_temporary(_dir)

    is_changed = has_change(_dir)
    if is_changed:
        revert_work(_dir)


# 撤消工作区修改
def revert_work(_dir='.'):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('checkout')
        args.append('--')
        args.append('"*"')

        subprocess.check_call(args)

        return True
    except subprocess.CalledProcessError:
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


# 撤消暂存区修改
def revert_temporary(_dir='.'):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('reset')
        args.append('--hard')

        subprocess.check_call(args)

        return True
    except subprocess.CalledProcessError:
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


def update(_dir='.', revision=None, branch=None):
    update_to_head(_dir, branch)
    if revision:
        switch_to_revision(revision, _dir)


def update_to_head(_dir='.', branch=None):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        # example: git pull origin master
        args = []
        args.append(_CMD_PATH)
        args.append('pull')
        args.append('origin')
        if branch:
            args.append(branch)
        else:
            args.append('master')

        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        # 打印异常堆栈信息
        #         excep_str = traceback.format_exc()
        #         print(excep_str)
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


def switch_to_revision(revision, _dir='.'):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        # example: git pull origin master
        args = []
        args.append(_CMD_PATH)
        args.append('reset')
        args.append('--hard')
        args.append(revision)

        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        # 打印异常堆栈信息
        #         excep_str = traceback.format_exc()
        #         print(excep_str)
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


# 将文件添加到暂存区
def add(paths, _dir='.'):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('add')

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
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


# 提交修改文件到本地配置库中(暂未验证)
def commit(msg=None, paths=None, _dir='.'):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('commit')
        if msg:
            args.append('-m')
            args.append(msg)

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
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


# 提交本地配置库中的文件到远程配置库中(暂未验证)
def push(repository=None, refspecs=None, _dir='.'):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('push')

        if repository:
            args.append(repository)

        if refspecs:
            for item in refspecs:
                args.append(item)

        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        # 打印异常堆栈信息
        #         excep_str = traceback.format_exc()
        #         print(excep_str)
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


def get_statuses(dirs):
    statuses = {}
    for item in dirs:
        statuses[item] = is_repository(item)

    return statuses


def is_repository(_dir='.'):
    # example: "git status"
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('status')

        subprocess.check_call(args, stderr=subprocess.STDOUT)

        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


# 获取git状态信息
def get_status_info(_dir='.'):
    # example: "git status"
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('status')

        return subprocess.check_output(args, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError:
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)

# 老的实现方式过于复杂
def get_revision_old(_dir='.'):
    # example: "commit 9f6854dc1a505b11e55616d93b0e98ac91905ec9 "
    _STATUS_PATTERN = '^commit\s+(\w+)\s+.*'

    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('log')

        #         result = subprocess.check_output(args, stderr=subprocess.STDOUT, universal_newlines=True)
        #         print('result:' + result)

        proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=False)
        outs = proc.communicate(input='q'.encode(encoding='utf_8', errors='strict'))[0].decode('utf-8')

        #         print(outs)
        if outs:
            match = re.match(_STATUS_PATTERN, outs, re.I)
            if match:
                revision = match.group(1)
                #                 print(revision)
                return revision
            else:
                raise Exception('Failed to get revision of {}!'.format(dst_dir))
    except subprocess.CalledProcessError:
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)

# 获取git版本信息(新方式，更简洁)
def get_revision(_dir='.'):
    # example: "git status"
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        args = []
        args.append(_CMD_PATH)
        args.append('rev-parse')
        args.append('HEAD')

        rtn_str = subprocess.check_output(args, universal_newlines=True)
        return rtn_str.strip()
    except subprocess.CalledProcessError:
        raise
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)

def get_git_root(code_root):
    sub_list = os.listdir(code_root)
    valid_dir = []
    for item in sub_list:
        item_path = os.path.join(code_root, item)
        if os.path.isdir(item_path):
            match = re.match('^\w.*', item)
            if match:
                valid_dir.append(item)

    if len(valid_dir) == 1:
        return os.path.join(code_root, valid_dir[0])
    else:
        raise Exception('Failed to get git directory on {}!'.format(code_root))


# 如果不存在代码，则checkout，存在代码，则执行更新操作
def checkout_or_update(code_root, code_url, revision=None, branch=None):
    if not os.path.isdir(code_root):
        os.makedirs(code_root)
        clone(code_url, code_root, revision, branch)
    else:
        sub_items = os.listdir(code_root)
        if sub_items:
            git_root = get_git_root(code_root)
            is_exists = is_repository(git_root)
            if is_exists:
                revert_submodules(git_root)
                revert(git_root)
                update(git_root, revision, branch)
            else:
                clone(code_url, code_root, revision, branch)
        else:
            clone(code_url, code_root, revision, branch)


def push_to_remote(paths, msg=None, repository=None, refspecs=None, _dir='.'):
    add(paths, _dir)
    commit(msg, paths, _dir)
    push(repository, refspecs, _dir)


# 更新或者拉取submodules
#   :param paths 项目路径(.gitmodules 所在路径)
#   :param modules_name submodules 名称
#   :param branch 更新的分支名称(默认为master)
#   :param need_remote 是否需要submodule拉取最新代码(默认为拉取)
def update_submodules(paths, modules_name, branch, need_remote=True):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(paths)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)

        subprocess.call([_CMD_PATH, 'submodule', 'init'])
        subprocess.call([_CMD_PATH, 'config', '-f', '.gitmodules', 'submodule.{}.branch'.format(modules_name), branch])
        if need_remote:
            subprocess.call([_CMD_PATH, 'submodule', 'update', '--recursive', '--remote'])
        else:
            subprocess.call([_CMD_PATH, 'submodule', 'update', '--recursive'])
        print('update submodules success')

    except subprocess.CalledProcessError:
        raise

    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


# 回滚submodules工作区
def revert_submodules(paths):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(paths)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)
        subprocess.call([_CMD_PATH, 'submodule', 'foreach', 'git checkout -- "*"'])
        subprocess.call([_CMD_PATH, 'submodule', 'update', '--init'])

    except subprocess.CalledProcessError:
        raise

    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)
