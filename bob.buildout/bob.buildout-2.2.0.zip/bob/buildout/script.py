#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds custom scripts with the right paths for external dependencies
installed on different prefixes.
"""

import os
import sys
import time
import logging
from zc.recipe.egg import Scripts

from . import tools
from .envwrapper import EnvironmentWrapper

import zc.buildout.easy_install

# Monkey patches the default template for script generation
zc.buildout.easy_install.script_template = \
    zc.buildout.easy_install.script_header + """ -S
# Automatically generated on %(date)s

'''Runs a specific user program'''

%%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %%(path)s,
  ]

#see: http://bugs.python.org/issue30167
if sys.version_info[:2] >= (3, 6) and \
    sys.modules['__main__'].__loader__ is not None:
  _hack = str(sys.modules['__main__'].__loader__.__module__)
  sys.modules['__main__'].__loader__.__module__ += '_'
import site #initializes site properly
site.main() #this is required for python>=3.4
if sys.version_info[:2] >= (3, 6) and \
    sys.modules['__main__'].__loader__ is not None:
  #restores original value
  sys.modules['__main__'].__loader__.__module__ = _hack
import pkg_resources #initializes virtualenvs properly
%%(initialization)s
import %%(module_name)s

if __name__ == '__main__':
    sys.exit(%%(module_name)s.%%(attrs)s(%%(arguments)s))
""" % {'date': time.asctime()}

class ScriptGenerator(object):
  """Replaces the default script generator so paths are properly filtered"""

  def __init__(self, buildout, prefixes):

    self.buildout = buildout
    self.prefixes = prefixes

  def __enter__(self):
    self.__old__  = zc.buildout.easy_install._script
    zc.buildout.easy_install._script = self

  def __exit__(self, *exc_details):
    zc.buildout.easy_install._script = self.__old__

  def __call__(self, module_name, attrs, path, dest, arguments, initialization, rsetup):
    """Default script generator"""

    if zc.buildout.easy_install.is_win32: dest += '-script.py'

    python = zc.buildout.easy_install._safe_arg(sys.executable)

    # the "difference": re-order python paths with a preference for locals
    realpath = [k.strip().strip("'").strip('"') for k in path.split(",\n")]
    realpath = [os.path.realpath(k.strip()) for k in realpath if k.strip()]
    path = ",\n  ".join(["'%s'" % k for k in realpath if k not in tools.site_paths(self.buildout['buildout'], self.prefixes)])
    if not path: path = "''" #dummy path

    contents = zc.buildout.easy_install.script_template % dict(
        python = python,
        path = path,
        module_name = module_name,
        attrs = attrs,
        arguments = arguments,
        initialization = initialization,
        relative_paths_setup = rsetup,
        )

    return zc.buildout.easy_install._create_script(contents, dest)

class Recipe(Scripts):
  """Just creates a given script with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    self.buildout = buildout
    self.name = name
    self.options = options

    self.logger = logging.getLogger(self.name)

    # Gets a personalized eggs list or the one from buildout
    self.eggs = tools.eggs(buildout['buildout'], options, name)

    # Gets a personalized prefixes list or the one from buildout
    self.prefixes = tools.get_prefixes(buildout['buildout'])
    self.user_paths = tools.find_site_packages(self.prefixes)

    # Builds an environment wrapper, in case dependent packages need to be
    # compiled
    self.envwrapper = EnvironmentWrapper(self.logger,
        tools.debug(buildout['buildout']), self.prefixes)

    # initializes the script infrastructure
    super(Recipe, self).__init__(buildout, name, options)

  def working_set(self, extra=()):
    """Separate method to just get the working set - overriding zc.recipe.egg

    This is intended for reuse by similar recipes.
    """

    distributions = self.eggs + list(extra)

    if tools.offline(self.buildout['buildout']):

      ws = tools.working_set(self.buildout['buildout'])
      ws = tools.filter_working_set_hard(ws, distributions)

    else:

      ws = tools.working_set(self.buildout['buildout'])

      if tools.newest(self.buildout['buildout']):

        for d in distributions:
          tools.install_package(self.buildout['buildout'], d, ws)

      else: #only installs packages which are not yet installed

        _ws, to_install = tools.filter_working_set_soft(ws, distributions)
        for d in to_install:
          tools.install_package(self.buildout['buildout'], d, ws)

      ws = tools.filter_working_set_hard(ws, distributions)

    return self.eggs, ws

  def install_on_wrapped_env(self):
    with ScriptGenerator(self.buildout, self.prefixes) as sg:
      return tuple(super(Recipe, self).install())

  def install(self):
    with self.envwrapper as ew:
      return self.install_on_wrapped_env()

  update = install
