'''
usage:
  bf create [options] <name> [<destination>]

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from blackfynn import Collection

from .cli_utils import get_item
from .working_dataset import require_working_dataset


def main(bf):
    args = docopt(__doc__)

    collection = Collection(args['<name>'])

    if args['<destination>']:
        parent = get_item(args['<destination>'], bf)
        resp = parent.add(collection)
    else:
        dataset = require_working_dataset(bf)
        resp = dataset.add(collection)

    print(collection)
