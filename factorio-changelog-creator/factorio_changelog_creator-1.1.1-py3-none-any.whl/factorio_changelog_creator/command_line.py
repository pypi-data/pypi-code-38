#!/usr/bin/env python

import argparse
import os
import json
from os.path import isdir, realpath
import logging

from .creator import create_changelog, get_format_filename, get_format_template

logger = logging.getLogger(__name__)


class WritableDirectoryAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values

        if not isdir(prospective_dir):
            os.mkdir(prospective_dir)

        if os.access(prospective_dir, os.W_OK):
            setattr(namespace, self.dest, realpath(prospective_dir))
            return

        raise argparse.ArgumentTypeError(
            "%s is not a writeable directory" % (prospective_dir,)
        )


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Factorio changelog generator")
    parser.add_argument(
        "output_dir",
        nargs="?",
        help="Directory where the files will be written",
        default=".",
        action=WritableDirectoryAction,
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="JSON file to parse for changes",
        default="changelog.json",
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "-f",
        "--formats",
        help="Which format[s] should be generated",
        default=["md", "ingame"],
        choices=["md", "ingame", "forum"],
        nargs="+",
    )
    parser.add_argument("-v", "--verbose", help="Output verbosity", action="count")
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    changelog = json.load(args.input_file)

    for output_format in args.formats:
        format_template = get_format_template(output_format)
        logger.info(format_template["message"])
        with open(
            os.path.join(args.output_dir, get_format_filename(output_format)),
            "w",
            encoding="utf-8",
        ) as output_file:
            output_file.write(create_changelog(changelog, format_template))


if __name__ == "__main__":
    pass
