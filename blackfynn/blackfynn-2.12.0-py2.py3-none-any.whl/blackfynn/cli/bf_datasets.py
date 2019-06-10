'''
usage:
  bf [options] ( datasets | ds )

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

import sys

from docopt import docopt

from .cli_utils import print_datasets


def main(bf):
    args = docopt(__doc__)

    print_datasets(bf)
