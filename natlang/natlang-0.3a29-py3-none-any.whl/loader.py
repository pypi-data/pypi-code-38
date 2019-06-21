# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Dataset loader for NLP experiments.
# Simon Fraser University
# Jetic Gu
#
#
from __future__ import absolute_import
import os
import sys
import inspect
import unittest
import glob
import six
import ast
import importlib

from natlang.format import *

__version__ = "0.3a"

supportedList = {
    "tree": tree,
    "txtFiles": txtFiles,
    "txt": txt,
    "AMR": AMR,
    "txtOrTree": txtOrTree,
    "pyCode": pyCode,
    "conll": conll,
    "semanticFrame": semanticFrame,
    "astTree": astTree,
    'django': django,
    'intent': intent,
    'intentJSON': intentJSON,
    'pyCodeJSON': pyCodeJSON,
    'bashJSON': bashJSON,
    'bashIntent': bashIntent,
    'bashAst': bashAst,
    'alignment': alignment
}


def processOption(option, errorMessage="invalid option"):
    if isinstance(option, str):
        if '{' in option and '}' in option:
            option = ast.literal_eval(option)
        else:
            option = option.split('=')
            if len(option) == 1:
                option = {option[0]: True}
            elif len(option) == 2:
                option = dict([option])
            else:
                raise ValueError(errorMessage)
    if option is None:
        option = {}
    if not isinstance(option, dict):
        raise ValueError(errorMessage)
    return option


class DataLoader():
    def __init__(self, format="txtOrTree", loader=None):
        if loader is not None:
            if hasattr(loader, '__call__'):
                self.loader = loader
                return
            else:
                raise TypeError(
                    "natlang.dataLoader: invalid loader selection,",
                    "selected loader does not have __call__ attr")
        # Added unicode for python2 compatibility
        if isinstance(format, six.string_types):
            if format not in supportedList:
                raise ValueError(
                    "natlang.dataLoader: invalid format selection")
            else:
                self.loader = supportedList[format].load
        else:
            if hasattr(format, 'load') and hasattr(format.load, '__call__'):
                self.loader = format.load
            else:
                raise ValueError(
                    "natlang.dataLoader: custom format selected does not",
                    "have a callable load attr")
        return

    def __call__(self,
                 file, linesToLoad=sys.maxsize, verbose=True, option=None):
        return self.load(file,
                         linesToLoad=linesToLoad,
                         verbose=verbose,
                         option=option)

    def load(self, file, linesToLoad=sys.maxsize, verbose=True, option=None):
        def matchPattern(pattern):
            pattern = os.path.expandvars(os.path.expanduser(pattern))
            return [filename
                    for filename in glob.glob(pattern)
                    if os.path.isfile(filename)]

        option = processOption(
            option, errorMessage="natlang.dataLoader.load: invalid option")

        content = []
        if isinstance(file, list):
            files = []
            for filePattern in file:
                files += matchPattern(filePattern)
        elif isinstance(file, six.string_types):
            files = matchPattern(file)
        else:
            raise RuntimeError("natlang.dataLoader.load [ERROR]: parameter " +
                               "type")

        if len(files) == 0:
            raise RuntimeError(
                "natlang.dataLoader.load [ERROR]: Cannot find matching files")

        if sys.version_info[0] < 3:
            getSpec = inspect.getargspec
        else:
            getSpec = inspect.getfullargspec

        if "verbose" in getSpec(self.loader)[0]:
            if "option" in getSpec(self.loader)[0]:
                def load(fileName):
                    return self.loader(filename, linesToLoad=linesToLoad,
                                       verbose=verbose, option=option)
            else:
                def load(fileName):
                    return self.loader(filename, linesToLoad=linesToLoad,
                                       verbose=verbose)
        else:
            if "option" in getSpec(self.loader)[0]:
                def load(fileName):
                    return self.loader(filename, linesToLoad=linesToLoad,
                                       option=option)
            else:
                def load(fileName):
                    return self.loader(filename, linesToLoad=linesToLoad)

        for filename in files:
            content += load(filename)
        return content


class ParallelDataLoader():
    def __init__(self,
                 srcFormat="txtOrTree",
                 tgtFormat="txtOrTree",
                 srcLoader=None,
                 tgtLoader=None):
        self.srcLoader = DataLoader(srcFormat, srcLoader)
        self.tgtLoader = DataLoader(tgtFormat, tgtLoader)
        return

    def __call__(self,
                 fFile, eFile,
                 linesToLoad=sys.maxsize, verbose=True, option=None):
        return self.load(fFile, eFile,
                         linesToLoad=linesToLoad,
                         verbose=verbose,
                         option=option)

    def load(self, fFile, eFile,
             linesToLoad=sys.maxsize, verbose=True, option=None):
        data = zip(self.srcLoader.load(fFile, linesToLoad,
                                       verbose=verbose, option=option),
                   self.tgtLoader.load(eFile, linesToLoad,
                                       verbose=verbose, option=option))
        # Remove incomplete or invalid entries
        data = [(f, e) for f, e in data if f is not None and e is not None]
        data = [(f, e) for f, e in data if len(f) > 0 and len(e) > 0]
        return data


class TestPatternMatching(unittest.TestCase):
    def testProcessOption(self):
        self.assertDictEqual(supportedList, processOption(supportedList, ""))
        testDict = {'a': '1', 'b': '2', 'c': '3'}
        self.assertDictEqual(testDict, processOption(str(testDict), ""))
        testDict = {'cheese': True}
        self.assertDictEqual(testDict, processOption('cheese', ""))
        testDict = {'cheese': '2'}
        self.assertDictEqual(testDict, processOption('cheese=2', ""))
        return

    def testLoaderOption(self):
        def load(fileName, linesToLoad=0, option={}):
            return [option]

        loader = DataLoader(loader=load)
        testDict = {'a': '1', 'b': '2', 'c': '3'}
        self.assertDictEqual(testDict,
                             loader.load("/*", option=str(testDict))[0])
        testDict = {'cheese': True}
        self.assertDictEqual(testDict,
                             loader.load("/*", option='cheese')[0])
        testDict = {'cheese': '2'}
        self.assertDictEqual(testDict,
                             loader.load("/*", option='cheese=2')[0])
        return


if __name__ == '__main__':
    if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        unittest.main()
