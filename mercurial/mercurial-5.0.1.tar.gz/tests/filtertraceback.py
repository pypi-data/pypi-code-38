#!/usr/bin/env python

# Filters traceback lines from stdin.

from __future__ import absolute_import, print_function

import sys

state = 'none'

for line in sys.stdin:
    if state == 'none':
        if line.startswith('Traceback '):
            state = 'tb'

    elif state == 'tb':
        if line.startswith('  File '):
            state = 'file'
            continue

        elif not line.startswith(' '):
            state = 'none'

    elif state == 'file':
        # Ignore lines after "  File "
        state = 'tb'
        continue

    print(line, end='')
