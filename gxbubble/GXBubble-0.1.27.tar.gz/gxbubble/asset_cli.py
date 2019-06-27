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
# from tail import Tail
# import sh


def _print(txt):
    """print line without /r, /n or white space"""
    print(txt.rstrip())


def _is_windows():
    """check if the system is Windows"""
    return 'Windows' in platform.system()


class AssetCli:
    """Asset Help class"""
    __path = ''
    __assetDir = ''

    def __init__(self):
        self.__assetDir = os.getenv("ASSET_CONSOLE", None)
        if self.__assetDir is None:
            if _is_windows():
                self.__path = "D:/AssetExpressConsole/AssetExpressCli"
            else:
                self.__path = "/Tools/AssetExpressConsole/AssetExpressCli"
        else:
            self.__path = os.path.join(self.__assetDir + "/AssetExpressCli")
        if _is_windows():
            self.__path += ".cmd"

    def valid(self):
        return self.__path is not None

    def run(self, **options):
        if not self.valid():
            raise FileNotFoundError('Cannot find AssetExpressCli!')

        parameters = ' '
        for k, v in options.items():
            k = k.replace("_","-")
            if v in (True, False):
                if v :
                    parameters += (' --' + k)
                else:
                    parameters += ' '
            else:
                parameters += (' --' + k + ' ' + str(v))
        #: Execute AssetExpressCli command
        os.system(self.__path + parameters)


