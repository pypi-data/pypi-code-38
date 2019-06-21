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

import bob.db.cuhk_cufsf
#possible_protocols  = ["cuhk"]

""" Defining protocols. Yes, they are static """
PROTOCOLS = ('search_split1_p2s','search_split2_p2s','search_split3_p2s','search_split4_p2s','search_split5_p2s',
             'search_split1_s2p','search_split2_s2p','search_split3_s2p','search_split4_s2p','search_split5_s2p',
             'idiap_verification_p2s','idiap_verification_s2p')

GROUPS    = ('world', 'dev', 'eval')

PURPOSES   = ('train', 'enroll', 'probe')



def test01_protocols_purposes_groups():
  
  #testing protocols
  possible_protocols = bob.db.cuhk_cufsf.Database().protocols()
  for p in possible_protocols:
    assert p  in PROTOCOLS

  #testing purposes
  possible_purposes = bob.db.cuhk_cufsf.Database().purposes()
  for p in possible_purposes:
    assert p  in PURPOSES

  #testing GROUPS
  possible_groups = bob.db.cuhk_cufsf.Database().groups()
  for p in possible_groups:
    assert p  in GROUPS


def test02_search_files_protocols():

  total_data = 2388
  world      = 1400
  dev        = 988
  dev_enroll = 494
  dev_probe  = 494
  
  
  protocols = bob.db.cuhk_cufsf.Database().protocols()
    
  for p in protocols:
  
    if "search" in p:  
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p)) == total_data
    
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="world")) == world

      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="dev")) == dev
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="dev", purposes="enroll")) == dev_enroll
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="dev", purposes="probe"))  == dev_probe
    
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="eval")) == 0

      # Checking the modalities
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="world", modality=["photo"])) == world//2
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="world", modality=["sketch"])) == world//2
      

def test03_verification_files_protocols():

  total_data = 2388
  world      = 700


  dev        = 700
  dev_enroll = 350
  dev_probe  = 350

  eval        = 988
  eval_enroll = 494
  eval_probe  = 494
  
  
  protocols = bob.db.cuhk_cufsf.Database().protocols()
    
  for p in protocols:
  
    if "verification" in p:  
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p)) == total_data
    
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="world")) == world

      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="dev")) == dev
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="dev", purposes="enroll")) == dev_enroll
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="dev", purposes="probe"))  == dev_probe
    
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="eval")) == eval
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="eval", purposes="enroll")) == eval_enroll
      assert len(bob.db.cuhk_cufsf.Database().objects(protocol=p, groups="eval", purposes="probe"))  == eval_probe



def test04_strings():
  
  db = bob.db.cuhk_cufsf.Database()

  for p in PROTOCOLS:
    for g in GROUPS:
      for u in PURPOSES:
        files = db.objects(purposes=u, groups=g, protocol=p)

        for f in files:
          #Checking if the strings are correct 
          assert f.purpose  == u
          assert f.protocol == p
          assert f.group    == g
       

def test05_annotations():

  db = bob.db.cuhk_cufsf.Database()

  for p in PROTOCOLS:
    for f in db.objects(protocol=p):    

      assert f.annotations()["reye"][0] > 0
      assert f.annotations()["reye"][1] > 0

      assert f.annotations()["leye"][0] > 0
      assert f.annotations()["leye"][1] > 0



 


