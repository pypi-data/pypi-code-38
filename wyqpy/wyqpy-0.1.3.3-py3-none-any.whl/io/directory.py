"""
Created on 2017年9月2日

:author: WYQ
"""

import os, shutil


def list_dir(dir_path):
    """
    :param dir_path: 
    """
    return os.listdir(dir_path)


def exist_dir(dir_path):
    """
    :param dir_path:
    """
    return os.path.isdir(dir_path)


def get_dir(dir_path, isCreate=True):
    """
    :param dir_path:
    :param isCreate:不存在是否创建
    """
    if exist_dir(dir_path):
        return dir_path
    else:
        if isCreate:
            make_dir(dir_path)
            return dir_path
        else:
            return None


def make_dir(dir_path):
    """
    :param dir_path: 
    """
    os.makedirs(dir_path)


def delete_dir(dir_path):
    """
    :param dir_path: 
    """
    os.removedirs(dir_path)


def copy_dir(old_dir_path, new_dir_path):
    """
    :param new_dir_path: 
    :param old_dir_path: 
    """
    shutil.copy(old_dir_path, new_dir_path)


def move_dir(old_dir_path, new_dir_path):
    """
    :param new_dir_path: 
    :param old_dir_path: 
    """
    shutil.move(old_dir_path, new_dir_path)


def rename_dir(old_dir_path, new_dir_path):
    """
    :param new_dir_path: 
    :param old_dir_path: 
    """
    os.rename(old_dir_path, new_dir_path)
