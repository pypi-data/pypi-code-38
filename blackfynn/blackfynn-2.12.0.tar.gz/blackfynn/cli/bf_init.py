'''
usage:
  bf [options] init <name>

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

import sys

from docopt import docopt

from .cli_utils import print_datasets
from .working_dataset import set_working_dataset


def main(bf):
    args = docopt(__doc__)

    name = args['<name>']
    dataset = bf.create_dataset(name)

    set_working_dataset(dataset)

    print_datasets(bf)
