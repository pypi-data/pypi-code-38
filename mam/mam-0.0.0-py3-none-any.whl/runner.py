"""Build and run nox tasks."""

import os
import shlex
from typing import Any, Callable

# nosa(6): pylint[E0401],mypy[:Cannot find module named]
import mam
from mam._mam.keys import TTask, Task

import nox

import yaml


def build_task(task: TTask) -> Callable[[Any], None]:
    """Build Nox task."""
    def function(session) -> None:
        """Run nox task."""
        os.chdir(CWD)
        session.install(*task[Task.DEPS])
        _status_code, output = mam.run(
            session,
            *shlex.split(task[Task.COMMAND]),
            *(task.get('args') or []),
        )
        converter = mam.find(task[Task.CONVERTER]).obj
        mam.write_output(task, output, converter, session.posargs)

    kwargs = {}
    if task.get(Task.PYTHON) is not None:
        kwargs['python'] = task.get(Task.PYTHON)

    function.__name__ = task[Task.NAME]
    return nox.session(**kwargs)(function)


def _build_tasks() -> None:
    with open('./configs/_mam.yaml') as config_file:
        data = yaml.safe_load(config_file)

    for task in data.get('tasks', []):
        build_task(task)


CWD = os.getcwd()  # https://github.com/theacodes/nox/issues/197
_build_tasks()
