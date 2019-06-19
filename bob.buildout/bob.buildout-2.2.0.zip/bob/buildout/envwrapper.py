#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon  4 Feb 09:24:35 2013 CET

"""A wrapper for defining environment variables for the compilation
"""

import os
import string
import logging
import platform


def substitute(value, d):
  """Substitutes ${} expressions on ``value`` with values from ``d``, using
  string.Template"""

  return string.Template(value).substitute(**d)

class EnvironmentWrapper(object):
  """Provides methods for wrapping other install() methods with environment
  settings from initialization.
  """

  # 30.01.2017: we only set debug flags, release flags are set by toolchain
  DEBUG_CFLAGS = '-O0 -g -DBOB_DEBUG'

  # Note: CLang does not work well with BZ_DEBUG
  if platform.system() != 'Darwin':
    DEBUG_CFLAGS += " -DBZ_DEBUG"

  def __init__(self, logger, debug=None, prefixes=None, environ=None):

    self.debug = debug
    self.environ = dict(environ) if environ else {}

    # do environment variable substitution on user dictionary
    for key in self.environ:
      self.environ[key] = substitute(self.environ[key], self.environ)

    # if PKG_CONFIG_PATH is set on self.environ, then prefix it
    pkgcfg = []
    if 'PKG_CONFIG_PATH' in self.environ:
      pkgcfg += self.environ['PKG_CONFIG_PATH'].split(os.pathsep)

    # set the pkg-config paths to look at, environment settings in front
    prefixes = prefixes if prefixes else []
    if 'CMAKE_PREFIX_PATH' in self.environ:
      prefixes = self.environ['CMAKE_PREFIX_PATH'].split(os.pathsep) + prefixes
    if 'CMAKE_PREFIX_PATH' in os.environ:
      prefixes = os.environ['CMAKE_PREFIX_PATH'].split(os.pathsep) + prefixes
    if 'BOB_PREFIX_PATH' in self.environ:
      prefixes = self.environ['BOB_PREFIX_PATH'].split(os.pathsep) + prefixes
    if 'BOB_PREFIX_PATH' in os.environ:
      prefixes = os.environ['BOB_PREFIX_PATH'].split(os.pathsep) + prefixes
    pkgcfg += [os.path.join(k, 'lib', 'pkgconfig') for k in prefixes]
    pkgcfg += [os.path.join(k, 'lib64', 'pkgconfig') for k in prefixes]
    pkgcfg += [os.path.join(k, 'lib32', 'pkgconfig') for k in prefixes]

    def __remove_environ(key):
      if key in self.environ: del self.environ[key]

    def __append_to_environ(key, value, sep=' '):
      if self.environ.get(key):
        if value:
          self.environ[key] += sep + value.strip(sep)
      else:
        if value:
          self.environ[key] = value.strip(sep)

    def __prepend_to_environ(key, value, sep=' '):
      if self.environ.get(key):
        if value:
          self.environ[key] = value.strip(sep) + sep + self.environ[key]
      else:
        if value:
          self.environ[key] = value.strip(sep)

    # joins all paths, respecting potential environment variables set by the
    # user, with priority
    __remove_environ('BOB_PREFIX_PATH')
    __append_to_environ('BOB_PREFIX_PATH', os.pathsep.join(prefixes),
        os.pathsep)

    __remove_environ('CMAKE_PREFIX_PATH')
    __append_to_environ('CMAKE_PREFIX_PATH', os.pathsep.join(prefixes),
        os.pathsep)

    __remove_environ('PKG_CONFIG_PATH')
    __append_to_environ('PKG_CONFIG_PATH', os.environ.get('PKG_CONFIG_PATH'),
        os.pathsep)
    __append_to_environ('PKG_CONFIG_PATH', os.pathsep.join(pkgcfg), os.pathsep)

    # reset the CFLAGS and CXXFLAGS depending on the user input
    cflags = None
    if self.debug is True: cflags = str(EnvironmentWrapper.DEBUG_CFLAGS)
    # else: pass

    def _order_flags(key, internal=None):
      if internal:
        # prepend internal
        saved = self.environ.get(key)
        __remove_environ(key)
        __append_to_environ(key, internal)
        __append_to_environ(key, saved)
      __prepend_to_environ(key, os.environ.get(key))

    # for these environment variables, values set on the environment come first
    # so we can override with our debug flag
    if cflags is not None:
      _order_flags('CFLAGS', cflags)
      _order_flags('CXXFLAGS', cflags)

  def set(self):
    """Sets the current environment for variables needed for the setup of the
    package to be compiled"""

    self._saved_environment = dict(os.environ) #copy
    os.environ.update(self.environ)

  def unset(self):
    """Resets the environment back to its previous state"""

    # cleanup
    if self._saved_environment:
      os.environ = self._saved_environment
      self._saved_environment = {}

  def __enter__(self):
    self.set()

  def __exit__(self, *exc_details):
    self.unset()
