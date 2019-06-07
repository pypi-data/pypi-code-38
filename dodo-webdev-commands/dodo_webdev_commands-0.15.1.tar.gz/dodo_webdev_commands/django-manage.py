import argparse
from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser(description='Run a django-manage command.')
    parser.add_argument('--name', )
    parser.add_argument('manage_args', nargs=argparse.REMAINDER)
    args = Dodo.parse_args(parser)
    args.python = Dodo.get_config("/DJANGO/python")
    args.cwd = Dodo.get_config("/DJANGO/src_dir")
    return args


if Dodo.is_main(__name__):
    args = _args()
    if args.name:
        Dodo.get_config('/DOCKER') \
            .setdefault('options', {}) \
            .setdefault('django-manage', {}) \
            .setdefault('name', args.name)

    Dodo.run(
        [
            args.python,
            "manage.py",
        ] + remove_trailing_dashes(args.manage_args),
        cwd=args.cwd)
