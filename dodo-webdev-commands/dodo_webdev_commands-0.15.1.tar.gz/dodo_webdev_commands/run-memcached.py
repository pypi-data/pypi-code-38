from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(["memcached", "-u", "memcache", "-vvv"], cwd="/")
