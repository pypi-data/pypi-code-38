'''
usage:
  bf [options] ( organizations | orgs )

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

import sys

from docopt import docopt


def main(bf):
    args = docopt(__doc__)

    for o in bf.organizations():
        print("  {} (id: {})".format(o.name, o.id))
