#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Commands the MNIST database can respond to.
"""

import os
import sys
import pkg_resources

from bob.db.base.driver import Interface as BaseInterface


class Interface(BaseInterface):


  def name(self):
    return 'mnist'


  def version(self):
    return pkg_resources.require('bob.db.%s' % self.name())[0].version


  def files(self):
    basedir = pkg_resources.resource_filename(__name__, '')
    filelist = os.path.join(basedir, 'files.txt')
    return [os.path.join(basedir, k.strip()) for k in \
        open(filelist, 'rt').readlines() if k.strip()]


  def type(self):
    return 'text'


  def add_commands(self, parser):
    from . import __doc__ as docs
    self.setup_parser(parser, "MNIST database", docs)
