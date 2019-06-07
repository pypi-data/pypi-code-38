from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser()
    parser.add_argument('script')
    parser.add_argument('script_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.python = Dodo.get_config('/PYTHON/python')
    args.cwd = Dodo.get_config('/PYTHON/src_dir')
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        [
            args.python,
            args.script,
        ] + remove_trailing_dashes(args.script_args),
        cwd=args.cwd)
