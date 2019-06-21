#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Thu May 24 10:41:42 CEST 2012


import nose.tools
import bob.pad.base
from bob.bio.base.test.utils import db_available


@db_available('verafinger')
def test_verafinger():
  module = bob.bio.base.load_resource('verafinger-pad', 'config',
      preferred_package='bob.pad.vein')
  try:
    # counts have already been tested on the low-level database
    # here, we just check we can access it through the PadDatabase interface
    groups = ('train', 'dev', 'eval')
    nose.tools.eq_(len(module.database.objects(groups=groups)), 1760)
  except IOError as e:
    raise SkipTest("The database could not queried; probably the db.sql3 file is missing. Here is the error: '%s'" % e)
