'''
Command-line user interface functions.
'''

import argparse

from angda import VERSION

parser = argparse.ArgumentParser(
    description  = 'Angda: A neat generic dice API.',
    epilog       = 'See angda.org for more information.',
    allow_abbrev = False,
)

parser.add_argument('rolls',
    nargs = '+',
    type  = str,
    help  = 'dice to roll (eg: d6, 2d5, 1d4+2)',
)

parser.add_argument('-d', '--details',
    action = 'store_true',
    help   = 'show detailed object output'
)

parser.add_argument('-q', '--quiet',
    action = 'store_true',
    help   = 'show integer result only',
)

parser.add_argument('-v', '--version',
    action  = 'version',
    version = VERSION,
    help    = 'show version and exit',
)

def parse(args=None):
    '''
    Return a dict of parsed command-line arguments.
    '''

    return vars(parser.parse_args(args=args))
