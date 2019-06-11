import argparse
import logging

import errno
import pkg_resources
import sys

from bgreference import refseq

__version__ = pkg_resources.require("bgreference")[0].version
logger = logging.getLogger(__name__)


def cmdline():

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', dest='build', default='hg19', help='Genome build')
    parser.add_argument('-s', '--sequence', dest='sequence', required=True, help='Genomic sequence (chromosome)')
    parser.add_argument('-p', '--position', type=int, dest='position', help='Start position (included)')
    parser.add_argument('-l', '--length', type=int, dest='size', default=1, help='Total bases to retrive')
    parser.add_argument('-d', '--debug', dest='debug', default=False, action='store_true', help="Debug mode")
    parser.add_argument('-v', '--version', action='version', version="BgReference version {}".format(__version__))
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG if args.debug else logging.INFO)
    logger.debug(args)

    try:
        print(refseq(args.build, args.sequence, args.position, args.size))
    except RuntimeError as e:
        logging.error(e)
        sys.exit(errno.ENOENT)

if __name__ == "__main__":
    cmdline()
