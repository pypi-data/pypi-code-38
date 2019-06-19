#!/usr/bin/env python3
import sys

import argparse
from tqdm import tqdm

from uccaapp.api import ServerAccessor

desc = """Sets the status of submitted tasks to ONGOING"""

ONGOING_STATUS = "ONGOING"


class TaskStatusSetter(ServerAccessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_task_status(self, status, filename, **kwargs):
        del kwargs
        with open(filename) as f:
            task_ids = list(f.readlines())
        for task_id in task_ids:
            task = self.get_task(int(task_id))
            task["status"] = status
            task_out = self.update_task(**task)
            assert task_out["status"] == status
            yield task_out

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("filename", help="file with lines, each with a different task ID")
        ServerAccessor.add_arguments(argparser)


def main(**kwargs):
    list(TaskStatusSetter(**kwargs).set_task_status(status=ONGOING_STATUS, **kwargs))


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    TaskStatusSetter.add_arguments(argument_parser)
    main(**vars(argument_parser.parse_args()))
    sys.exit(0)
