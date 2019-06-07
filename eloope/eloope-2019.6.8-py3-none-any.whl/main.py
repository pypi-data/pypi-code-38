from .command import Command
import sys


def main():
    params = sys.argv[1:]
    cmd = params[0] if params else 'help'
    host = params[1] if len(params) > 1 else 'localhost'
    port = params[2]if len(params) > 2 else 6991

    return Command.execute(cmd, host=host, port=port)
