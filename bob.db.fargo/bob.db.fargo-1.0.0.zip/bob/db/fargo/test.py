#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Fri 23 Dec 09:49:48 CET 2016


"""A few checks on the protocols of the FARGO public database 
"""
import os, sys
import bob.db.base
import bob.db.fargo

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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'fargo'))

  return wrapper


@db_available
def test_clients():

  # test whether the correct number of clients is returned
  db = bob.db.fargo.Database()
  assert len(db.groups()) == 3
  assert len(db.clients()) == 75
  assert len(db.clients(groups='world')) == 25
  assert len(db.clients(groups='dev')) == 25
  assert len(db.clients(groups='eval')) == 25


@db_available
def test_objects():
#  # tests if the right number of File objects is returned
  
  db = bob.db.fargo.Database()

  assert len(db.objects(protocol='mc-rgb', groups='world')) == 1000
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='enroll')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='enroll', model_ids=26)) == 20
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='probe')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='dev', purposes='probe', model_ids=26)) == 500 # dense probing
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='enroll')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='enroll', model_ids=51)) == 20
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='probe')) == 500
  assert len(db.objects(protocol='mc-rgb', groups='eval', purposes='probe', model_ids=51)) == 500 # dense probing

  assert len(db.objects(protocol='ud-nir', groups='world')) == 1000
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='enroll')) == 500
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='enroll', model_ids=26)) == 20
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='probe')) == 1000
  assert len(db.objects(protocol='ud-nir', groups='dev', purposes='probe', model_ids=26)) == 1000 # dense probing
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='enroll')) == 500
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='enroll', model_ids=51)) == 20
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='probe')) == 1000
  assert len(db.objects(protocol='ud-nir', groups='eval', purposes='probe', model_ids=51)) == 1000 # dense probing

  assert len(db.objects(protocol='uo-depth', groups='world')) == 1000
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='enroll')) == 500
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='enroll', model_ids=26)) == 20
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='probe')) == 1000
  assert len(db.objects(protocol='uo-depth', groups='dev', purposes='probe', model_ids=26)) == 1000 # dense probing
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='enroll')) == 500
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='enroll', model_ids=51)) == 20
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='probe')) == 1000
  assert len(db.objects(protocol='uo-depth', groups='eval', purposes='probe', model_ids=51)) == 1000 # dense probing


@db_available
def test_heterogeneous():    
    # Test heterogeous protocols    

    db = bob.db.fargo.Database()

    groups = ["dev", "eval"]

    ##############
    # Testing controlled
    ##############
    protocols = ["mc-rgb2nir", "mc-rgb2depth"]
    probe_modalities = ["nir", "depth"]

    for p, m in zip(protocols, probe_modalities):
        assert len(db.objects(protocol=p)) == 4000       
        assert len(db.objects(protocol=p, groups="world")) == 2000
        assert len(db.objects(protocol=p, groups="world", modality=m)) == 1000

        for g in groups:
            assert len(db.objects(protocol=p, groups="dev")) == 1000
            assert len(db.objects(protocol=p, groups="eval")) == 1000

            # Checking the modalities
            modality = set([o.modality for o in db.objects(protocol=p, groups=g, purposes="enroll")])
            assert len(modality) == 1
            assert list(modality)[0] == "rgb"

            modality = set([o.modality for o in db.objects(protocol=p, groups=g, purposes="probe")])
            assert len(modality) == 1
            assert list(modality)[0] == m
            
    #############
    # Testing UNcontrolled
    #############
    protocols = ["ud-rgb2nir", "ud-rgb2depth",
                 "uo-rgb2nir", "uo-rgb2depth"]
    probe_modalities = ["nir", "depth",
                        "nir", "depth"]
  
    for p, m in zip(protocols, probe_modalities):
        assert len(db.objects(protocol=p)) == 5000
        assert len(db.objects(protocol=p, groups="world")) == 2000
        assert len(db.objects(protocol=p, groups="world", modality=m)) == 1000

        for g in groups:
            assert len(db.objects(protocol=p, groups="dev")) == 1500
            assert len(db.objects(protocol=p, groups="eval")) == 1500

            # Checking the modalities
            modality = set([o.modality for o in db.objects(protocol=p, groups=g, purposes="enroll")])
            assert len(modality) == 1
            assert list(modality)[0] == "rgb"

            modality = set([o.modality for o in db.objects(protocol=p, groups=g, purposes="probe")])
            assert len(modality) == 1
            assert list(modality)[0] == m
 
