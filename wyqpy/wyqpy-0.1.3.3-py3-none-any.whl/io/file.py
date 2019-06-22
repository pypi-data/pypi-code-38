"""
Created on 2017年7月12日

:author: WYQ
"""

import os, shutil

def make_file(file_path):
    """
    创建空文件
    :param file_path:文件路径
    :return:
    """
    os.mknod(file_path)

def create_file(file_path,ret = False):
    """
    创建空文件
    :param file_path:文件路径
    :param ret:是否返回文件引用
    :return:
    """
    f= open(file_path,'w')
    if ret:
        return f
    else:
        f.close()


def read_all_text(file_path, encoding="utf-8"):
    """
    读取文件全部内容
    :param file_path:
    :return:文件全部内容

    """
    f = open(file_path, "rU", encoding=encoding)
    content = f.read()
    f.close()
    return content


def read_all_lines(file_path, encoding="utf-8"):
    """
    读取文件中的所有行
    :param file_path:
    :return:文件中的所有行
    """
    f = open(file_path, "r", encoding=encoding)
    content = f.readlines()
    f.close()
    ls = []
    for l in content:
        ls.append(l.rstrip('\n'))
    return ls


def read_one_line(file_path, n, encoding="utf-8"):
    """
    读取文件某一行
    :param file_path:
    :param n:
    :return:文件中的所有行
    """
    f = open(file_path, "r", encoding=encoding)
    content = f.readline(n)
    f.close()
    return content


def write_all_text(file_path, s, encoding="utf-8"):
    """
    写入文件全部内容
    :param file_path:
    """
    f = open(file_path, "w", encoding=encoding)
    f.write(s)
    f.close()


def write_all_lines(file_path, ss, encoding="utf-8"):
    """
    写入所有行
    :param file_path:
    """
    f = open(file_path, "w", encoding=encoding)
    for s in ss:
        f.writelines(s + "\n")
    f.close()


def append_all_text(file_path, s, encoding="utf-8"):
    """
    追加所有内容
    :param file_path:
    """
    f = open(file_path, "a", encoding=encoding)
    f.writelines(s)
    f.close()


def append_all_lines(file_path, ss, encoding="utf-8"):
    """
    追加所有行
    :param file_path:
    """
    f = open(file_path, "a", encoding=encoding)
    for s in ss:
        f.writelines(s + "\n")
    f.close()


def delete_file(file_path):
    """
    :param file_path: 
    """
    os.remove(file_path)


def copy_file(old_file_path, new_file_path):
    """
    :param new_file_path: 
    :param old_file_path: 
    """
    shutil.copy(old_file_path, new_file_path)


def move_file(old_file_path, new_file_path):
    """
    :param new_file_path: 
    :param old_file_path: 
    """
    shutil.move(old_file_path, new_file_path)


def rename_file(old_file_path, new_file_path):
    """
    :param new_file_path: 
    :param old_file_path: 
    """
    os.rename(old_file_path, new_file_path)
