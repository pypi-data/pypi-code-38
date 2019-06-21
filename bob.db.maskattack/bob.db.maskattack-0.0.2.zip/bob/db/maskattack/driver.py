#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Mon 25 Feb 15:21:28 2013

"""Bob Database Driver entry-point for the 3d mask attack database
"""

import os
import sys
from bob.db.base.driver import Interface as BaseInterface

class Interface(BaseInterface):

  def name(self):
    return 'maskattack'

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('bob.db.%s' % self.name())[0].version

  def files(self):

    from pkg_resources import resource_filename
    raw_files = ('db.sql3',)
    return [resource_filename(__name__, k) for k in raw_files]

  def type(self):
    return 'sqlite'

  def add_commands(self, parser):

    from . import __doc__ as docs
    
    subparsers = self.setup_parser(parser, 
        "3D mask attack database", docs)

    # get the "create" action from a submodule
    from .create import add_command as create_command
    create_command(subparsers)

    # get the "dumplist" action from a submodule
    from .dumplist import add_command as dumplist_command
    dumplist_command(subparsers)

    # get the "checkfiles" action from a submodule
    from .checkfiles import add_command as checkfiles_command
    checkfiles_command(subparsers)
