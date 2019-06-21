# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test user variables
# :Created:   gio 12 mag 2016 12:32:39 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import fixtures


class TestScriptWithVariables(fixtures.BaseTestCase):
    TEST_TXT = """
    Variables Test
    ==============

    .. patchdb:script:: Create key-value table

       create table keyvalue (
         id integer primary key,
         val varchar(15)
       )

    .. patchdb:script:: Insert first pair
       :depends: Create key-value table

       INSERT INTO keyvalue (id, val) VALUES ({{key1}}, '{{value1}}')
    """

    def test(self):
        output = self.patchdb()
        self.assertIn('Undefined variable "key1"', output)

        output = self.patchdb('--define', 'key1=1',
                              '--define', 'value1=value',
                              '--define', 'this_is_unused=true')
        self.assertIn('Done, applied 1 script', output)
        c, _ = self.get_connection_and_base_exception()
        try:
            q = c.cursor()
            q.execute('SELECT id, val FROM keyvalue')
            r = q.fetchone()
            self.assertEqual(r[0], 1)
            self.assertEqual(r[1], 'value')
        finally:
            c.close()

    def test_invalid(self):
        output = self.patchdb('--define', 'dummy')
        self.assertIn('Invalid variable definition', output)

    def test_invalid_name(self):
        output = self.patchdb('--define', '=1')
        self.assertIn('Invalid variable name', output)

        output = self.patchdb('--define', 'a b=1')
        self.assertIn('Invalid variable name', output)

        output = self.patchdb('--define', '1ab=1')
        self.assertIn('Invalid variable name', output)

    def test_invalid_value(self):
        output = self.patchdb('--define', 'a=$FOO')
        self.assertIn('Invalid variable value', output)

        output = self.patchdb('--define', "a='; drop")
        self.assertIn('Invalid variable value', output)
