# -*- coding: utf-8 -*-

import argparse

from .registry import REGISTRY
from .version import VERSION


class Argument(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='',
                                               formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self._add()

    def _add(self):
        triggers = ','.join([x['name'] for x in REGISTRY])
        self._parser.add_argument('-t', '--trigger',
                                  default=triggers,
                                  dest='trigger',
                                  help='set trigger, triggers: %s' % triggers,
                                  required=True)
        self._parser.add_argument('-v', '--version',
                                  action='version',
                                  version=VERSION)

    def parse(self):
        return self._parser.parse_args()
