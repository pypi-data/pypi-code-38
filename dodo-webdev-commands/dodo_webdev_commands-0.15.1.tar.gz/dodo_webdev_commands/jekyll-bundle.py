from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo, ConfigArg
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser()
    parser.add_argument('jekyll_args', nargs=REMAINDER)
    args = Dodo.parse_args(
        parser, config_args=[ConfigArg('/ROOT/src_dir', 'src_dir')])
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run(
        ['bundle', 'exec', 'jekyll', 'serve'] + remove_trailing_dashes(
            args.jekyll_args or []),
        cwd=args.src_dir)
