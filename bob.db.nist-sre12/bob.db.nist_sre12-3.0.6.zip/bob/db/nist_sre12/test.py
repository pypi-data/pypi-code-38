#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Fri Aug 23 16:27:27 CEST 2013
#
# Copyright (C) 2012-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A few checks on the protocols of a subset of the NIST SRE 2012 database
"""

import os, sys
import bob.db.nist_sre12

def db_available(test):
  """Decorator for detecting if the database file is available"""
  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'nist_sre12'))

  return wrapper


@db_available
def test_query():
  from pkg_resources import resource_filename

  db = bob.db.nist_sre12.Database()

  assert(len(db.objects(groups='eval', protocol='core-all', purposes='enroll')) == 55019)
  assert(len(db.objects(groups='eval', protocol='core-all', purposes='probe')) == 73106)
  assert(len(db.objects(groups='eval', protocol='core-c1', purposes='enroll')) == 2379)
  assert(len(db.objects(groups='eval', protocol='core-c1', purposes='probe')) == 22887)
  assert(len(db.objects(groups='eval', protocol='core-c2', purposes='enroll')) == 54919)
  assert(len(db.objects(groups='eval', protocol='core-c2', purposes='probe')) == 14274)
  assert(len(db.objects(groups='eval', protocol='core-c3', purposes='enroll')) == 2379)
  assert(len(db.objects(groups='eval', protocol='core-c3', purposes='probe')) == 17572)
  assert(len(db.objects(groups='eval', protocol='core-c4', purposes='enroll')) == 54919)
  assert(len(db.objects(groups='eval', protocol='core-c4', purposes='probe')) == 11391)
  assert(len(db.objects(groups='eval', protocol='core-c5', purposes='enroll')) == 54919)
  assert(len(db.objects(groups='eval', protocol='core-c5', purposes='probe')) == 6182)

  # check some enroll and probes for given model_ids
  assert (len(db.objects(protocol='core-all', groups='eval', model_ids='110552', purposes='enroll')) == 69 )
  assert (len(db.objects(protocol='core-all', groups='eval', model_ids='110552', purposes='probe')) == 518 )
  assert (len(db.objects(protocol='core-c1', groups='eval', model_ids='120546', purposes='enroll')) == 55 )
  assert (len(db.objects(protocol='core-c1', groups='eval', model_ids='120546', purposes='probe')) == 2538 )

  # male
  assert(len(db.objects(groups='eval', protocol='core-all', gender='male', purposes='enroll')) == 22474)
  assert(len(db.objects(groups='eval', protocol='core-all', gender='male', purposes='probe')) == 29728)
  assert(len(db.objects(groups='eval', protocol='core-c1', gender='male', purposes='enroll')) == 645)
  assert(len(db.objects(groups='eval', protocol='core-c1', gender='male', purposes='probe')) == 8850)
  assert(len(db.objects(groups='eval', protocol='core-c2', gender='male', purposes='enroll')) == 22442)
  assert(len(db.objects(groups='eval', protocol='core-c2', gender='male', purposes='probe')) == 5451)
  assert(len(db.objects(groups='eval', protocol='core-c3', gender='male', purposes='enroll')) == 645)
  assert(len(db.objects(groups='eval', protocol='core-c3', gender='male', purposes='probe')) == 7048)
  assert(len(db.objects(groups='eval', protocol='core-c4', gender='male', purposes='enroll')) == 22442)
  assert(len(db.objects(groups='eval', protocol='core-c4', gender='male', purposes='probe')) == 4386)
  assert(len(db.objects(groups='eval', protocol='core-c5', gender='male', purposes='enroll')) == 22442)
  assert(len(db.objects(groups='eval', protocol='core-c5', gender='male', purposes='probe')) == 2421)

  # female
  assert(len(db.objects(groups='eval', protocol='core-all', gender='female', purposes='enroll')) == 32545)
  assert(len(db.objects(groups='eval', protocol='core-all', gender='female', purposes='probe')) == 43378)
  assert(len(db.objects(groups='eval', protocol='core-c1', gender='female', purposes='enroll')) == 1734)
  assert(len(db.objects(groups='eval', protocol='core-c1', gender='female', purposes='probe')) == 14037)
  assert(len(db.objects(groups='eval', protocol='core-c2', gender='female', purposes='enroll')) == 32477)
  assert(len(db.objects(groups='eval', protocol='core-c2', gender='female', purposes='probe')) == 8823)
  assert(len(db.objects(groups='eval', protocol='core-c3', gender='female', purposes='enroll')) == 1734)
  assert(len(db.objects(groups='eval', protocol='core-c3', gender='female', purposes='probe')) == 10524)
  assert(len(db.objects(groups='eval', protocol='core-c4', gender='female', purposes='enroll')) == 32477)
  assert(len(db.objects(groups='eval', protocol='core-c4', gender='female', purposes='probe')) == 7005)
  assert(len(db.objects(groups='eval', protocol='core-c5', gender='female', purposes='enroll')) == 32477)
  assert(len(db.objects(groups='eval', protocol='core-c5', gender='female', purposes='probe')) == 3761)

@db_available
def test_driver_api():
#
  from bob.db.base.script.dbmanage import main
  assert main('nist_sre12 dumplist --self-test'.split()) == 0
  assert main('nist_sre12 checkfiles --self-test'.split()) == 0
