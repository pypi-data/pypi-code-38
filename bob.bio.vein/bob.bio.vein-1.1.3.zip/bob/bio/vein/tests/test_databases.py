#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Thu May 24 10:41:42 CEST 2012

from nose.plugins.skip import SkipTest

import bob.bio.base
from bob.bio.base.test.utils import db_available
from bob.bio.base.test.test_database_implementations import check_database


@db_available('utfvp')
def test_utfvp():
    module = bob.bio.base.load_resource('utfvp', 'config',
        preferred_package='bob.bio.vein')
    try:
        check_database(module.database, protocol='nomLeftIndex', groups=('dev',
          'eval'))
    except IOError as e:
        raise SkipTest(
            "The database could not queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)


@db_available('verafinger')
def test_verafinger():
    module = bob.bio.base.load_resource('verafinger', 'config',
        preferred_package='bob.bio.vein')
    try:
        check_database(module.database, protocol='Fifty', groups=('dev',
          'eval'))
    except IOError as e:
        raise SkipTest(
            "The database could not queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)


@db_available('fv3d')
def test_fv3d():
    module = bob.bio.base.load_resource('fv3d', 'config',
        preferred_package='bob.bio.vein')
    try:
        check_database(module.database, protocol='central', groups=('dev',))
    except IOError as e:
        raise SkipTest(
            "The database could not queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)


@db_available('putvein')
def test_putvein():
    module = bob.bio.base.load_resource('putvein', 'config',
        preferred_package='bob.bio.vein')
    try:
        check_database(module.database, protocol='wrist-LR_1', groups=('dev',))
    except IOError as e:
        raise SkipTest(
            "The database could not queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)
