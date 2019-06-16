"""Builtin config post-processing."""

from __future__ import annotations

import collections
import logging
import os
from typing import (
    Any, Dict, Iterator, KeysView, List, Optional, Sequence, Tuple, Union,
)

from ...core.objects import PathFormatter

__all__ = [
    'expand_extensions',
    'expand_arguments',
    'reduce_arguments',
    'ensure_config_exists',
    'expand_format',
    'remove_internals',
    'remove_base',
]

# nosa(1): pylint[C0103]
logger = logging.getLogger(__name__)

TConfig = Dict[str, Any]
Task = Dict[str, Any]


def expand_extensions(config: TConfig) -> None:
    """Expand tasks extensions."""
    tasks: Dict[str, Task] = collections.OrderedDict()
    for task in config.get('tasks', None) or []:
        tasks[task['name']] = task

    new_tasks: Dict[str, Task] = collections.OrderedDict()
    for name, task in tasks.items():
        extensions = task.pop('extensions', None)
        new_tasks[name] = task
        if extensions is None:
            continue
        if not isinstance(extensions, list):
            raise ValueError('extensions must be a list')
        for ext in extensions:
            if isinstance(ext, str):
                ext = {
                    'name': ext,
                    'deps': [ext],
                }
                if not ext['name'].startswith(task['name']):
                    ext['name'] = task['name'] + '-' + ext['name']
            new_ext = task.copy()
            new_ext.update(ext)
            new_ext['deps'] = task['deps'] + ext['deps']
            new_ext['extends'] = (task.get('extends', None) or []) + [name]
            new_tasks[new_ext['name']] = new_ext
    config['tasks'] = list(new_tasks.values())


def expand_arguments(config: TConfig) -> None:
    """Expand task arguments."""
    for task in config.get('tasks', None) or []:
        args = task.get('args', None) or {}
        base = args.pop('$base', None) or {}
        if not base:
            continue

        for key, arg in args.items():
            if arg is None:
                new = None
            else:
                new = base.copy()
                new.update(arg)
            args[key] = new
        args['$base'] = base


def reduce_arguments(config: TConfig) -> None:
    """Reduce arguments to a list."""
    for task in config.get('tasks', None) or []:
        args = task.get('args', None) or {}
        args.pop('$base', None)
        task['args'] = [
            arg.get('arg', None)
            for arg in args.values()
            if arg is not None
        ]


def ensure_config_exists(config: TConfig) -> None:
    """Ensure the tasks config exists."""
    for task in config.get('tasks', None) or []:
        args = task.get('args', None) or {}
        config_ = args.get('config', None) or {}
        path = config_.get('value', None)
        if path is None or not os.path.exists(path):
            args['config'] = None


Key = Union[str, int]


# nosa: pylint[:Undefined variable 'Wrap'],pyflakes[:undefined name 'Wrap']
class Wrap:
    """Wrap objects for tree traversal."""

    _value: Any
    parent: Optional[Wrap]
    root: Wrap

    def __init__(self,
                 value: Any,
                 parent: Optional[Wrap] = None,
                 root: Optional[Wrap] = None,
                 ) -> None:
        self._value = value
        self.parent = parent
        if root is None:
            self.root = self
        else:
            self.root = root

    def keys(self) -> Union[Sequence[int], KeysView[str]]:
        """Get keys of contained type."""
        if isinstance(self._value, dict):
            return self._value.keys()
        elif isinstance(self._value, list):
            return range(len(self._value))
        return []

    def __getitem__(self, item: Key) -> Wrap:
        return Wrap(self._value[item], self, self.root)

    def __setitem__(self, key: Key, item: Any) -> None:
        self._value[key] = item

    def __delitem__(self, key: Key) -> None:
        del self._value[key]

    def __getattr__(self, item: Key) -> Wrap:
        return self[item]


FORMATTER = PathFormatter()
WrapKeys = List[Tuple[Wrap, Key]]


def _expand_format(wrap: Wrap,
                   ) -> Iterator[Tuple[WrapKeys, Wrap]]:
    """Expand format strings in config."""
    if isinstance(wrap._value, (dict, list)):
        for key in wrap.keys():
            for values in _expand_format(wrap[key]):
                values[0].append((wrap, key))
                yield values
    elif isinstance(wrap._value, str):
        yield ([], wrap)


def expand_format(config: TConfig) -> None:
    """Expand format strings in config."""
    for ((parent, key), *_), wrap in _expand_format(Wrap(config)):
        value = parent[key]._value
        if value.startswith('r!'):
            parent[key] = value[2:]
        elif any(i[1] is not None for i in FORMATTER.parse(value)):
            parent[key] = FORMATTER.format(value, self=wrap)


def remove_internals(config: TConfig) -> None:
    """Remove internal keys from config."""
    for key in list(config.keys()):
        if key.startswith('_'):
            config.pop(key)


def remove_base(config: TConfig) -> None:
    """Remove base from config."""
    for key in list(config.keys()):
        if key == 'base':
            config.pop(key)
