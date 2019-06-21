#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Test Units
"""
from bob.db.oulunpu.config import database as db
import nose


def assert_nfiles(files, total, nbonafide, nattack):
    len_files = len(files)
    assert len_files == total, len_files
    len_bonafide = len([f for f in files if f.attack_type is None])
    len_attack = len_files - len_bonafide
    assert len_bonafide == nbonafide, len_bonafide
    assert len_attack == nattack, len_attack


def test_database():
    protocol = 'Protocol_1'
    db.protocol = protocol
    assert len(db.all_files()[0])
    assert len(db.all_files()[1])
    assert_nfiles(db.objects(protocol=protocol), 1200 + 900 + 600,
                  240 + 180 + 120, 960 + 720 + 480)
    assert_nfiles(db.objects(protocol=protocol,
                             groups='train'), 1200, 240, 960)
    assert_nfiles(db.objects(protocol=protocol, groups='dev'), 900, 180, 720)
    assert_nfiles(db.objects(protocol=protocol, groups='eval'), 600, 120, 480)

    protocol = 'Protocol_2'
    db.protocol = protocol
    assert_nfiles(db.objects(protocol=protocol), 1080 * 2 + 810,
                  360 + 270 + 360, 720 + 540 + 720)
    assert_nfiles(db.objects(protocol=protocol,
                             groups='train'), 1080, 360, 720)
    assert_nfiles(db.objects(protocol=protocol,
                             groups='dev'), 810, 270, 540)
    assert_nfiles(db.objects(protocol=protocol,
                             groups='eval'), 1080, 360, 720)

    for i in range(1, 7):
        protocol = 'Protocol_3_{}'.format(i)
        db.protocol = protocol
        assert_nfiles(db.objects(protocol=protocol), 1500 + 1125 + 300,
                      300 + 225 + 60, 1200 + 900 + 240)
        assert_nfiles(db.objects(protocol=protocol,
                                 groups='train'), 1500, 300, 1200)
        assert_nfiles(db.objects(protocol=protocol,
                                 groups='dev'), 1125, 225, 900)
        assert_nfiles(db.objects(protocol=protocol,
                                 groups='eval'), 300, 60, 240)

        protocol = 'Protocol_4_{}'.format(i)
        db.protocol = protocol
        assert_nfiles(db.objects(protocol=protocol), 600 + 450 + 60,
                      200 + 150 + 20, 400 + 300 + 40)
        assert_nfiles(db.objects(protocol=protocol,
                                 groups='train'), 600, 200, 400)
        assert_nfiles(db.objects(protocol=protocol,
                                 groups='dev'), 450, 150, 300)
        assert_nfiles(db.objects(protocol=protocol,
                                 groups='eval'), 60, 20, 40)


def test_frames():
    protocol = 'Protocol_1'
    db.protocol = protocol
    if db.original_directory is None:
        raise nose.SkipTest(
            "Please configure bob.db.oulunpu (refer to package documentation) "
            "to point to the directory where the database's raw data are. This"
            " way we can test more features of the database interface.")
    padfile = db.all_files()[0][0]
    assert db.number_of_frames(padfile) == 151, db.number_of_frames(padfile)


def test_annotations():
    protocol = 'Protocol_1'
    db.protocol = protocol
    if db.original_directory is None:
        raise nose.SkipTest(
            "Please configure bob.db.oulunpu (refer to package documentation) "
            "to point to the directory where the database's raw data are. This"
            " way we can test more features of the database interface.")
    padfile = db.all_files()[0][0]
    annot = padfile.annotations['0']
    # leye x must be higher than reye x to conform to Bob format
    assert annot['leye'][1] > annot['reye'][1], annot
