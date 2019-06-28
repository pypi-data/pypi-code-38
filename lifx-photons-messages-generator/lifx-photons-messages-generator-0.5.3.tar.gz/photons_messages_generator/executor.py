from photons_messages_generator.generate import generate

from delfick_logging import setup_logging
from delfick_error import DelfickError
from ruamel.yaml import YAML
import argparse
import sys
import os

this_dir = os.path.dirname(__file__)

def make_parser():
    parser = argparse.ArgumentParser(description = "messages generator")

    def add_argument(name, **kwargs):
        environment_name = name.upper()

        if environment_name in os.environ:
            kwargs['default'] = os.environ[environment_name]

        parser.add_argument(f"--{name.replace('_', '-')}"
            , **kwargs
            )

    add_argument("src")
    add_argument("adjustments", type=argparse.FileType('r'))
    add_argument("output_folder")

    return parser

def main(argv=None):
    setup_logging()

    parser = make_parser()
    args = parser.parse_args(argv)

    if not os.path.exists(args.src):
        raise Exception("Couldn't find the source yaml file, did you `git submodule update --init` ?")

    with open(args.src) as fle:
        src = YAML(typ='safe').load(fle)
    adjustments = YAML(typ='safe').load(args.adjustments)

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    try:
        generate(src, adjustments, args.output_folder)
    except DelfickError as error:
        print("")
        print("!" * 20)
        sys.exit(str(error))
