# -*- coding: utf-8 -*-
# Python version: 2/3
#
# AMR/Propbank/Nombank Frame loader
# Simon Fraser University
# Jetic Gu
#
#
from __future__ import absolute_import
import os
import sys
import unittest
import glob
from xml.dom import minidom
__version__ = "0.3a"


def load(filename, linesToLoad=sys.maxsize):
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
            "loader.loadSemFrameXML [WARN]: linesToLoad option ignored\n")

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


def load(filename, linesToLoad=sys.maxsize):
    content = []
    if filename[-4:] == ".xml":
        content += loadSemFrameXML(filename, linesToLoad=linesToLoad)
    else:
        content += loadAMRFrame(filename, linesToLoad=linesToLoad)
    return content
