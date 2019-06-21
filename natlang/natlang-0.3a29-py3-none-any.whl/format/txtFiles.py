# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Txt file format loader
# Simon Fraser University
# Jetic Gu
#
#
from __future__ import absolute_import
import os
import sys
import inspect
import unittest
__version__ = "0.3a"


def load(files, linesToLoad=sys.maxsize):
    '''
    This function is used to read a set of files with different information
    (e.g. POS, Form, etc.) on the same set of tokens.

    @param files: list of str, the files include FORM, POS, etc.,
    @param* linesToLoad: int, the lines to read
    @return: list of sentences. Each sentence is a list of tuples with POS,
        FORM, etc.
    '''
    content =\
        [list(zip(*[content.strip().split() for content in contents]))
         for contents in list(zip(*[open(os.path.expanduser(f))
                                    for f in files]))[:linesToLoad]]
    return content
