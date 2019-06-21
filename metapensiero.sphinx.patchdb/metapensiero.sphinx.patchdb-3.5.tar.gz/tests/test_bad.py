# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Broken scripts test
# :Created:   mar 23 feb 2016 11:05:47 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2018, 2019 Lele Gaifax
#

import fixtures


class AssertBuildError(object):
    def setUp(self):
        self.assertIsNotNone(self.build_error)


class TestBadDependency(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Bad dep test
    ============

    .. patchdb:script:: Create first table
       :depends: Not existing script

       create table sl_test (
         id integer primary key
       )
    """

    def test(self):
        self.assertIn('PatchDB error:', self.build_error)
        self.assertIn('references an unknown script', self.build_error)
        self.assertIn('not existing script', self.build_error)


class TestBadDependency2(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Bad dep test
    ============

    .. patchdb:script:: Create first table
       :depends:
          - Not, existing, script

       create table sl_test (
         id integer primary key
       )
    """

    def test(self):
        self.assertIn('PatchDB error:', self.build_error)
        self.assertIn('references an unknown script', self.build_error)
        self.assertIn('not, existing, script', self.build_error)


class TestBadReference(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Bad ref test
    ============

    .. patchdb:script:: Create first table

       create table sl_test (
         id integer primary key
       )

    See :patchdb:script:`Foo`.
    """

    def test(self):
        self.assertIn('Reference to an unknown script', self.build_error)
        self.assertIn('foo', self.build_error)


class TestCircularDependency(fixtures.BaseTestCase):
    TEST_TXT = """
    Circular dep test
    =================

    .. patchdb:script:: Create first table
       :depends: Create second table

       create table test1 (
         id integer primary key
       )

    .. patchdb:script:: Create second table
       :depends: Create first table

       create table test2 (
         id integer primary key
       )
    """

    def test(self):
        output = self.patchdb()
        self.assertIn('digraph cycle', output)


class TestBadSQL(fixtures.BaseTestCase):
    TEST_TXT = """
    Bad SQL test
    ============

    .. patchdb:script:: Create first table

       crate table sl_test (
         id integer primary key
       )
    """

    def test(self):
        output = self.patchdb()
        self.assertIn(' generated an error: ', output)


class TestDuplicatedPatchID(AssertBuildError, fixtures.BaseTestCase):
    SCRIPT = """
    .. patchdb:script:: Create first table

       create table test1 (
         id integer primary key
       )

    """

    TEST_TXT = """
    Duplicated script test
    ======================

    """ + SCRIPT + SCRIPT

    RETEST_TXT = """
    Fixed test
    ==========

    """ + SCRIPT

    def test(self):
        # Let try to rebuild removing the duplicated script, then reprocessing
        # again with a little variation
        self.assertIsNone(self.build({'test.txt': self.RETEST_TXT}))
        self.assertIsNone(self.build({'test.txt': self.RETEST_TXT + ".. comment"}))
        self.assertIsNone(self.build({'test.txt': self.RETEST_TXT + "oh comment"}))


class TestDependsWithSpuriousComma(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Bad title
    =========

    .. patchdb:script:: Second
       :depends: First,
    """

    def test(self):
        self.assertIn('bad option', self.build_error)


class TestTitleWithAt(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Bad title
    =========

    .. patchdb:script:: Add lele@example.com
    """

    def test(self):
        self.assertIn('ID contains "@"', self.build_error)


class TestBadRevision(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Bad title
    =========

    .. patchdb:script:: First
       :revision: 0
    """

    def test(self):
        self.assertIn('Invalid revision', self.build_error)


class TestTitleWithContentAndFile(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Bad title
    =========

    .. patchdb:script:: Something
       :file: foo.sql

       create table sl_test (
         id integer primary key
       )
    """

    def test(self):
        self.assertIn('content and :file: option', self.build_error)


class TestPlaceholderWithBrings(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Invalid placeholder
    ===================

    .. patchdb:script:: Create table a
       :description: Place holder
       :brings: Invalid
    """

    def test(self):
        self.assertIn('Placeholder script cannot bring anything', self.build_error)


FOO = """
;;INCLUDE: foo.txt
"""


class TestCircularInclude(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    Circular include test
    =====================

    .. patchdb:script:: Include test

       ;;INCLUDE: foo.txt
    """

    OTHER_FILES = (('foo.txt', FOO),)

    def test(self):
        self.assertIn('circular include of file', self.build_error)
        self.assertIn('foo.txt', self.build_error)


FIRST_REV = """
First revision
==============

.. patchdb:script:: Create first table

   create table test (
     id integer primary key
   )
"""

SECOND_REV = """
Same revision, different script
===============================

.. patchdb:script:: Create first table

   create table test (
     id integer primary key,
     thevalue integer
   )
"""


class TestChangedScriptSameRevision(fixtures.BaseTestCase):
    TEST_TXT = FIRST_REV

    def test_2(self):
        output = self.build({'test.txt': SECOND_REV})
        assert ('The script "create first table@1" has been modified,'
                ' but the revision did not' in output)


class TestPatchNonExistingBrings(AssertBuildError, fixtures.BaseTestCase):
    TEST_TXT = """
    .. patchdb:script:: Update old_table
       :depends: Create old_table@1
       :brings: Create old_table@2

       alter table old_table add column value varchar(10)
    """

    def test(self):
        self.assertIn('brings an unknown script "create old_table"', self.build_error)
