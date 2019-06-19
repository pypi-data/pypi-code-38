#!/usr/bin/env python3
import sys

import argparse
import json
import requests

from ucca import convert
from ucca import normalization, validation
from uccaapp.api import ServerAccessor

desc = """Sets the status of submitted tasks to ONGOING"""

SUBMITTED_STATUS = "SUBMITTED"

class TaskSubmitter(ServerAccessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def submit_tasks(self, filename, log_file, **kwargs):
        del kwargs
        log_file = open(log_file,'w')
        with open(filename) as f:
            task_ids = list(f.readlines())
        for task_id in task_ids:
            try:
                task_id = task_id.strip()
                task = self.get_user_task(int(task_id))
                if task['type'] not in ['ANNOTATION', 'REVIEW']:
                    print(task_id, "NOT AN ANNOTATION/REVIEW TASK", file=log_file, sep="\t", flush=True)
                    continue
                try:
                    passage = convert.from_json(task)
                except ValueError as e:
                    raise ValueError("Failed reading json for task %s:\n%s" % (task_id, json.dumps(task))) from e
                # validate the task
                normalization.normalize(passage)
                validation_errors = list(validation.validate(passage, linkage=False))
                if len(validation_errors) == 0:
                        self.submit_task(**task)
                        print(task_id, "SUBMITTED", file=log_file, sep="\t", flush=True)
                else:
                    for error in validation_errors:
                        print(task_id, error, file=log_file, sep="\t", flush=True)
            except requests.exceptions.HTTPError as e:
                print(task_id, "HTTP Request Error: "+str(e), file=log_file, sep="\t", flush=True)


    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("filename", help="file with lines, each with a different task ID")
        argparser.add_argument("-l","--log_file", help="output log file")

        ServerAccessor.add_arguments(argparser)


def main(**kwargs):
    TaskSubmitter(**kwargs).submit_tasks(**kwargs)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    TaskSubmitter.add_arguments(argument_parser)
    main(**vars(argument_parser.parse_args()))
    sys.exit(0)


