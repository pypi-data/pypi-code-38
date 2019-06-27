#!/usr/bin/env python3

import sys

from lad import convert

args = sys.argv
if len(args) == 1:
    print('usage: lad_convert <lad string>')
    exit(0)

string = args[1]

output = convert(string)
print(output)
