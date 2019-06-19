#!/usr/bin/env python

import os

import click

from . import bdt

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Update the root certificate authority bundle on the distribution:

     $ bdt caupdate -v
     $ git status  #to check if bundle changed
     $ git commit -m '[data] Update CA bundle'  #if need be

''')
@verbosity_option()
@bdt.raise_on_error
def caupdate():
    """Updates the root certificate authority bundle on the distribution

    This script will download the latest CA bundle from curl at
    https://curl.haxx.se/ca/cacert.pem and will append Idiap's Root CA to the
    bundle, so we can use https://gitlab.idiap.ch transparently.
    """

    import requests
    from ..constants import CACERT, CACERT_URL, IDIAP_ROOT_CA

    logger.info('Retrieving %s...', CACERT_URL)
    r = requests.get(CACERT_URL, allow_redirects=True)

    logger.info('Writing %s...', CACERT)
    with open(CACERT, 'wb') as f:
      f.write(r.content)
      f.write(IDIAP_ROOT_CA)

    logger.warn('CA bundle is updated')
    logger.warn('Run git status, commit and push (if need be)')
