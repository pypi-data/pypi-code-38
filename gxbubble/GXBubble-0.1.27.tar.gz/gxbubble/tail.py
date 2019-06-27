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
import sys
import time
import _thread


class Tail(object):
    __file = None
    __size = 0
    __timestamp = None
    __pos = 0
    __func = None

    def __init__(self, file):
        self.__file = file
        self.__func = sys.stdout.write

        if os.path.exists(self.__file):
            self.__size = os.path.getsize(self.__file)
            self.__timestamp = os.path.getmtime(self.__file)
            with open(self.__file) as f:
                f.seek(0, 2)
                self.__pos = f.tell()

    def set_callback(self, func):
        self.__func = func
        return self

    def follow(self, interval=1):
        _thread.start_new_thread(self.__tail, (interval,))

    def __tail(self, interval=1):
        while True:
            if self.__has_modified():
                with open(self.__file) as f:
                    f.seek(0, 2)
                    self.__pos = min(self.__pos, f.tell())
                    f.seek(self.__pos)
                    while True:
                        self.__pos = f.tell()
                        line = f.readline()
                        if not line:
                            break
                        else:
                            self.__func(line)

                    f.close()
            else:
                time.sleep(interval)

    def __has_modified(self):
        if not os.path.exists(self.__file):
            return False

        return self.__size != os.path.getsize(self.__file) or self.__timestamp != os.path.getmtime(self.__file)

