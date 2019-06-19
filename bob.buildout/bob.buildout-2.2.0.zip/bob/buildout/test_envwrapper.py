#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri 21 Mar 2014 11:50:06 CET

'''Tests for our environment wrapper class'''

import os
import logging
import nose.tools
import platform

from .envwrapper import EnvironmentWrapper

def cleanup():
  '''Removes weird variables from the user environment just for the tests'''

  remove = ['CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'BOB_PREFIX_PATH',
      'PKG_CONFIG_PATH', 'CMAKE_PREFIX_PATH']
  for key in remove:
    if key in os.environ: del os.environ[key]

@nose.with_setup(cleanup)
def test_default():

  e = EnvironmentWrapper(logging.getLogger())

  before = dict(os.environ)

  e.set()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

@nose.with_setup(cleanup)
def test_set_debug_true():

  # a few checks before we start
  assert 'CFLAGS' not in os.environ
  assert 'CXXFLAGS' not in os.environ

  e = EnvironmentWrapper(logging.getLogger(), debug=True)

  before = dict(os.environ)

  e.set()

  nose.tools.eq_(len(os.environ) - len(before), 2)

  assert 'CFLAGS' in os.environ
  assert os.environ['CFLAGS'].find(EnvironmentWrapper.DEBUG_CFLAGS) >= 0
  assert 'CXXFLAGS' in os.environ
  assert os.environ['CXXFLAGS'].find(EnvironmentWrapper.DEBUG_CFLAGS) >= 0

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

@nose.with_setup(cleanup)
def test_set_debug_false():

  # a few checks before we start
  assert 'CFLAGS' not in os.environ
  assert 'CXXFLAGS' not in os.environ

  e = EnvironmentWrapper(logging.getLogger(), debug=False)

  before = dict(os.environ)

  e.set()

  nose.tools.eq_(len(os.environ) - len(before), 0)

  assert 'CFLAGS' not in os.environ
  assert 'CXXFLAGS' not in os.environ

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

@nose.with_setup(cleanup)
def test_set_prefixes():

  # a few checks before we start
  assert 'PKG_CONFIG_PATH' not in os.environ

  prefixes = ['/a/b', '/c/d']
  e = EnvironmentWrapper(logging.getLogger(), prefixes=prefixes)

  before = dict(os.environ)

  e.set()
  #nose.tools.eq_(len(os.environ) - len(before), 2)
  assert 'PKG_CONFIG_PATH' in os.environ
  nose.tools.eq_(os.environ['PKG_CONFIG_PATH'], e.environ['PKG_CONFIG_PATH'])
  assert 'BOB_PREFIX_PATH' in os.environ
  nose.tools.eq_(os.environ['BOB_PREFIX_PATH'], os.pathsep.join(prefixes))
  assert 'CMAKE_PREFIX_PATH' in os.environ
  nose.tools.eq_(os.environ['CMAKE_PREFIX_PATH'], os.pathsep.join(prefixes))

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

@nose.with_setup(cleanup)
def test_set_environment():

  # a few checks before we start
  varname = 'BOB_FOO'
  varvalue = 'abc'
  assert varname not in os.environ

  e = EnvironmentWrapper(logging.getLogger(), environ={varname: varvalue})

  before = dict(os.environ)

  e.set()

  nose.tools.eq_(len(os.environ) - len(before), 1)
  assert varname in os.environ
  nose.tools.eq_(os.environ[varname], varvalue)

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

@nose.with_setup(cleanup)
def test_environ_substitutions():

  # defines the environment with all legal substitutions
  environ = dict(
      BOB_FOO = 'foo',
      BOB_T1 = '${BOB_FOO}:bar',
      BOB_T2 = 'bar$BOB_FOO',
      )

  e = EnvironmentWrapper(logging.getLogger(), environ=environ)

  before = dict(os.environ)

  e.set()
  nose.tools.eq_(len(os.environ) - len(before), 3)
  for key in environ: assert key in os.environ
  nose.tools.eq_(os.environ['BOB_FOO'], environ['BOB_FOO'])
  nose.tools.eq_(os.environ['BOB_T1'], environ['BOB_FOO'] + ':bar')
  nose.tools.eq_(os.environ['BOB_T2'], 'bar' + environ['BOB_FOO'])

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

@nose.with_setup(cleanup)
def test_set_multiple():

  # a few checks before we start
  environ = dict(
      CFLAGS='-DNDEBUG',
      CXXFLAGS='${CFLAGS}',
      PKG_CONFIG_PATH='/a/b/lib/pkgconfig',
      BOB_PREFIX_PATH='/c/d',
      CMAKE_PREFIX_PATH='/d/f',
      )

  e = EnvironmentWrapper(logging.getLogger(), debug=True, environ=environ)

  before = dict(os.environ)

  e.set()

  nose.tools.eq_(len(os.environ) - len(before), 5)

  nose.tools.eq_(os.environ['CFLAGS'], EnvironmentWrapper.DEBUG_CFLAGS + ' ' + environ['CFLAGS'])
  nose.tools.eq_(os.environ['CXXFLAGS'], os.environ['CFLAGS'])
  assert os.environ['BOB_PREFIX_PATH'].startswith(environ['BOB_PREFIX_PATH'])
  assert os.environ['BOB_PREFIX_PATH'].endswith(environ['CMAKE_PREFIX_PATH'])
  assert os.environ['CMAKE_PREFIX_PATH'] == os.environ['BOB_PREFIX_PATH']
  assert os.environ['PKG_CONFIG_PATH'].startswith(environ['PKG_CONFIG_PATH'])
  assert os.environ['PKG_CONFIG_PATH'].find(environ['BOB_PREFIX_PATH']) >= 0

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)

@nose.with_setup(cleanup)
def test_preserve_user():

  # a few checks before we start
  environ = dict(
      CFLAGS='-DNDEBUG',
      CXXFLAGS='${CFLAGS}',
      )

  os.environ['CFLAGS'] = '-BUILDOUT-TEST-STRING'

  e = EnvironmentWrapper(logging.getLogger(), debug=True, environ=environ)

  before = dict(os.environ)

  e.set()

  nose.tools.eq_(len(os.environ) - len(before), 1)

  assert os.environ['CFLAGS'].startswith('-BUILDOUT-TEST-STRING')

  e.unset()
  for key in before:
    assert key in os.environ, "key `%s' from before is not on os.environ" % (key,)
  for key in os.environ:
    assert key in before, "key `%s' was not on os.environ before" % (key,)
  nose.tools.eq_(before, os.environ)
