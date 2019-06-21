# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Text loader
# Simon Fraser University
# Jetic Gu
#
#
from __future__ import absolute_import
import io
import os
import sys
__version__ = "0.3a"


def load(file, linesToLoad=sys.maxsize):
    with io.open(os.path.expanduser(file), encoding='utf-8') as f:
        content = [line.lower().strip().split() for line in f][:linesToLoad]
    return content
