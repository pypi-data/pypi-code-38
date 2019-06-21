from __future__ import absolute_import
import unittest
import sys

from natlang import format
from natlang import analysis

from natlang import exporter
from natlang import fileConverter
from natlang import loader as loade

from natlang import __version__
__version__ = __version__.version

testModules = {
    analysis.conllTransformer,
    format.AMR,
    format.pyCode,
    format.semanticFrame,
    format.tree,
    format.txt,
    format.txtFiles,
    format.txtOrTree,
    format.conll,
    format.astTree,
    loader,
}


def testSuite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # add tests to the test suite
    for module in testModules:
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


name = "natlang"


# Functions
def load(filePattern,
         format='txtOrTree',
         loader=None,
         linesToLoad=sys.maxsize, verbose=True, option=None):
    _loader = loade.DataLoader(format, loader)
    return _loader(filePattern,
                   linesToLoad=linesToLoad,
                   verbose=verbose,
                   option=option)


def biload(srcFilePattern, tgtFilePattern,
           srcFormat='txtOrTree', tgtFormat='txtOrTree',
           srcLoader=None, tgtLoader=None,
           linesToLoad=sys.maxsize, verbose=True, option=None):
    lad = loader.ParallelDataLoader(srcFormat, tgtFormat)
    return lad(fFile=srcFilePattern,
               eFile=tgtFilePattern,
               linesToLoad=linesToLoad,
               verbose=verbose,
               option=option)


def export(content, fileName):
    f = exporter.RealtimeExporter(fileName)
    for line in content:
        f.write(line)
    return
