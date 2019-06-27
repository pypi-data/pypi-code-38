# -*- coding: utf-8 -*-
#
# This file is part of ProjectBubble.
#
# (c) Giant - MouGuangyi <mouguangyi@ztgame.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import os
import platform
from gxbubble.tail import Tail
from gxbubble import (
    shell
)


def _print(txt):
    """print line without /r, /n or white space"""
    print(txt.rstrip())


def _is_windows():
    """check if the system is Windows"""
    return 'Windows' in platform.system()


class Unity:
    """Unity Help class"""
    __path = ''

    def __init__(self, unity_path):
        self.__path = os.getenv(unity_path, None)

    def valid(self):
        return self.__path is not None

    def run(self, **options):
        if not self.valid():
            raise FileNotFoundError('CANNOT find Unity!')

        parameters = ' '
        for k, v in options.items():
            if v in (True, False):
                if v :
                    parameters += (' -' + k)
                else:
                    parameters += ' '
            else:
                parameters += (' -' + k + ' ' + v)

        # new thread to tail log file
        log_path = self.__get_log_path(options.get('logFile', None))
        Tail(log_path).set_callback(_print).follow()

        #: Execute unity command
        return shell(self.__path + parameters)

    def __get_log_path(self, log_path):
        if log_path is not None:
            return log_path

        if _is_windows():
            return os.path.join(os.getenv('LOCALAPPDATA'), 'Unity/Editor/Editor.log')
        else:
            return os.path.join(os.getenv('HOME'), 'Library/Logs/Unity/Editor.log')


