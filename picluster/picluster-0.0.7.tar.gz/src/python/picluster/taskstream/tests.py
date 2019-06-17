import pytest
from .primitive import cli
from .cli_tasks import ls
from . import cli_tasks as cli


def a_simple_ls_command():
    ls.subscribe(print)  # shows files under directory


def touch_chaning_test():
    task = sequential(lambda _: cli.mkdir("test"), lambda d: cli.touch("some.txt"))
    task.subscribe()


def parallel_test():
    taks = sequential(
        lambda _: cli.mkdir("testdir"),
        lambda d: parallel([cli.mkdir(d / f"sub.{i}") for i in range(10)]),
    )
    task.subscribe()
