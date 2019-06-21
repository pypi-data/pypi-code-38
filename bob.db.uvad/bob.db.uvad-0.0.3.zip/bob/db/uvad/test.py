#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Test Units
"""
from bob.db.uvad.config import database as db
import nose


def assert_nfiles(files, total, nbonafide, nattack):
    len_files = len(files)
    assert len_files == total, len_files
    len_bonafide = len([f for f in files if f.attack_type is None])
    len_attack = len_files - len_bonafide
    assert len_bonafide == nbonafide, len_bonafide
    assert len_attack == nattack, len_attack


def test_database():
    protocol = 'experiment_1'
    db.protocol = protocol
    assert len(db.all_files(('train', 'dev'))[0])
    assert len(db.all_files(('train', 'dev'))[1])
    assert_nfiles(db.objects(protocol=protocol), 5244,
                  404, 4840)
    assert_nfiles(db.objects(protocol=protocol,
                             groups='train'), 2768, 344, 2424)
    assert_nfiles(db.objects(protocol=protocol, groups='dev'), 2476, 60, 2416)


def test_frames():
    protocol = 'experiment_1'
    db.protocol = protocol
    if db.original_directory is None:
        raise nose.SkipTest(
            "Please configure bob.db.uvad (refer to package documentation) to "
            "point to the directory where the database's raw data are. This "
            "way we can test more features of the database interface.")
    padfile = db.all_files(('train', 'dev'))[0][0]
    assert db.number_of_frames(padfile) == 270, db.number_of_frames(padfile)
    frame = next(db.frames(padfile))
    assert db.frame_shape == frame.shape, frame.shape
