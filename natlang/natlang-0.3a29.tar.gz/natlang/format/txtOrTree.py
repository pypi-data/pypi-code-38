# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Text and Tree loader
# Simon Fraser University
# Jetic Gu
#
#
from __future__ import absolute_import
import os
import sys
import inspect
import unittest
try:
    from tree import load as loadTree
    from txt import load as loadTxt
except ImportError:
    from natlang.format.tree import load as loadTree
    from natlang.format.txt import load as loadTxt
__version__ = "0.3a"


def load(file, linesToLoad=sys.maxsize, verbose=True):
    try:
        contents = loadTree(file, linesToLoad, verbose=verbose)
        contentsTxt = loadTxt(file, linesToLoad)
        if len([f for f in contents if f is not None]) <\
                (len(contentsTxt) / 2):
            return contentsTxt
    except AttributeError:
        return loadTxt(file, linesToLoad)
    return contents


class TestTxtOrTree(unittest.TestCase):
    def testLoadTreeFromFile(self):
        from natlang.format.tree import constructTree, constructTreeFromStr

        def compare(x, y):
            if x is None and y is None:
                return
            anc, fra, val, child, sibl = x.columnFormat()
            ancG, fraG, valG, childG, siblG = y.columnFormat()
            self.assertSequenceEqual(anc, ancG)
            self.assertSequenceEqual(fra, fraG)
            self.assertSequenceEqual(val, valG)
            return

        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        content = load(parentdir + "/test/sampleTree.txt", verbose=False)
        gContent = loadTree(parentdir + "/test/sampleTree.txt", verbose=False)
        for x, y in zip(content, gContent):
            compare(x, y)
        return

    def testLoadTxtFromFile(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        content = load(parentdir + "/test/sampleDepTree.txt", verbose=False)
        gContent = loadTxt(parentdir + "/test/sampleDepTree.txt")
        for x, y in zip(content, gContent):
            self.assertSequenceEqual(x, y)
        return


if __name__ == '__main__':
    if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        unittest.main()
