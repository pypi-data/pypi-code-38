from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser()
    parser.add_argument(
        '--playbook',
        default=Dodo.get_config("/ANSIBLE/default_playbook", None))
    parser.add_argument('server')
    parser.add_argument('ansible_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.cwd = Dodo.get_config("/ANSIBLE/src_dir")
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        ["ansible-playbook", "-i", "hosts", args.playbook, "-l", args.server] +
        remove_trailing_dashes(args.ansible_args),
        cwd=args.cwd)
