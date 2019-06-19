#!/usr/bin/env python3
import sys

import argparse
import re
from glob import glob

from ucca.convert import to_json, from_text
from uccaapp.api import ServerAccessor

try:
    from simplejson.scanner import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError

desc = """Upload passages from CoNLL-U files including complete tokenization, and create annotation task for each"""


class ConlluPassageUploader(ServerAccessor):
    def __init__(self, user_id, annotation_user_id, source_id, project_id, **kwargs):
        super().__init__(**kwargs)
        self.set_source(source_id)
        self.set_project(project_id)
        self.set_user(user_id)
        self.annotation_user = dict(id=annotation_user_id) if annotation_user_id else self.user
        
    def upload_passages(self, filenames, **kwargs):
        del kwargs
        for pattern in filenames:
            filenames = sorted(glob(pattern))
            if not filenames:
                raise IOError("Not found: " + pattern)
            for filename in sorted(filenames):
                with open(filename, encoding="utf-8") as f:
                    external_id = None
                    tokens = []
                    try:
                        for line in f:
                            line = line.strip()
                            m = re.match(r"^# sent_id = (.*)", line)
                            if m:
                                external_id = m.group(1)
                            elif line:
                                tokens.append(line.split("\t")[1])
                            else:
                                self.upload_passage(external_id, tokens)
                                external_id = None
                                tokens = []
                        if tokens:
                            self.upload_passage(external_id, tokens)
                    except (IndexError, AssertionError) as e:
                        raise ValueError(filename) from e

    def upload_passage(self, external_id, tokens):
        assert external_id, "Missing external ID for passage %s" % tokens
        assert tokens, "Empty passage %s" % external_id
        passage_out = self.create_passage(text=" ".join(tokens), external_id=external_id, type="PUBLIC",
                                          source=self.source)
        task_in = dict(type="TOKENIZATION", status="SUBMITTED", project=self.project, user=self.user,
                       passage=passage_out, manager_comment="External ID: "+external_id,
                       user_comment="", parent=None, is_demo=False, is_active=True)
        tok_task_out = self.create_task(**task_in)
        tok_user_task_in = dict(tok_task_out)
        passage = list(from_text(tokens, tokenized=True))[0]
        tok_user_task_in.update(to_json(passage, return_dict=True, tok_task=True))
        self.submit_task(**tok_user_task_in)
        task_in = dict(type="ANNOTATION", status="NOT_STARTED", project=self.project, user=self.annotation_user,
                       passage=tok_task_out["passage"], manager_comment="External ID: "+external_id,
                       user_comment=external_id, parent=tok_task_out, is_demo=False, is_active=True)
        self.create_task(**task_in)
        print("Uploaded passage "+external_id+" successfully")

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("filenames", nargs="+", help="filename pattern of CoNLL-U files")
        ServerAccessor.add_project_id_argument(argparser)
        ServerAccessor.add_source_id_argument(argparser)
        ServerAccessor.add_user_id_argument(argparser)
        argparser.add_argument("--annotation-user-id", type=int, help="user id for annotation tasks, if different")
        ServerAccessor.add_arguments(argparser)


def main(**kwargs):
    ConlluPassageUploader(**kwargs).upload_passages(**kwargs)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    ConlluPassageUploader.add_arguments(argument_parser)
    main(**vars(argument_parser.parse_args()))
    sys.exit(0)

