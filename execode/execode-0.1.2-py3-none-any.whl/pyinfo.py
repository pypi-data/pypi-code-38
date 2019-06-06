# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import sys
import abc
import importlib
import importlib.util
from typing import Union, List

from fsoopify import NodeType, NodeInfo, DirectoryInfo, FileInfo, Path

from .finder import PATH_MAP

class IPyInfo(abc.ABC):
    def __init__(self, path: Path, mro_name: List[str]):
        self._path = path
        self._mro_name = mro_name

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        '''
        when you import the .py file, this should be the key in `sys.modules`
        '''
        return '.'.join(self._mro_name)

    @property
    @abc.abstractmethod
    def is_package(self):
        '''
        get whether the .py is a package or not.

        return True when the path endswith a `__init__.py`
        '''
        raise NotImplementedError

    @property
    def is_top_module(self):
        return len(self._mro_name) == 1

    @abc.abstractmethod
    def get_parent_package(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_top_package(self):
        raise NotImplementedError

    def get_sys_path_required(self):
        return self.get_top_package().path.get_parent(2).get_abspath()

    @abc.abstractmethod
    def import_module(self):
        raise NotImplementedError


class PyFileInfo(IPyInfo):
    @property
    def is_package(self):
        return False

    def get_parent_package(self):
        if len(self._mro_name) == 1:
            raise RuntimeError(f'{self!r} is not in any package')

        else:
            return PyPackageInfo(
                self._path.get_parent(1) / '__init__.py',
                self._mro_name[:-1]
            )

    def get_top_package(self):
        return self.get_parent_package().get_top_package()

    def import_module(self):
        try:
            return sys.modules[self.name]
        except KeyError:
            pass

        if self.is_top_module:
            # single .py file
            path = str(self.path)
            spec = importlib.util.spec_from_file_location(self.name, path)
            assert spec.name == self.name
            # code is base on `importlib._bootstrap._load_unlocked()`
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            return module

        else:
            self.get_top_package()._setup_finder()
            return importlib.import_module(self.name)


class PyPackageInfo(IPyInfo):
    @property
    def is_package(self):
        return True

    def get_parent_package(self):
        if len(self._mro_name) == 1:
            raise RuntimeError(f'{self!r} is top package')

        else:
            return PyPackageInfo(
                self._path.get_parent(2) / '__init__.py',
                self._mro_name[:-1]
            )

    def get_top_package(self):
        if len(self._mro_name) == 1:
            return self

        return PyPackageInfo(
            self._path.get_parent(len(self._mro_name)) / '__init__.py',
            [self._mro_name[0]]
        )

    def _setup_finder(self):
        assert self.is_top_module
        PATH_MAP[self.name] = str(self.path.get_parent(2))

    def import_module(self):
        try:
            return sys.modules[self.name]
        except KeyError:
            pass

        self.get_top_package()._setup_finder()
        return importlib.import_module(self.name)


def get_pyinfo(node: Union[NodeInfo, str]):
    path: Path = None
    rmro_name: List[str] = []

    def resolve_from_dir(node: DirectoryInfo):
        init = node.get_fileinfo('__init__.py')
        if init.is_file():
            rmro_name.append(node.path.name)
            resolve_from_dir(node.get_parent())

    def resolve_from_file(node: FileInfo):
        if node.path.name != '__init__.py':
            rmro_name.append(node.path.name.pure_name)
        resolve_from_dir(node.get_parent())

    if isinstance(node, str):
        node = NodeInfo.from_path(node)
        if not node:
            raise FileNotFoundError(f'{node} is not exists')

    if node.node_type == NodeType.file:
        resolve_from_file(node)
        path = node.path

    elif node.node_type == NodeType.dir:
        resolve_from_dir(node)
        path = node.path / '__init__.py'

    else:
        raise NotImplementedError

    if not rmro_name:
        raise RuntimeError(f'{node!r} is not a python file or dir')

    mro_name = list(reversed(rmro_name))

    if node.node_type == NodeType.file:
        return PyFileInfo(path, mro_name)

    elif node.node_type == NodeType.dir:
        return PyPackageInfo(path, mro_name)
