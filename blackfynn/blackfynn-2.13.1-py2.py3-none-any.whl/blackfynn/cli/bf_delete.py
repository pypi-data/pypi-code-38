'''
usage:
  bf delete [options] <item>

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from blackfynn import Collection, DataPackage

from .cli_utils import get_item


def main(bf):
    args = docopt(__doc__)

    try:
        item = get_item(args['<item>'], bf)

        if not (isinstance(item, Collection) or isinstance(item, DataPackage)):
            raise Exception("only data packages and collections may be deleted.")

        bf.delete(item)
    except Exception as e:
        exit("  failed to delete {}: {}".format(args['<item>'], e))
