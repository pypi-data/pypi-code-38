#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sphinx.ext import intersphinx

import click

from . import bdt

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Dumps objects documented in python 3.x:

     $ bdt dumpsphinx https://docs.python.org/3/objects.inv


  2. Dumps objects documented in numpy:

     $ bdt dumpsphinx https://docs.scipy.org/doc/numpy/objects.inv


  3. Dumps objects documented in matplotlib:

     $ bdt dumpsphinx http://matplotlib.org/objects.inv
''')
@click.argument('url')
@verbosity_option()
@bdt.raise_on_error
def dumpsphinx(url):
  """Dumps all the objects given an sphinx catalog/inventory URL

  This command is useful when you are struggling to do proper links from your
  documentation.
  """
  intersphinx.inspect_main([url])
