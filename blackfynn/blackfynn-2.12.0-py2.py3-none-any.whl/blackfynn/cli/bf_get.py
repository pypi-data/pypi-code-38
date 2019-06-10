'''Describe a package or collection

usage:
  bf get [options] [--tree] [<item>]

options:
  --tree                    Recursively print the item's contents

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from .cli_utils import get_item
from .working_dataset import require_working_dataset


def display(item, print_tree):
    if print_tree:
        item.print_tree()

    else:
        print("  {}".format(item))

        if hasattr(item, 'items') and item.items:
            print("  [contents]")
            for i in item.items:
                print("     {}".format(i))

        if hasattr(item, 'channels') and item.channels:
            print("  [channels]")
            for ch in item.channels:
                print("     {} (id: {})".format(ch.name, ch.id))

def main(bf):
    args = docopt(__doc__)

    if args['<item>']:
        item = get_item(args['<item>'], bf)
    else:
        item = require_working_dataset(bf)

    display(item, args['--tree'])
