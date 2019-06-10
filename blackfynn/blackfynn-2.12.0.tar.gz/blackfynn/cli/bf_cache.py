'''
usage:
  bf cache [options] clear
  bf cache [options] compact

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from blackfynn.cache import get_cache


def main(bf):
    args = docopt(__doc__)

    cache = get_cache(bf.settings, init=False)

    if args['clear']:
        print("Clearing cache...")
        cache.clear()
        print("Cache cleared.")
    elif args['compact']:
        print('Compacting cache...')
        cache.start_compaction(background=False)
        print('Cache compaction done.')
