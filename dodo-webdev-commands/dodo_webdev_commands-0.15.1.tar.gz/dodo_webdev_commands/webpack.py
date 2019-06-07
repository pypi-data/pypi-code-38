"""Run the webpack command."""
from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser()
    parser.add_argument('--watch', action="store_true")
    parser.add_argument('webpack_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.webpack = Dodo.get_config("/WEBPACK/webpack", "webpack")
    args.cwd = Dodo.get_config("/WEBPACK/webpack_dir")
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        [args.webpack] + (["--watch-stdin"] if args.watch else []) +
        remove_trailing_dashes(args.webpack_args or []),
        cwd=args.cwd)
