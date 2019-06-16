# -*- coding: utf-8 -*-

import argparse

from .version import VERSION


class Argument(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='',
                                               formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self._add()

    def _add(self):
        self._parser.add_argument('-d', '--debug',
                                  action='store_true',
                                  dest='debug',
                                  help='debug mode')
        self._parser.add_argument('-m', '--mailer-config',
                                  dest='mailer_config',
                                  help='mailer configuration',
                                  required=True)
        self._parser.add_argument('-s', '--scheduler-config',
                                  dest='scheduler_config',
                                  help='scheduler configuration',
                                  required=True)
        self._parser.add_argument('-t', '--trigger-config',
                                  dest='trigger_config',
                                  help='trigger configuration',
                                  required=True)
        self._parser.add_argument('-v', '--version',
                                  action='version',
                                  version=VERSION)

    def parse(self):
        return self._parser.parse_args()
