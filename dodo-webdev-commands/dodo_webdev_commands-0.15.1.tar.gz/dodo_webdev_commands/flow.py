import argparse
from dodo_commands.framework import Dodo

# from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = argparse.ArgumentParser()
    parser.add_argument('yarn_args', nargs=argparse.REMAINDER)
    parser.add_argument('--name')
    args = Dodo.parse_args(parser)
    args.yarn = 'yarn'
    args.cwd = Dodo.get_config('/WEBPACK/webpack_dir')
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.name:
        Dodo.get_config('/DOCKER') \
            .setdefault('options', {}) \
            .setdefault('yarn', {})['name'] = args.name

    Dodo.run([args.yarn, 'run', 'flow-watch'], cwd=args.cwd)
