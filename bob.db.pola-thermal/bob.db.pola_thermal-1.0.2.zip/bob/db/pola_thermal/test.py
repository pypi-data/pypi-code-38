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

"""A few checks on the protocols of the Near-Infrared and Visible-Light (NIVL) Dataset
"""

import bob.db.pola_thermal

""" Defining protocols. Yes, they are static """
PROTOCOLS = ( 
              'VIS-VIS-split1', \
              'VIS-VIS-split2', \
              'VIS-VIS-split3', \
              'VIS-VIS-split4', \
              'VIS-VIS-split5', \

              'VIS-thermal-overall-split1', \
              'VIS-thermal-overall-split2', \
              'VIS-thermal-overall-split3', \
              'VIS-thermal-overall-split4', \
              'VIS-thermal-overall-split5', \

              'VIS-polarimetric-overall-split1', \
              'VIS-polarimetric-overall-split2', \
              'VIS-polarimetric-overall-split3', \
              'VIS-polarimetric-overall-split4', \
              'VIS-polarimetric-overall-split5', \

               ########## EXPRESSION

              'VIS-thermal-expression-split1', \
              'VIS-thermal-expression-split2', \
              'VIS-thermal-expression-split3', \
              'VIS-thermal-expression-split4', \
              'VIS-thermal-expression-split5', \

              'VIS-polarimetric-expression-split1', \
              'VIS-polarimetric-expression-split2', \
              'VIS-polarimetric-expression-split3', \
              'VIS-polarimetric-expression-split4', \
              'VIS-polarimetric-expression-split5', \

               ########## RANGE 1

              'VIS-thermal-R1-split1', \
              'VIS-thermal-R1-split2', \
              'VIS-thermal-R1-split3', \
              'VIS-thermal-R1-split4', \
              'VIS-thermal-R1-split5', \

              'VIS-polarimetric-R1-split1', \
              'VIS-polarimetric-R1-split2', \
              'VIS-polarimetric-R1-split3', \
              'VIS-polarimetric-R1-split4', \
              'VIS-polarimetric-R1-split5', \

               ########## RANGE 2

              'VIS-thermal-R2-split1', \
              'VIS-thermal-R2-split2', \
              'VIS-thermal-R2-split3', \
              'VIS-thermal-R2-split4', \
              'VIS-thermal-R2-split5', \

              'VIS-polarimetric-R2-split1', \
              'VIS-polarimetric-R2-split2', \
              'VIS-polarimetric-R2-split3', \
              'VIS-polarimetric-R2-split4', \
              'VIS-polarimetric-R2-split5', \

               ########## RANGE 3

              'VIS-thermal-R3-split1', \
              'VIS-thermal-R3-split2', \
              'VIS-thermal-R3-split3', \
              'VIS-thermal-R3-split4', \
              'VIS-thermal-R3-split5', \

              'VIS-polarimetric-R3-split1', \
              'VIS-polarimetric-R3-split2', \
              'VIS-polarimetric-R3-split3', \
              'VIS-polarimetric-R3-split4', \
              'VIS-polarimetric-R3-split5')

GROUPS    = ('world', 'dev')

PURPOSES   = ('train', 'enroll', 'probe')



def test01_protocols_purposes_groups():

  #testing protocols

  possible_protocols = bob.db.pola_thermal.Database().protocols()
  for p in possible_protocols:
    assert p  in PROTOCOLS

  #testing purposes
  possible_purposes = bob.db.pola_thermal.Database().purposes()
  for p in possible_purposes:
    assert p  in PURPOSES

  #testing GROUPS
  possible_groups = bob.db.pola_thermal.Database().groups()
  for p in possible_groups:
    assert p  in GROUPS


def test02_vis_vis():

  for i in range(1,6):
    protocol = 'VIS-VIS-split{0}'.format(i)
    
    assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='world')) == 25*16
    assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='enroll')) == 35*4
    assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='probe')) == 35*12
  

def test03_vis_overall():

  for p in ['thermal', 'polarimetric']:
    for i in range(1,6):
      protocol = "VIS-{0}-overall-split{1}".format(p, i)
    
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='world')) == 25*16 + 25*48 # VIS + Thermal
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='enroll')) == 35*4 # VIS
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='probe')) == 35*48 # Thermal
      
      # Checking the modalities
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups="world", modality=["VIS"])) == 25*16
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups="world", modality=["THERMAL"])) == 25*48


def test04_vis_expression():

  for p in ['thermal', 'polarimetric']:
    for i in range(1,6):
      protocol = "VIS-{0}-expression-split{1}".format(p, i)
    
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='world')) == 25*16 + 25*48 # VIS + Thermal
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='enroll')) == 35*4 # VIS
      assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='probe')) == 35*36 # Thermal


def test05_vis_ranges():

  for p in ['thermal', 'polarimetric']:
    for r in ['R1', 'R2', 'R3']:
      for i in range(1,6):
        protocol = "VIS-{0}-{1}-split{2}".format(p, r, i)
    
        assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='world')) == 25*16 + 25*48 # VIS + Thermal
        assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='enroll')) == 35*4 # VIS
        assert len(bob.db.pola_thermal.Database().objects(protocol=protocol, groups='dev', purposes='probe')) == 35*16 # Thermal


def test06_annotations():

  db = bob.db.pola_thermal.Database()

  for p in PROTOCOLS:
    for f in db.objects(protocol=p):
      assert f.annotations()["reye"][0] > 0
      assert f.annotations()["reye"][1] > 0

      assert f.annotations()["leye"][0] > 0
      assert f.annotations()["leye"][1] > 0


def test08_strings():
  
  db = bob.db.pola_thermal.Database()

  for p in PROTOCOLS:
    for g in GROUPS:
      for u in PURPOSES:
        files = db.objects(purposes=u, groups=g, protocol=p)
        for f in files:
          #Checking if the strings are correct 
          assert f.purpose  == u
          assert f.protocol == p
          assert f.group    == g

