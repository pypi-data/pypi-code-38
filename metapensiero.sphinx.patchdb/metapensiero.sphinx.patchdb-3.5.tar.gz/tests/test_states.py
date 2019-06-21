# -*- coding: utf-8 -*-
# :Project:   PatchDB -- States related tests
# :Created:   ven 15 apr 2016 12:08:46 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import hashlib
import os

import test_revisions
import test_sql


THIRD_REV = """
Multiple revisions
==================

.. patchdb:script:: Create first table
   :revision: 2

   create table test (
     id integer primary key,
     thevalue integer
   )

.. patchdb:script:: Update first table
   :depends: Create first table@1
   :brings: Create first table@2

   alter table test add thevalue integer

.. patchdb:script:: Insert record in first table
   :depends: Create first table@2

   insert into test values (1, 42)

.. patchdb:script:: Insert record in first table, another one
   :depends:
      - Insert record in first table

   insert into test values (2, 84)
"""


REV1_HASH = hashlib.md5(b'create first table@1').hexdigest()
REV2_HASH = hashlib.md5(b'create first table@2update first table@1').hexdigest()


class TestStates(test_sql.TestSingleSQLScript):
    def test(self):
        bckdir = os.path.join(self.sphinx.directory, 'bcks')
        output = self.patchdb('-b', bckdir)
        self.assertIn('Done, applied 1 script', output)
        output = self.patchdb('-b', bckdir)
        self.assertIn('Done, applied 0 scripts', output)
        output = self.pdbstates('list', bckdir)
        self.assertIn(REV1_HASH + ' <create first table@1>\n', output)
        output = self.pdbstates('list', '--tsv', bckdir)
        self.assertIn(REV1_HASH, (line.split('\t')[1]
                                  for line in output.splitlines()
                                  if line))


class TestRestoreState(test_revisions.TestMultipleRevIncremental):
    def test_3(self):
        output = self.pdbstates('list')
        self.assertIn(REV1_HASH + ' <create first table@1>\n', output)
        output = self.pdbstates('restore', REV1_HASH)
        self.assertIn('Restored ', output)
        self.assertIn(' from ', output)
        self.assertIn(REV1_HASH, output)

        self.test_1()
        self.test_2()

    def test_4(self):
        self.build({'test.txt': THIRD_REV})
        output = self.patchdb('--debug')
        self.assertIn('Done, applied 2 scripts', output)
        output = self.pdbstates('list')
        self.assertIn(REV1_HASH + ' <create first table@1>\n', output)
        self.assertIn(REV2_HASH + ' <update first table@1>\n', output)

    def test_5(self):
        output = self.pdbstates('clean', '-k', '1', '--dry-run')
        self.assertIn('Would remove ', output)
        output = self.pdbstates('clean', '-k', '1')
        self.assertIn('Removed ', output)
        self.assertIn('Kept most recent 1 snapshot', output)
