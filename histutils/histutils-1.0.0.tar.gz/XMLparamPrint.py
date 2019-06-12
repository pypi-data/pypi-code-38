#!/usr/bin/env python
"""
demos reading HiST camera parameters from XML file
"""
from histutils.hstxmlparse import xmlparam
from argparse import ArgumentParser


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('fn', help='xml filename to parse')
    p = p.parse_args()

    params = xmlparam(p.fn)

    print(params)
