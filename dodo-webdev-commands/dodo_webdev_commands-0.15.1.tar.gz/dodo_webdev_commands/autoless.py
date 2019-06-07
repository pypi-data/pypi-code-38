from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser()
    parser.add_argument('autoless_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.autoless = Dodo.get_config("/LESS/autoless", "autoless")
    args.output_dir = Dodo.get_config("/LESS/output_dir")
    args.cwd = Dodo.get_config("/LESS/src_dir")
    return args


if Dodo.is_main(__name__):
    args = _args()

    Dodo.run(["mkdir", "-p", args.output_dir])

    Dodo.run(
        [args.autoless, ".", args.output_dir] + remove_trailing_dashes(
            args.autoless_args),
        cwd=args.cwd)
