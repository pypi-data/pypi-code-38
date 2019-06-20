'''
usage:
  bf search [options] <term>...

search options:
  --show-paths

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from .cli_utils import print_path_tree


def main(bf):
    args = docopt(__doc__)

    terms = ' '.join(args['<term>'])
    results = bf._api.search.query(terms)
    if len(results) == 0:
        print("No Results.")
    else:
        if args['--show-paths']:
            print_path_tree(bf, results)
        else:
            for r in results:
                print(" * {}".format(r))
