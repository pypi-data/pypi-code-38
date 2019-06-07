from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    args.ngrok = Dodo.get_config('/NGROK/ngrok')
    args.port = Dodo.get_config('/NGROK/port')
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run([
        args.ngrok,
        'http',
        str(args.port),
    ])
