#!/usr/bin/env python3
import argparse
import json
import sys

from tqdm import tqdm

from ucca import normalization, validation
from ucca.convert import from_json
from ucca.ioutil import write_passage
from uccaapp.api import ServerAccessor

desc = """Download task from UCCA-App and convert to a passage in standard format"""


class TaskDownloader(ServerAccessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def download_tasks(self, task_ids, by_filename=False, validate=None, log=None, **kwargs):
        if by_filename:
            task_ids_from_file = []
            for filename in task_ids:
                with open(filename, 'r') as f:
                    task_ids_from_file += list(filter(None, map(str.strip, f)))
            task_ids = task_ids_from_file
        validate_h = open(validate, "w", encoding="utf-8") if validate else None
        log_h = open(log, "w", encoding="utf-8") if log else None
        for task_id in tqdm(task_ids, unit=" tasks", desc="Downloading"):
            yield self.download_task(task_id, validate=validate_h, log=log_h, **kwargs)
        if validate:
            validate_h.close()
        if log:
            log_h.close()

    def download_task(self, task_id, normalize=False, write=True, validate=None, binary=None, log=None, out_dir=None,
                      prefix=None, by_external_id=False, verbose=False, write_valid_only=False, **kwargs):
        del kwargs
        task = self.get_user_task(task_id)
        user_id = task["user"]["id"]
        try:
            passage = from_json(task, by_external_id=by_external_id)
        except ValueError as e:
            raise ValueError("Failed reading json for task %s:\n%s" % (task_id, json.dumps(task))) from e
        if normalize:
            try:
                normalization.normalize(passage)
            except AssertionError as e:
                raise ValueError("Failed normalizing task %s:\n%s" % (task_id, json.dumps(task))) from e
        if log:
            print(passage.ID, task_id, user_id, task["user_comment"], task["created_at"], task["updated_at"],
                  file=log, sep="\t", flush=True)
        ret = passage, task_id, user_id
        if validate or write_valid_only:
            for error in validation.validate(passage, linkage=False):
                if validate:
                    print(passage.ID, task_id, user_id, error, file=validate, sep="\t", flush=True)
                if write_valid_only:
                    return ret
        if write:
            write_passage(passage, binary=binary, outdir=out_dir, prefix=prefix, verbose=verbose)
        return ret

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("task_ids", nargs="+", help="IDs of tasks to download and convert")
        argparser.add_argument("-f", "--by-filename", action="store_true", help="treat task_ids as a filename, "
                                                                                "otherwise it is a list of IDs")
        TaskDownloader.add_write_arguments(argparser)
        argparser.add_argument("-V", "--validate", help="run validation on downloaded passages and save errors to file")
        argparser.add_argument("-N", "--normalize", action="store_true", help="normalize downloaded passages")
        argparser.add_argument("-l", "--log", help="filename to write log of downloaded passages to")
        ServerAccessor.add_arguments(argparser)

    @staticmethod
    def add_write_arguments(argparser):
        argparser.add_argument("-o", "--out-dir", default=".", help="output directory")
        argparser.add_argument("-p", "--prefix", default="", help="output filename prefix")
        argparser.add_argument("-x", "--by-external-id", action="store_true", help="save filename by external ID")
        argparser.add_argument("-b", "--binary", action="store_true", help="write in binary format (.pickle)")
        argparser.add_argument("-n", "--no-write", action="store_false", dest="write", help="do not write files")
        argparser.add_argument("--write-valid-only", action="store_true", help="only write passages that passed "
                                                                               "validation")


def main(**kwargs):
    list(TaskDownloader(**kwargs).download_tasks(**kwargs))


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    TaskDownloader.add_arguments(argument_parser)
    main(**vars(argument_parser.parse_args()))
    sys.exit(0)
