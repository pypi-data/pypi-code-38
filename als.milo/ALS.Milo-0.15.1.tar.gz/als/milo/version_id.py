#!/usr/bin/env python

"""version_id.py

   Prints PEP440-compliant version identifier to standard output
"""

__author__ = "Padraic Shafer"
__copyright__ = "Copyright (c) 2018-2019, Padraic Shafer"
__credits__ = [__author__, ]
__license__ = ""
__maintainer__ = "Padraic Shafer"
__email__ = "PShafer@lbl.gov"
__status__ = "Development"

# Allow import of package siblings when module is run as script
import pkgscript
if (__name__ == "__main__") and (__package__ is None):
    pkgscript.import_parent_packages("als.milo", globals())

from als.milo import __version__, __date__

import argparse


def main():
    parser = argparse.ArgumentParser(
        # usage=__doc__,
        description=__doc__,
        # formatter_class=SmartFormatter,
        )
    parser.add_argument(
        "--version",
        action="version",
        # version="{} {}".format(__package__, __version__),
        version=__version__,
        help="Display PEP440 version identifier",
        )
    args = parser.parse_args()

    # Default: Print version identifier
    if args == argparse.Namespace():
        parser.parse_args(["--version"])


if __name__ == "__main__":
    main()
