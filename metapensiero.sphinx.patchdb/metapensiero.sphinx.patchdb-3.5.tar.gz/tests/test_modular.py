# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test modular composition
# :Created:   gio 25 feb 2016 09:46:36 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import os
import os.path
import fixtures


MODULE_A = """
Module A
========

.. patchdb:script:: Create table a

   create table a (
     id integer not null primary key,
     value integer
   )
"""


MODULE_B = """
Module B
========

.. patchdb:script:: Create table a
   :description: Place holder

.. patchdb:script:: Create unique index on value
   :depends: Create table a

   create unique index on_value on a (value)
"""


MODULE_C = """
Module C
========

.. patchdb:script:: Create table a
   :description: Duplicated script

   create table a (
     id integer not null primary key,
     value integer
   )
"""


class TestModularModuleBWithoutA(fixtures.BaseTestCase):
    TEST_TXT = MODULE_B

    def test(self):
        output = self.patchdb()
        self.assertIn('"create table a@1" has not been applied yet',
                      output)


class TestModular(fixtures.BaseTestCase):
    TEST_TXT = MODULE_A

    def test_1(self):
        self.build({'test.txt': MODULE_B})
        output = self.patchdb()
        self.assertIn('Done, applied 1 script', output)


class TestModularA_plus_B(fixtures.BaseTestCase):
    TEST_TXT = MODULE_A

    def test(self):
        s = self.sphinx
        os.rename(os.path.join(s.directory, s.PATCHDB_SHELVE),
                  os.path.join(s.directory, 'patchdb-module-a.json'))
        self.build({'test.txt': MODULE_B})
        output = self.patchdb('patchdb-module-a.json')
        self.assertIn('Done, applied 2 script', output)


class TestModularA_plus_C(fixtures.BaseTestCase):
    TEST_TXT = MODULE_A

    def test(self):
        s = self.sphinx
        os.rename(os.path.join(s.directory, s.PATCHDB_SHELVE),
                  os.path.join(s.directory, 'patchdb-module-a.json'))
        self.build({'test.txt': MODULE_C})
        output = self.patchdb('patchdb-module-a.json')
        self.assertIn('Duplicated script "create table a@1":'
                      ' present in patchdb-module-a.json and %s'
                      % s.PATCHDB_SHELVE, output)
