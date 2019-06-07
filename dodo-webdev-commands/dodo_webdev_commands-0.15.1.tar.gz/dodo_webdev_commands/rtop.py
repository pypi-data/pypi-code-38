import os
from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    args.rtop = os.path.join(
        Dodo.get_config('/SERVER/node_modules_dir'), '.bin', 'rtop')
    args.cwd = Dodo.get_config('/WEBPACK/webpack_dir')
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run([args.rtop], cwd=args.cwd)
