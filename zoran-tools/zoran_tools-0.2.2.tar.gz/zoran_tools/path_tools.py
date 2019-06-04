"""
模块的主要功能是进行路径操作
"""

import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


filetypes=(
    ('text file', '*.md *.txt'),
    ('Word file', '*.doc *.docx'),
    ('CSV  file', '*.csv'),
    ('SQL  file', '*.sql *.hql'),
    ('Python file', '*.py'),
    ('Java file', '*.jar *.java *.class'),
    ('Go   file', '*.go'),
    ('All  file', '*'),
)


class ZPath(object):
    def __init__(self, path):
        self._path = path

    def __str__(self):
        return '<zoran_tools.Path>\n{}'.format(self.path)

    def __repr__(self):
        return self.__str__()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def abspath(self):
        return os.path.abspath(self.path)

    @property
    def dirname(self):
        return os.path.dirname(self.abspath)

    def join(self, *paths, split=True, new=False):
        if split:
            dir_name = os.path.splitext(self.abspath)[0]
        else:
            dir_name = self.path
        if new:
            return ZPath(os.path.join(dir_name, *paths))
        else:
            return os.path.join(dir_name, *paths)

    def make(self, split=True, new=False):
        if split:
            dir_name = os.path.splitext(self.abspath)[0]
        else:
            dir_name = self.path
        if not os.path.exists(dir_name) or not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        if new:
            return ZPath(dir_name)
        else:
            return dir_name

    def isdir(self):
        return os.path.isdir(self.path)

    def isfile(self):
        return os.path.isfile(self.path)

    def exist(self):
        return os.path.exists(self.abspath)

    def children(self):
        return {self.basename: os.listdir(self.path)}

    def tree(self, maxlevel=3):
        if maxlevel == 0:
            return self.basename
        try:
            return {
                self.basename: [
                    self.join(e, new=True).tree(maxlevel=maxlevel-1)
                    if self.join(e, new=True).isdir() else self.join(e, new=True).basename
                    for e in os.listdir(self.path)
                ]
            }
        except PermissionError:
            return self.basename

    def plot_tree(self, maxlevel=3):
        def _plot(node, plot='', level=0):
            if isinstance(node, str):
                plot += (' ' * 2) * (level + 1) + '|-- ' + node + '\n'
            elif isinstance(node, dict):
                for k in node:
                    v = node[k]
                    plot = _plot(plot=plot, node=k, level=level)
                    plot = _plot(plot=plot, node=v, level=level + 1)
            elif isinstance(node, list):
                node = sorted(node, key=lambda e: not isinstance(e, str))
                for i, e in enumerate(node):
                    plot = _plot(plot=plot, node=e, level=level + 1)
            return plot

        return _plot(node=self.tree(maxlevel=maxlevel))


class File(ZPath):
    pass


class Directory(ZPath):
    pass


def plot_tree(path=None, maxlevel=3):
    if path is None:
        path = os.getcwd()
    return ZPath(path).plot_tree(maxlevel=maxlevel)


def list_files(directory=None, fm=None, return_abs=False, mode=None):
    """
    返回文件夹下的所有文件<list>
    :param directory: <str> 文件夹路径
        如果给出文件夹路径, 则返回该文件夹下的文件;
        如果没有给出文件夹路径, 则返回控制台所在文件夹下的文件
    :param fm: <str, list> 指定文件格式
        如果给出了文件格式, 则返回指定格式的文件;
        如果没有给出文件格式, 则返回所有文件
    :param isabspath: <bool> 为真时返回绝对路径文件名, 为假时返回相对路径文件名
    """
    if not directory:
        directory = os.getcwd()
    files = os.listdir(directory)

    if isinstance(mode, File):
        files = [file for file in files if os.path.isfile(file)]
    elif isinstance(mode, Directory):
        files = [file for file in files if os.path.isdir(file)]
    else:
        pass
    
    if isinstance(fm, str):
        fm = [fm]
    if isinstance(fm, (list, tuple)):
        fm = ['.{}'.format(e) for e in fm]
    files = [file for file in files if os.path.splitext(file)[-1] in fm]

    if return_abs:
        files = [os.path.abspath(file) for file in files]
    else:
        files = [os.path.basename(file) for file in files]

    return files


def create_father_dir(filename):
    """
    接收一个文件名, 判断其父路径是否存在, 如果不存在, 则创建
    :param filename: <str>接收的文件路径, 为相对路径
    """
    abs_filename = os.path.abspath(filename)
    father_dir = os.path.dirname(abs_filename)
    if not os.path.exists(father_dir) or not os.path.isdir(father_dir):
        os.makedirs(father_dir)
    return father_dir


def create_dir_same_as_filename(filename):
    """
    创建文件同名文件夹
    :param filename: <str>接收的文件路径, 为相对路径或绝对路径
    :param tail: <str>有时候生成的文件夹后要加个尾缀
    """
    abs_filename = os.path.abspath(filename)
    split_extension_abs_filename = os.path.splitext(abs_filename)[0]
    if os.path.exists(split_extension_abs_filename) and os.path.isdir(split_extension_abs_filename):
        return split_extension_abs_filename
    else:
        os.makedirs(split_extension_abs_filename)
        return split_extension_abs_filename


# tkinter.filedialog.asksaveasfile():选择以什么文件保存，创建文件并返回文件流对象
# tkinter.filedialog.askopenfile():选择打开什么文件，返回IO流对象
# tkinter.filedialog.askopenfiles():选择打开多个文件，以列表形式返回多个IO流对象
def get_goal_by_dialog_box(goal='file', filetype=None):
    """
    启用对话框, 以根据goal参数的不同选择文件或文件夹
    :param goal:
    :param filetype:
    :return: 返回文件名或文件夹名
    """
    root = tk.Tk()
    root.withdraw()

    goal_dict = {
        'file': filedialog.askopenfilename,
        'files': filedialog.askopenfilenames,
        'directory': filedialog.askdirectory,
        'dir': filedialog.askdirectory,
        'saveas': filedialog.asksaveasfilename,
        'save_as': filedialog.asksaveasfilename,
    }

    goal_func = goal_dict.get(goal)
    goal_name = goal_func(filetype=filetype) if isinstance(filetype, tuple) else goal_func()

    root.destroy()
    return goal_name


def ask_file(filetype=None):
    """
    打开一个对话框, 以选择文件, 返回文件路径.
    利用了tkinter框架
    示例：
    a = ask_file(filetype=(
        ('text file', '*.md *.txt'),
        ('word file', '*.doc *.docx'),
        ('all file', '*'),
        )
    )
    :return: 返回文件绝对路径名
    """
    return get_goal_by_dialog_box(goal='file', filetype=filetype)


def ask_files(filetype=None):
    """
    打开一个对话框, 以选择多个文件, 返回文件名列表
    :return:
    """
    return get_goal_by_dialog_box(goal='files', filetype=filetype)


def ask_dir():
    """
    打开一个对话框, 以选择文件夹, 返回文件夹名
    :return:
    """
    return get_goal_by_dialog_box(goal='directory')


def ask_save_as():
    """
    打开一个对话框，以选择文件名，如果文件名已存在，则询问是否覆盖
    :return:
    """
    return get_goal_by_dialog_box(goal='save_as')


def ask_chdir():
    """
    切换控制台路径
    :return:
    """
    return os.chdir(ask_dir())


def get_size(dir_or_file, unit='m'):
    """
    计算文件或文件夹的大小
    :param dir_or_file: 文件或文件夹路径
    :param unit: 返回的单位，默认为MB
    :return:
    """
    size = 0

    if os.path.isfile(dir_or_file):
        size = os.path.getsize(dir_or_file)
    elif os.path.isdir(dir_or_file):
        for root, dirs, files in os.walk(dir_or_file):
            size += sum(map(lambda e: os.stat(os.path.join(root, e)).st_size, files))
    else:
        return 0

    unit_dict = {
        'k': lambda x: x / 1024,
        'kb': lambda x: x / 1024,
        'm': lambda x: x / 1024 / 1024,
        'mb': lambda x: x / 1024 / 1024,
        'g': lambda x: x / 1024 / 1024 / 1024,
        'gb': lambda x: x / 1024 / 1024 / 1024,
    }

    return '{:.2f}'.format(unit_dict.get(unit.lower(), lambda x: x)(size))

