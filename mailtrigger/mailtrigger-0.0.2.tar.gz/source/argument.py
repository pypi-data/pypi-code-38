# -*- coding: utf-8 -*-

import argparse

from .trigger.trigger import Trigger
from .version import VERSION


class Argument(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='mailtrigger',
                                               formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self._add_arguments()

    def _add_arguments(self):
        t = Trigger()
        triggers = ','.join(t.get_list())
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
