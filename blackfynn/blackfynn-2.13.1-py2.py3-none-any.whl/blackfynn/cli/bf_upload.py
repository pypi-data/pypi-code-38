'''
usage:
  bf upload [options] [--to=destination] <file>...

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

import os

from docopt import docopt

from .cli_utils import recursively_upload
from .working_dataset import require_working_dataset


def main(bf):
    args = docopt(__doc__)

    files = args['<file>']

    if args['--to']:
        collection = bf.get(args['--to'])
        recursively_upload(bf, collection, files)

    else:
        dataset = require_working_dataset(bf)
        recursively_upload(bf, dataset, files)
