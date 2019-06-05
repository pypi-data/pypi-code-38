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
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import argparse
import logging
import sys

from comet_ml.offline import main_upload

LOGGER = logging.getLogger("comet_ml")


def main():
    # Called via `comet-upload EXP.zip`
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "archives", nargs="+", help="the offline experiment archives to upload"
    )
    parser.add_argument(
        "--force-reupload",
        help="force reupload offline experiments that were already uploaded",
        action="store_const",
        const=True,
        default=False,
    )

    parsed_args = parser.parse_args(sys.argv[1:])

    main_upload(parsed_args.archives, parsed_args.force_reupload)


if __name__ == "__main__":
    # Called via `python -m comet_ml.scripts.comet_upload EXP.zip`
    main()
