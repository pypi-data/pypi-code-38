#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds custom interpreters with the right paths for external Bob
"""

import os
import six
import logging
import pkg_resources
import zc.buildout
from . import tools
from .script import Recipe as Script
from .python import Recipe as PythonInterpreter
from .dbpy import Recipe as DebuggerPythonInterpreter
from .envwrapper import EnvironmentWrapper

def version_is_lessthan(name, version):
  """Checks if the version of a package is at least..."""

  if not is_available(name): return False
  else:
    from distutils.version import LooseVersion
    return LooseVersion(pkg_resources.require(name)[0].version) < version

class UserScripts(Script):
  """Installs all user scripts from the eggs"""

  def __init__(self, buildout, name, options):

    self.name = name
    self.buildout = buildout
    self.options = options

    if 'interpreter' in options: del self.options['interpreter']
    if 'scripts' in options: del self.options['scripts']
    super(UserScripts, self).__init__(self.buildout, self.name, self.options)

  def install(self):

    return super(UserScripts, self).install()

  update = install

class IPythonInterpreter(Script):
  """Installs all user scripts from the eggs"""

  def __init__(self, buildout, name, options):

    self.name = name
    self.buildout = buildout
    self.options = options

    # adds ipython interpreter into the mix
    interpreter = self.options.setdefault('interpreter', 'python')
    del self.options['interpreter']
    self.options['entry-points'] = 'i%s=IPython.frontend.terminal.ipapp:launch_new_instance' % interpreter
    self.options['scripts'] = 'i%s' % interpreter
    self.options['dependent-scripts'] = 'false'

    eggs = tools.eggs(self.buildout['buildout'], self.options, self.name)
    self.options['eggs'] = tools.add_eggs(eggs, ['ipython'])

    # initializes base class
    super(IPythonInterpreter, self).__init__(self.buildout,
        self.name, self.options)

  def install(self):

    return super(IPythonInterpreter, self).install()

  update = install

class PyLint(Script):
  """Installs PyLint infrastructure"""

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name)
    self.name = name
    self.buildout = buildout
    self.options = options

    if 'interpreter' in options: del self.options['interpreter']
    if 'pylint-flags' in options:
      if version_is_lessthan('pylint', '1.0'):
        # use 'options' instead of 'self.options' to force use
        flags = tools.parse_list(options['pylint-flags'])
        init_code = ['sys.argv.append(%r)' % k for k in flags]
        self.options['initialization'] = '\n'.join(init_code)
      else:
        self.logger.warn('the option pylint-flags for this recipe is only available for older versions of pylint < 1.0')
    self.options['entry-points'] = 'pylint=pylint.lint:Run'
    self.options['arguments'] = 'sys.argv[1:]'
    self.options['scripts'] = 'pylint'
    self.options['dependent-scripts'] = 'false'

    eggs = tools.eggs(self.buildout['buildout'], self.options, self.name)
    self.options['eggs'] = tools.add_eggs(eggs, ['pylint'])

    # initializes base class
    super(PyLint, self).__init__(self.buildout, self.name, self.options)

  def install(self):

    return super(PyLint, self).install()

  update = install

class NoseTests(Script):
  """Installs Nose infrastructure"""

  def __init__(self, buildout, name, options):

    self.name = name
    self.buildout = buildout
    self.options = options

    if 'interpreter' in options: del options['interpreter']
    if 'nose-flags' in options:
      # use 'options' instead of 'options' to force use
      flags = tools.parse_list(options['nose-flags'])
      init_code = ['sys.argv.append(%r)' % k for k in flags]
      options['initialization'] = '\n'.join(init_code)
    self.options['entry-points'] = 'nosetests=nose:run_exit'
    self.options['scripts'] = 'nosetests'
    self.options['dependent-scripts'] = 'false'

    eggs = tools.eggs(self.buildout['buildout'], self.options, self.name)
    self.options['eggs'] = tools.add_eggs(eggs, ['nose'])

    # initializes base class
    super(NoseTests, self).__init__(self.buildout, self.name, self.options)

  def install(self):

    return super(NoseTests, self).install()

  update = install

class Coverage(Script):
  """Installs Coverage infrastructure"""

  def __init__(self, buildout, name, options):

    self.name = name
    self.buildout = buildout
    self.options = options

    if 'interpreter' in options: del options['interpreter']
    if 'coverage-flags' in options:
      # use 'options' instead of 'options' to force use
      flags = tools.parse_list(options['coverage-flags'])
      init_code = ['sys.argv.append(%r)' % k for k in flags]
      self.options['initialization'] = '\n'.join(init_code)
    self.options['entry-points'] = 'coverage=coverage.cmdline:main'
    self.options['scripts'] = 'coverage'
    self.options['dependent-scripts'] = 'false'

    eggs = tools.eggs(self.buildout['buildout'], self.options, self.name)
    self.options['eggs'] = tools.add_eggs(eggs, ['coverage'])

    # initializes base class
    super(Coverage, self).__init__(self.buildout, self.name, self.options)

  def install(self):

    return super(Coverage, self).install()

  update = install

class Sphinx(Script):
  """Installs the Sphinx documentation generation infrastructure"""

  def __init__(self, buildout, name, options):

    self.name = name
    self.buildout = buildout
    self.options = options

    if 'interpreter' in options: del self.options['interpreter']
    self.options['scripts'] = '\n'.join([
      'sphinx-build',
      'sphinx-apidoc',
      'sphinx-autogen',
      'sphinx-quickstart',
      ])
    self.options['entry-points'] = '\n'.join([
      'sphinx-build=sphinx.cmd.build:main',
      'sphinx-apidoc=sphinx.ext.apidoc:main',
      'sphinx-autogen=sphinx.ext.autosummary.generate:main',
      'sphinx-quickstart=sphinx.cmd.quickstart:main',
      ])
    self.options['dependent-scripts'] = 'false'

    eggs = tools.eggs(self.buildout['buildout'], self.options, self.name)
    self.options['eggs'] = tools.add_eggs(eggs, ['sphinx'])

    # initializes base class
    super(Sphinx, self).__init__(self.buildout, self.name, self.options)

  def install(self):

    return super(Sphinx, self).install()

  update = install

class Recipe(object):
  """Just creates a given script with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name.capitalize())

    # Gets a personalized prefixes list or the one from buildout
    prefixes = tools.get_prefixes(buildout['buildout'])

    # Builds an environment wrapper, in case dependent packages need to be
    # compiled
    self.envwrapper = EnvironmentWrapper(self.logger,
        tools.debug(buildout['buildout']), prefixes)

    # Touch the options
    self.dependent_scripts = options.get('dependent-scripts')

    self.python = PythonInterpreter(buildout, 'Python', options.copy())
    #self.ipython = IPythonInterpreter(buildout, 'IPython', options.copy())
    self.dbpy = DebuggerPythonInterpreter(buildout, 'DebugPython',
        options.copy())
    self.scripts = UserScripts(buildout, 'Scripts', options.copy())
    self.nose = NoseTests(buildout, 'Nose', options.copy())
    self.coverage = Coverage(buildout, 'Coverage', options.copy())
    self.sphinx = Sphinx(buildout, 'Sphinx', options.copy())

  def install(self):
    with self.envwrapper as ew:
      return \
          self.python.install_on_wrapped_env() + \
          self.dbpy.install_on_wrapped_env() + \
          self.scripts.install_on_wrapped_env() + \
          self.nose.install_on_wrapped_env() + \
          self.coverage.install_on_wrapped_env() + \
          self.sphinx.install_on_wrapped_env()

  update = install
