#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""
"""

from loguru import logger
import argparse


from PyQt5 import QtGui
import sys

import collections
import numpy as np

from pyqtgraph.parametertree import ParameterTree
import pyqtgraph.parametertree.parameterTypes as pTypes


class BatchFileProcessingParameter(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add"
        {'name': 'Save State', 'type': 'action'},
        # opts['addList'] = ['str', 'float', 'int']
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self):
        # val = {
        #     'str': '',
        #     'float': 0.0,
        #     'int': 0
        # }[typ]
        fname = QtGui.QFileDialog.getOpenFileName(None, 'Open file', '')
        self.add_filename(fname=fname)

    def add_filename(self, fname):
        self.addChild(
            dict(name="%i" % ((len(self.childs))), type='str', value=str(fname), removable=True, renamable=True))