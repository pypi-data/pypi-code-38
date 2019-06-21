#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Thu Oct 09 11:27:27 CEST 2014
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
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

"""A few checks on the protocols of a subset of the CUHK database
"""

import bob.db.ldhf

""" Defining protocols. Yes, they are static """
PROTOCOLS = ('split1','split2','split3','split4','split5','split6','split7','split8','split9','split10')

GROUPS    = ('world', 'dev')

PURPOSES   = ('train', 'enroll', 'probe')




def test01_protocols_purposes_groups():

  #testing protocols

  possible_protocols = bob.db.ldhf.Database().protocols()
  for p in possible_protocols:
    assert p  in PROTOCOLS

  #testing purposes
  possible_purposes = bob.db.ldhf.Database().purposes()
  for p in possible_purposes:
    assert p  in PURPOSES

  #testing GROUPS
  possible_groups = bob.db.ldhf.Database().groups()
  for p in possible_groups:
    assert p  in GROUPS


def test02_all_files_protocols():

  world_files = 400
  enroll_files  = 50
  probe_files   = 10000
  possible_protocols = bob.db.ldhf.Database().protocols()

  for p in possible_protocols:
    assert len(bob.db.ldhf.Database().objects(protocol=p, groups='world'))                 == world_files
    assert len(bob.db.ldhf.Database().objects(protocol=p, groups='dev', purposes="enroll")) == enroll_files
    assert len(bob.db.ldhf.Database().objects(protocol=p, groups='dev', purposes="probe"))  == probe_files


def test03_strings():
  
  db = bob.db.ldhf.Database()

  for p in PROTOCOLS:
    for g in GROUPS:
      for u in PURPOSES:
        files = db.objects(purposes=u, groups=g, protocol=p)

        for f in files:
          #Checking if the strings are correct 
          assert f.purpose  == u
          assert f.protocol == p
          assert f.group    == g


def test09_annotations():

  db = bob.db.ldhf.Database()

  for p in PROTOCOLS:
    for f in db.objects(protocol=p):
      assert f.annotations()["reye"][0] > 0
      assert f.annotations()["reye"][1] > 0

      assert f.annotations()["leye"][0] > 0
      assert f.annotations()["leye"][1] > 0


 


