#!/usr/bin/env python
import sys, os
argv = sys.argv
if argv[0] == __file__:
    argv = sys.argv[1:]
file = argv[0].split('/')[-1]
args = ' '.join(argv[1:])
os.system("%s.py %s" % (file, args))
