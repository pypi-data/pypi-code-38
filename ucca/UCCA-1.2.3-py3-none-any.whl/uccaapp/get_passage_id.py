#!/usr/bin/env python3
import sys

import argparse
from tqdm import tqdm

from uccaapp.api import ServerAccessor

desc = """Get passage ID for tasks"""


class PassageIdGetter(ServerAccessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_passage_ids(self, filename, **kwargs):
        del kwargs
        with open(filename, encoding="utf-8") as f:
            task_ids = list(map(str.strip, f))
        for task_id in tqdm(task_ids, unit=" tasks", desc="Getting passage IDs"):
            task = self.get_task(task_id)
            passage_id = task["passage"]["id"]
            yield passage_id

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("filename", help="file with lines of the form <TASK ID>")
        ServerAccessor.add_arguments(argparser)


def main(**kwargs):
    print(*PassageIdGetter(**kwargs).get_passage_ids(**kwargs), sep="\n")


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    PassageIdGetter.add_arguments(argument_parser)
    main(**vars(argument_parser.parse_args()))
    sys.exit(0)
