# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# Revised BSD License, included in this distribution as LICENSE

"""
Show path to include.mk for building packages with makefiles.
"""

from metapack.package import Downloader
from pathlib import Path
import argparse

downloader = Downloader.get_instance()


def mk_args(subparsers):
    """
    Show path to include.mk for building packages with makefiles.

    The include.mk can be included in a makefile with:

        include $(shell mp mk)

    Define ``PACKAGE_NAMES`` with the names of the source package directories.
    Run ``make list`` to list all targets. Useful targets are:

      build: Build filesystem and ZIP packages
      s3: publish to s3
      ckan: Publish to CKAN
      wp: Publish to workdpress

    The ``s3``, ``ckan`` and ``wp`` targets require the ``metapack-wp``
    module to be installed.

    For publishing to s3, define `S3_BUCKET` with the name of an S3 bucket

    For publishing to CKAN, define `GROUP` and `TAG` with a comma separated
    list of gorups or tags.

    For publishing to wordpress, define `GROUP` and `TAG` with a comma
    separated list of gorups or tags, and ``WP_SITE`` with the name
    of the wordpress site credentials in the ``~/.metapack.yaml`` file




    """
    parser = subparsers.add_parser(
        'mk',
        help='Show path to include.mk for building packages with makefiles. ',
        description=mk_args.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.set_defaults(run_command=mk_cmd)


def mk_cmd(args):
    import metapack_build.support as support

    print(Path(support.__file__).parent.joinpath('include.mk'))
