#!/usr/bin/env python3
#
# Copyright(C) 2019 wuyaoping
#

import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pippurge.cli import main

if __name__ == '__main__':
    main()
