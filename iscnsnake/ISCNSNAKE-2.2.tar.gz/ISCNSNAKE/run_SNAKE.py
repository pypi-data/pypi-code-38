#!usr/bin/env python

"""
Quick Start script for ISCNParser
"""
import ISCNSNAKE.ISCNParser as ISCN
import sys

if len(sys.argv) > 1:
    input = sys.argv[1]
else:
    input = 'None selected'

ISCN.parse_file(input)

