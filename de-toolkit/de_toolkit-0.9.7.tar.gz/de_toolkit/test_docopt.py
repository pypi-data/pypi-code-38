#!/usr/bin/env python3
'''
Usage: test_docopt.py [options]

Options:
    -h      helpful helping of helpy help
    -v      verbose, pass multiple times for more verbose
'''

from docopt import docopt

if __name__ == '__main__' :
    
    opts = docopt(__doc__)

    print(opts)
