"""Load config."""

import json
from typing import Any, Callable

import yaml  # nosa: pylint[E0401]

from .config import Config
from ..find import find, find_system


def load_config(path_: str) -> Any:
    """Load the config at the specified path."""
    path = find_system(path_).path
    if path is None:
        raise ValueError("Can't find path {path_!r}".format(path_=path_))
    loader: Callable[[Any], Any]
    if path.endswith('.yaml'):
        loader = yaml.safe_load
    elif path.endswith('.json'):
        loader = json.load
    else:
        raise ValueError('No known loader for {0}'.format(path))
    with open(path) as file_object:
        return loader(file_object)


def load_configs(path: str) -> Config:
    """Load the config inheritance tree as Configs."""
    config = load_config(path)
    root = node = Config(config)
    while node.orig.get('bases') is not None:
        node.parent = Config(load_config(node.orig.pop('bases')), p_node=node)
        node = node.parent
    return root


def load(path: str) -> Any:
    """Load the config and mutate it for use."""
    config = load_configs(path)
    config.reduce(config.MUTATIONS)
    config.reduce('_reduce')
    for reduces in config.output.get('_reduce') or []:
        for item in reduces or [None]:
            config.reduce(item)

    output = config.output
    for post_process in output.get('_post_process') or []:
        file_info = find(post_process)
        file_info.search(file_info.module)(output)
    return output
