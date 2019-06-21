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


def processAlignmentEntry(entry, listToAddTo, splitChar='-',
                          reverse=False, loadType=True):
    if entry.find(splitChar) != -1:
        for ch in (',', '(', ')', '[', ']'):
            entry = entry.replace(ch, splitChar)
        items = [item for item in entry.split(splitChar) if item != '']
        # items = entry.split(splitChar)
        f = int(items[0])
        alignmentType = ""
        for i in range(len(items) - 1, 0, -1):
            if items[i].isdigit():
                e = int(items[i])
                if alignmentType != "" and loadType is True:
                    if reverse is True:
                        listToAddTo.append((e, f, alignmentType))
                    else:
                        listToAddTo.append((f, e, alignmentType))
                else:
                    if reverse is True:
                        listToAddTo.append((e, f))
                    else:
                        listToAddTo.append((f, e))
            else:
                alignmentType = items[i]
    return


def load(file, linesToLoad=sys.maxsize):
    alignment =\
        [sentence.strip().split() for sentence in
            list(open(os.path.expanduser(file)))[:linesToLoad]]

    for i in range(len(alignment)):
        entries = alignment[i]
        result = []
        for entry in entries:
            processAlignmentEntry(entry, result, reverse=False)
        alignment[i] = result

    return alignment
