#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 21 Aug 2012 13:20:38 CEST

"""Tests various scripts for our bob.db driver
"""

def test_iris_files():

  from bob.db.iris.driver import Interface
  import os

  for k in Interface().files():
    assert os.path.exists(k)

def test_iris_dump():

  from bob.db.base.script.dbmanage import main
  cmdline = 'iris dump --self-test'
  assert main(cmdline.split()) == 0

def test_iris_dump_2():

  from bob.db.base.script.dbmanage import main
  cmdline = 'iris dump --class=versicolor --self-test'
  assert main(cmdline.split()) == 0

def test_iris_files_2():

  from bob.db.base.script.dbmanage import main
  assert main('iris files'.split()) == 0

def test_iris_version():

  from bob.db.base.script.dbmanage import main
  assert main('iris version'.split()) == 0
