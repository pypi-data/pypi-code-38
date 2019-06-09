# -*- coding: utf-8 -*-

import colorama
import json
import os
import sys

CONFIG = '../config/config.json'


class Logger(object):
    def __init__(self):
        self._debug = self._load_config(os.path.join(os.path.dirname(__file__), CONFIG))

    def _load_config(self, name):
        with open(name, 'r') as f:
            data = json.load(f)
        return data.get('debug', False)

    def debug(self, msg):
        if self._debug is False:
            return
        sys.stderr.write(u'{debug}DEBUG:{reset} {msg}\n'.format(
            debug=colorama.Fore.GREEN + colorama.Style.BRIGHT,
            reset=colorama.Style.RESET_ALL,
            msg=msg))

    def error(self, msg):
        sys.stderr.write(u'{error}ERROR:{reset} {msg}\n'.format(
            error=colorama.Fore.RED + colorama.Style.BRIGHT,
            reset=colorama.Style.RESET_ALL,
            msg=msg))

    def info(self, msg):
        sys.stderr.write(u'{info}info:{reset} {msg}\n'.format(
            info=colorama.Fore.WHITE + colorama.Style.BRIGHT,
            reset=colorama.Style.RESET_ALL,
            msg=msg))

    def warn(self, msg):
        sys.stderr.write(u'{warn}WARN:{reset} {msg}\n'.format(
            warn=colorama.Fore.YELLOW + colorama.Style.BRIGHT,
            reset=colorama.Style.RESET_ALL,
            msg=msg))
