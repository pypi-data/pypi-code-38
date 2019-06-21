# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Jetic's dataset loader for NLP experiments.
# Simon Fraser University
# Jetic Gu
#
#
import os
import sys
import inspect
import unittest
from natlang.format.tree import Node
from natlang.format.tree import load as loadPennTree
__version__ = "0.2a"
sys.stderr.write("Warning, use of fileIO is deprecated")


def _loadBitext(file1, file2, linesToLoad=sys.maxsize):
    '''
    This function is used to read a bitext from two text files.

    @param file1: str, the first file to read
    @param file2: str, the second file to read
    @param* linesToLoad: int, the lines to read
    @return: Bitext, detailed of this format:
        https://github.com/sfu-natlang/HMM-Aligner/wiki/API-reference:-Dataset-Data-Format-V0.1a#bitext
    '''
    path1 = os.path.expanduser(file1)
    path2 = os.path.expanduser(file2)
    bitext =\
        [[sentence.strip().split() for sentence in pair] for pair in
            list(zip(open(path1), open(path2)))[:linesToLoad]]
    return bitext


def loadDataset(fFiles, eFiles, linesToLoad=sys.maxsize,
                reverse=False):
    '''
    This function is used to read a Dataset files.

    @param fFiles: list of str, the file containing source language files,
        including FORM, POS, etc.,
    @param eFiles: list of str, the file containing target language files,
        including FORM, POS, etc.,
    @param alignmentFile: str, the alignmentFile
    @param* linesToLoad: int, the lines to read
    @return: Dataset, detail of this format:
        https://github.com/sfu-natlang/HMM-Aligner/wiki/API-reference:-Dataset-Data-Format-V0.2a#tritext
    '''
    fContents =\
        [list(zip(*[fContent.strip().split() for fContent in contents]))
         for contents in list(zip(*[open(os.path.expanduser(fFile))
                                    for fFile in fFiles]))[:linesToLoad]]
    eContents =\
        [list(zip(*[eContent.strip().split() for eContent in contents]))
         for contents in list(zip(*[open(os.path.expanduser(eFile))
                                    for eFile in eFiles]))[:linesToLoad]]

    return zip(fContents, eContents)


"""
AMR/PropBank/NomBank Semantic Frame loaders
"""


def loadSemFrame(filePattern, linesToLoad=sys.maxsize):
    content = []
    import glob
    if isinstance(filePattern, list):
        files = []
        for fileP in filePattern:
            files += [filename
                      for filename in glob.glob(os.path.expanduser(fileP))
                      if os.path.isfile(filename)]
    else:
        files = [filename
                 for filename in glob.glob(os.path.expanduser(filePattern))
                 if os.path.isfile(filename)]
    if len(files) == 0:
        if not isinstance(filePattern, list):
            sys.stderr.write(
                "fileIO.loadSemFrame [ERROR]: matching pattern" +
                filePattern + "\n")
        raise RuntimeError(
            "fileIO.loadSemFrame [ERROR]: Cannot find matching files")
    for filename in files:
        if filename[-4:] == ".xml":
            content += loadSemFrameXML(filename)
        else:
            content += loadAMRFrame(filename, linesToLoad=linesToLoad)
    return content


def loadAMRFrame(filename, linesToLoad=sys.maxsize):
    """
    Loader for AMR2.0 frames file: propbank-frame-arg-descr.txt
    """
    content = list(open(os.path.expanduser(filename)))[:linesToLoad]

    def splitEntry(line):
        raw = line.strip().split()
        result = [raw[0]]
        try:
            for i in range(1, len(raw)):
                if raw[i][:3] == "ARG" and raw[i][-1] == ":":
                    result.append([raw[i][:-1], ""])
                else:
                    if result[-1][1] == "":
                        result[-1][1] = raw[i]
                    else:
                        result[-1][1] += " " + raw[i]
            result =\
                (result[0], dict(result[1:]))
        except ValueError:
            sys.stderr.write("Original entry: " + str(raw) + "\n")
            sys.stderr.write("Entry Frame:    " + str(result[0]) + "\n")
            raise
        return result

    content = [splitEntry(entry) for entry in content]
    return content


def loadSemFrameXML(filename, linesToLoad=sys.maxsize):
    """
    Loader for CoNLL-2008 frames file: *.xml
    """
    content = []
    if linesToLoad != sys.maxsize:
        sys.stderr.write(
            "fileIO.loadAMRFrameXML [WARN]: linesToLoad option ignored\n")

    from xml.dom import minidom
    xmldoc = minidom.parse(os.path.expanduser(filename))
    items = xmldoc.getElementsByTagName('roleset')
    for item in items:
        frame = str(item.attributes['id'].value)
        args = {}
        roleList = item.getElementsByTagName('role')
        for role in roleList:
            args[str("ARG" + role.attributes['n'].value)] =\
                str(role.attributes['descr'].value)
        content.append((frame, args))
    return content


def loadTreeDataset(fFile, eFile, linesToLoad=sys.maxsize):
    try:
        fContents = loadPennTree(fFile, linesToLoad)
        if len([f for f in fContents if f is not None]) < (len(fContents) / 2):
            fContents =\
                [line.strip().split()
                 for line in open(os.path.expanduser(fFile))][:linesToLoad]
    except AttributeError:
        fContents =\
            [line.strip().split() for line in open(os.path.expanduser(fFile))][
                :linesToLoad]
    try:
        eContents = loadPennTree(eFile, linesToLoad)
        if len([e for e in eContents if e is not None]) < (len(eContents) / 2):
            eContents =\
                [line.strip().split()
                 for line in open(os.path.expanduser(eFile))][:linesToLoad]
    except AttributeError:
        eContents =\
            [line.strip().split() for line in open(os.path.expanduser(eFile))][
                :linesToLoad]
    dataset = zip(fContents, eContents)
    dataset = [(f, e) for f, e in dataset if f is not None and e is not None]
    dataset = [(f, e) for f, e in dataset if len(f) > 0 and len(e) > 0]

    return dataset


def exportToFile(result, fileName):
    try:
        outputFile = open(fileName, "w")
    except IOError:
        # In case of Keroberos failure.
        os.system("kinit")
        outputFile = open(fileName, "w")

    for sent in result:
        if isinstance(sent, Node):
            line = sent.export()
        else:
            line = " ".join(sent)
        outputFile.write(line + "\n")
    outputFile.close()
    return


class RealtimeExporter():
    """
    Use this class to export in real time.
    """
    def __init__(self, fileName):
        self.__outputFile = open(fileName, "w")
        return

    def write(self, sent):
        if isinstance(sent, Node):
            line = sent.export()
        else:
            line = " ".join(sent)
        self.__outputFile.write(line + "\n")
        self.__outputFile.flush()
        return

    def __del__(self):
        if self.__outputFile:
            self.__outputFile.close()
