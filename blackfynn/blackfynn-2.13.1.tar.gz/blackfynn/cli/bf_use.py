'''
usage:
  bf use [options] <dataset>

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from .working_dataset import set_working_dataset


def main(bf):
    args = docopt(__doc__)

    dataset_id_or_name = args['<dataset>']

    try:
        dataset = bf.get_dataset(dataset_id_or_name)
        set_working_dataset(dataset)
    except Exception as e:
        exit(e)
