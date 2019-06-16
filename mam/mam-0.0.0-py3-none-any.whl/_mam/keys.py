"""Common string values."""
# nosa: pylint[R0903]

from typing import Any, Dict

__all__ = [
    'TTask',
    'Task',
]


TTask = Dict[str, Any]


class Task:
    """Task names."""

    NAME = 'name'
    EXTENDS = 'extends'
    DEPS = 'deps'
    CONFIG_PATH = 'config_path'
    CONVERTER = 'converter'
    PYTHON = 'python'
    COMMAND = 'command'
