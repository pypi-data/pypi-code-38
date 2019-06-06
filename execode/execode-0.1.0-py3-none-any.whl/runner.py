# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import sys
import runpy
import importlib
import importlib.util

from fsoopify import FileInfo, NodeInfo, NodeType

from .pyinfo import get_pyinfo
from .finder import use_path


def run_py(path: str):
    '''
    run a file like `python ?`.
    '''

    py_file = FileInfo(path)
    if not py_file.is_file():
        raise FileNotFoundError(f'{path} is not a file')

    with use_path(py_file.path.dirname):
        return runpy.run_path(py_file.path, run_name='__main__')

def run_py_m(path: str):
    '''
    run a dir like `python -m ?`.

    `runpy.run_module()` only run the module in `sys.path`,
    but `run_py_m` can run the module from any path.
    '''

    node = NodeInfo.from_path(path)
    if not node:
        raise FileNotFoundError(f'{path} is not a file or dir')

    if node.node_type == NodeType.dir:
        pkg_dir = node # should be the dir which has a file __main__.py
        main_file = pkg_dir.get_fileinfo('__main__.py')
        if not main_file.is_file():
            raise FileNotFoundError(f'{pkg_dir.path} is not a module')
    else:
        main_file = node # user may pass `pkg/__main__.py`
        pkg_dir = node.get_parent()

    with use_path(pkg_dir.path.dirname):
        return runpy.run_module(pkg_dir.path.name, run_name='__main__')

def exec_pkg_py(path: str):
    '''
    exec a `.py` file which inside a package.
    the `.py` file can use relative import.

    this is helpful for dynimic exec some files.

    #### diff between `run_py` and `exec_pkg_py`

    - `run_py` run file by name `__name__`
    - `exec_pkg_py` run file by name which same with when you direct import

    #### diff between `exec_pkg_py` and `import_py`

    - `exec_pkg_py` can run file twice
    - `import_py` only run file once like you direct import
    '''

    node = NodeInfo.from_path(path)
    if not node.is_file():
        raise FileNotFoundError(f'{path} is not a file')

    pyinfo = get_pyinfo(node)
    kwargs = {
        pyinfo.get_top_package().name: pyinfo.get_sys_path_required()
    }
    with use_path(**kwargs):
        return runpy.run_path(node.path, run_name=pyinfo.name)


def import_py(path: str):
    '''
    import a `.py` file which inside a package or not.
    the `.py` file can use relative import.

    this is helpful for dynimic import some files.
    '''

    node = NodeInfo.from_path(path)
    if not node.is_file():
        raise FileNotFoundError(f'{path} is not a file')

    pyinfo = get_pyinfo(node)
    pyinfo.import_module()
