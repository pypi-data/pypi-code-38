#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 21 Aug 2012 13:20:38 CEST

"""Tests various examples for bob.db.iris
"""

import nose.tools
from bob.io.base import test_utils

def test_lda():

  from .example.lda import main
  cmdline = ['--self-test']
  assert main(cmdline) == 0

@nose.tools.nottest
def test_backprop():

  from .example.backprop import main
  cmdline = ['--self-test']
  assert main(cmdline) == 0

@nose.tools.nottest
def test_rprop():

  from .example.rprop import main
  cmdline = ['--self-test']
  assert main(cmdline) == 0
