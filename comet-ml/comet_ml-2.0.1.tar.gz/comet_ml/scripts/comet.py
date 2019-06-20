#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

import sys

from .comet_optimize import main as optimize
from .comet_upload import main as upload


def usage():
    print(
        """comet COMMAND [OPTIONS]

where COMMAND is `upload` or `optimize`.

Examples:

    comet upload file.zip ...
    comet upload --force-reupload file.zip ...

    comet optimize script.py optimize.config
    comet optimize -j 4 script.py optimize.config
    comet optimize -j 4 script.py optimize.config -- arg1 --flag arg2

Note that `comet optimize` requires your COMET_API_KEY
be configured in the environment, or in your .comet.config
file. For example:

    COMET_API_KEY=74345364546 comet optimize ...

For more information:
    comet COMMAND --help
"""
    )


def main(args=sys.argv[1:]):
    if len(args) < 2:
        usage()
    elif args[0] == "upload":
        upload(args[1:])
    elif args[0] == "optimize":
        optimize(args[1:])
    else:
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])
