#!/usr/bin/env python
"""The main entry point. Invoke as `collabi` (when installed) or
`python -m collabi' (from a clone of the source).
"""
from sys import exit
from collabi.cli import main

if __name__ == '__main__':
    exit(main())
