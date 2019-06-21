# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Content in external file test
# :Created:   mar 23 feb 2016 11:40:22 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import fixtures


SQL = """
create table sl_test (
  id integer primary key,
  value varchar(10)
)
"""


class TestExternalFile(fixtures.BaseTestCase):
    TEST_TXT = """
    Basic Test
    ==========

    .. patchdb:script:: Create first table
       :file: test.sql
    """

    OTHER_FILES = (('test.sql', SQL),)


class TestIncludeFile(fixtures.BaseTestCase):
    TEST_TXT = """
    Basic Test
    ==========

    .. patchdb:script:: Create first tables

       ;;INCLUDE: test.sql
       ;;
       insert into sl_test (value) values ('lele')
    """

    OTHER_FILES = (('test.sql', SQL),)

    def test(self):
        super(TestIncludeFile, self).test()
        c, _ = self.get_connection_and_base_exception()
        try:
            q = c.cursor()
            q.execute("select * from sl_test where value = 'lele'")
            r = q.fetchone()
            self.assertTrue(r)
        finally:
            c.close()
