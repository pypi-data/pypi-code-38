'''
usage:
  bf append [options] <destination> <file>...

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

from docopt import docopt

from blackfynn.models import DataPackage


def main(bf):
    args = docopt(__doc__)

    files = args['<file>']
    destination  = args['<destination>']

    try:
        package = bf.get(destination)

        if not isinstance(package, DataPackage):
            raise Exception("Only data packages may be appended to.")

        bf._api.io.upload_files(package, files, append=True, display_progress=True)
    except Exception as e:
        exit(e)
