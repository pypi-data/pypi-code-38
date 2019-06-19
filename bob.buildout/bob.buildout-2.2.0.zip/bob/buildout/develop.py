#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon  4 Feb 09:24:35 2013 CET

"""Compiles a Python/C++ egg extension for Bob
"""

import os
import sys
import shutil
import tempfile
import logging
import warnings
from . import tools
import zc.buildout.easy_install
from .envwrapper import EnvironmentWrapper
from .python import Recipe as PythonInterpreter

class Recipe(object):
  """Compiles a Python/C++ egg extension for Bob
  """

  def __init__(self, buildout, name, options):

    self.name, self.options = name, options
    self.logger = logging.getLogger(self.name)
    self.buildout = buildout

    self.logger.warn("this recipe is **deprecated**, use bob.buildout as your first extension instead (before any other)")

    # finds the setup script or use the default
    self.setup = os.path.join(buildout['buildout']['directory'],
        options.get('setup', '.'))

    # some fine-tunning
    if os.path.isdir(self.setup):
      self.directory = self.setup
      self.setup = os.path.join(self.directory, 'setup.py')
    else:
      self.directory = os.path.dirname(self.setup)

    # where to place the egg
    self.dest = self.buildout['buildout']['develop-eggs-directory']

    # the eggs we need to **build** this package
    eggs = tools.parse_list(options.get('eggs', ''))
    required_eggs = [
        'bob.extension', # basic extension building using pkg-config + Bob
        ]
    eggs += required_eggs
    eggs = tools.uniq(eggs)

    # generates the script that will work as the "builder"
    builder_options = self.options.copy()
    builder_options['eggs'] = '\n'.join(eggs)
    name = self.options.get('interpreter', 'xpython.builder')
    builder_options['interpreter'] = name
    self.builder = PythonInterpreter(buildout, name, builder_options)

    self.debug = tools.debug(self.buildout['buildout'])
    self.verbose = tools.verbose(self.buildout['buildout'])

    # gets a personalized prefixes list or the one from buildout
    prefixes = tools.parse_list(options.get('prefixes', ''))
    if not prefixes:
      prefixes = tools.parse_list(buildout['buildout'].get('prefixes', ''))

    self.envwrapper = EnvironmentWrapper(self.logger, self.debug, prefixes)

  def develop(self, executable):
    """Copy of zc.buildout.easy_install.develop()

    This copy has been modified to use our own development executable
    """

    undo = []
    try:
      fd, tsetup = tempfile.mkstemp()
      undo.append(lambda: os.remove(tsetup))
      undo.append(lambda: os.close(fd))

      if hasattr(zc.buildout.easy_install, 'distribute_loc'):
        os.write(fd, (zc.buildout.easy_install.runsetup_template % dict(
          distribute=zc.buildout.easy_install.distribute_loc,
          setupdir=self.directory,
          setup=self.setup,
          __file__ = self.setup,
          )).encode())
      else:
        os.write(fd, (zc.buildout.easy_install.runsetup_template % dict(
          setuptools=zc.buildout.easy_install.setuptools_loc,
          setupdir=self.directory,
          setup=self.setup,
          __file__ = self.setup,
          )).encode())

      tmp3 = tempfile.mkdtemp('build', dir=self.dest)
      undo.append(lambda : shutil.rmtree(tmp3))

      args = [executable, tsetup, '-q', 'develop', '-mxN', '-d', tmp3]
      if self.verbose: args[2] = '-v'

      self.logger.debug("in: %r\n%s", self.directory, ' '.join(args))

      zc.buildout.easy_install.call_subprocess(args)

      return zc.buildout.easy_install._copyeggs(tmp3, self.dest, '.egg-link', undo)

    finally:
      undo.reverse()
      [f() for f in undo]


  # a modified copy of zc.buildout.easy_install.develop
  def install(self):
    with self.envwrapper as ew:
      retval = self.builder.install_on_wrapped_env()
      retval += (self.develop(retval[0]),)
      return retval

  update = install
