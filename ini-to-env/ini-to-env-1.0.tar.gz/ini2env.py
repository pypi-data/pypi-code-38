__version__ = '1.0'

import os as _os
from configparser import (
    ConfigParser as _ConfigParser,
)


class Loader(object):
    def __init__(self):
        self.conf = _ConfigParser()
        self.conf.optionxform = str  # preserve case

    def add_files(self, *filenames):
        for filename in filenames:
            with open(filename):  # raise FileNotFoundError
                pass
        self.conf.read(filenames)

    def __iter__(self):
        for section in self.conf:
            yield from self.conf[section].items()

    def load(self, target=None):
        if target is None:
            target = _os.environ
        for k, v in self:
            target.setdefault(k, v)


def load(*filenames):
    loader = Loader()
    loader.add_files(*filenames)
    loader.load()


def cmd(args=None):
    import sys
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('file', nargs='+', type=str, help='ini file(s) to load')
    args = parser.parse_args(args=args)

    loader = Loader()
    loader.add_files(*args.file)

    if sys.stdout.isatty():
        print('# source this output to export environment variables', file=sys.stderr)
    for k, v in loader:
        print('export {}={}'.format(k, v))
