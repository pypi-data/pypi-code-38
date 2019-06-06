# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import sys
from typing import Union, Optional
from collections import namedtuple
import contextlib
import abc

from fsoopify import NodeType, NodeInfo, DirectoryInfo, FileInfo, Path

def find_pipfile(node: Union[NodeInfo, str], depth: int = 10) -> Optional[Path]:
    '''
    find the first parent dir which has `Pipfile`, return the path of the `Pipfile`.

    return `None` if not found.
    '''

    def _find_pipfile(dir: DirectoryInfo, depth: int):
        if dir is None or depth == 0:
            return None
        pf = dir.get_fileinfo('Pipfile')
        if pf.is_file():
            return pf.path
        return _find_pipfile(dir.get_parent(), depth-1)

    if isinstance(node, str):
        node = NodeInfo.from_path(node)
        if not node:
            raise FileNotFoundError(f'{node} is not exists')

    if node.node_type == NodeType.file:
        node = node.get_parent()
        depth -= 1

    return _find_pipfile(node, depth)

def ensure_pipfile(node: Union[NodeInfo, str], depth: int = 10) -> Path:
    '''
    find the first parent dir which has `Pipfile`, return the path of the `Pipfile`.

    raise `FileNotFoundError` if not found.
    '''
    pipfile = find_pipfile(node, depth)
    if pipfile is None:
        raise FileNotFoundError(f'unable to find Pipfile for {node}')
    return pipfile

def find_pipenv_venv(cwd: str) -> Optional[str]:
    '''
    find venv path for pipenv by cwd.
    '''

    import subprocess

    result = subprocess.run(['pipenv', '--venv'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        encoding='utf-8', cwd=cwd)
    if result.returncode == 0:
        return result.stdout.strip()

@contextlib.contextmanager
def use_path(path):
    is_insert = path not in sys.path
    if is_insert:
        sys.path.insert(0, path)
    yield
    if is_insert:
        try:
            sys.path.remove(path)
        except ValueError:
            pass
