#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module to Convert an integer id to a filepath for storage system."""
from __future__ import print_function
import sys


def id2dirandfilename(fileid):
    """Algorithm for getting filepath from an integer id."""
    hexfileid = '{0:x}'.format(fileid)
    directories = ''
    while len(hexfileid) > 2:
        directories = '{0}/{1}'.format(directories, hexfileid[-2:])
        hexfileid = hexfileid[:-2]
    if directories == '':
        filename = 'file.{0}'.format(hexfileid)
        filepath = '/{0}'.format(filename)
        directories = '/'
    else:
        filename = '{0:x}'.format(fileid)
        filepath = '{0}/{1}'.format(directories, filename)
    return filepath


def id2filename(fileid):
    """Will return the filepath associated to passed fileid."""
    return id2dirandfilename(fileid)


if __name__ == '__main__':  # pragma: no cover
    print(id2filename(int(sys.argv[1])))
