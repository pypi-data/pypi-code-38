#!/usr/bin/env python3
import sys

import argparse

from uccaapp.create_annotation_tasks import ServerAccessor, AnnotationTaskCreator

desc = """Upload a list of tokenization tasks to a project"""


class TokenizationTaskCreator(AnnotationTaskCreator):
    def __init__(self, project_id, **kwargs):
        super().__init__(**kwargs)
        self.set_project(project_id)

    def build_task(self, user_id, passage_id, **kwargs):
        del kwargs
        user = self.get_user(user_id)
        passage = self.get_passage(passage_id)
        return dict(type="TOKENIZATION", project=self.project, user=user, passage=passage,
                    manager_comment="passage #%s" % passage["id"], user_comment="", parent=None, is_demo=False,
                    is_active=True)

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("filename", help="a file where each line is a <User ID> <Passage ID>")
        argparser.add_argument("-l", "--log", help="filename to write log of uploaded passages to")
        ServerAccessor.add_project_id_argument(argparser)
        ServerAccessor.add_arguments(argparser)


def main(**kwargs):
    TokenizationTaskCreator(**kwargs).create_tasks(**kwargs)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    TokenizationTaskCreator.add_arguments(argument_parser)
    main(**vars(argument_parser.parse_args()))
    sys.exit(0)
