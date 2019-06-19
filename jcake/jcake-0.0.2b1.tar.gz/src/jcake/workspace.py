#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
执行jcake工作空间的支持

"""

import os
import random

__all__ = ['create_new_workspace']


ROOT_DIR_NAME = '.jcake'
_POPULATION = ('abcdefghigklmnopqrstuvwxzy'
               'ABCDEFGHIGKLMNOPQRSTUVWXYZ'
               '0123456789')


def get_user_home():
    from os.path import expanduser
    return expanduser('~')


def get_or_create_root_dir():
    home = get_user_home()
    root_dir = os.path.join(home, ROOT_DIR_NAME)

    os.makedirs(root_dir, exist_ok=True)
    return root_dir


def next_workspace_name():
    """
    生成工作空间名称

    生成机制为获取当前所处目录名称 + 随机生成的

    """

    cur_dir = os.path.basename(os.getcwd())
    random_name = ''.join(random.sample(_POPULATION, 8))
    return cur_dir + '-' + random_name


def get_exist_workspace(workspace_root_dir):
    """
    获取已经存在的可用工作空间

    如果存在以当前所处目录名称-开头的目录直接返回，否则返回None

    Args:
      workspace_root_dir: 工作空间根目录

    Returns:
      可用的工作空间目录路径或None

    """
    cur_dir = os.path.basename(os.getcwd())
    canuse_workspace_prefix = cur_dir + '-'
    for name in os.listdir(workspace_root_dir):
        if name.startswith(canuse_workspace_prefix):
            return os.path.join(workspace_root_dir, name)

    return None


def create_new_workspace(workspace_root_dir):
    """
    创建新的工作空间

    使用当前操作系统用户目录作为父目录，其中.jcake作为整个工作目录的根目录

    Args:
      workspace_root_dir: 工作空间根目录

    Returns:
      工作空间目录路径

    """
    space_name = next_workspace_name()
    workspace_dir_path = os.path.join(workspace_root_dir, space_name)
    os.makedirs(workspace_dir_path)
    return workspace_dir_path


def get_or_create_worksapce():
    """ 获取或创建工作空间
    """

    root_dir_path = get_or_create_root_dir()
    workspace = get_exist_workspace(root_dir_path)
    return workspace if workspace is not None else create_new_workspace(
        root_dir_path
    )
