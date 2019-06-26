# copyright 2004-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of rql.
#
# rql is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# rql is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with rql. If not, see <http://www.gnu.org/licenses/>.

from logilab.common.testlib import TestCase, unittest_main

from rql import parse
from rql.nodes import Exists


class RQLUndoTestCase(TestCase):

    def test_selected(self):
        rqlst = parse('Person X')
        orig = rqlst.as_string()
        rqlst.save_state()
        select = rqlst.children[0]
        var = select.make_variable()
        select.remove_selected(select.selection[0])
        select.add_selected(var)
        # check operations
        self.assertEqual(rqlst.as_string(), 'Any %s WHERE X is Person' % var.name)
        # check references before recovering
        rqlst.check_references()
        rqlst.recover()
        # check equivalence after recovering
        self.assertEqual(rqlst.as_string(), orig)
        # check references after recovering
        rqlst.check_references()

    def test_selected3(self):
        rqlst = parse('Any lower(N) WHERE X is Person, X name N')
        orig = rqlst.as_string()
        rqlst.save_state()
        select = rqlst.children[0]
        var = select.make_variable()
        select.remove_selected(select.selection[0])
        select.add_selected(var)
        # check operations
        self.assertEqual(rqlst.as_string(), 'Any %s WHERE X is Person, X name N' % var.name)
        # check references before recovering
        rqlst.check_references()
        rqlst.recover()
        # check equivalence after recovering
        self.assertEqual(rqlst.as_string(), orig)
        # check references after recovering
        rqlst.check_references()

    def test_undefine_1(self):
        rqlst = parse('Person X, Y WHERE X travaille_pour Y')
        orig = rqlst.as_string()
        rqlst.save_state()
        rqlst.children[0].undefine_variable(rqlst.children[0].defined_vars['Y'])
        # check operations
        self.assertEqual(rqlst.as_string(), 'Any X WHERE X is Person')
        # check references before recovering
        rqlst.check_references()
        rqlst.recover()
        # check equivalence
        self.assertEqual(rqlst.as_string(), orig)
        # check references after recovering
        rqlst.check_references()

    def test_undefine_2(self):
        rqlst = parse('Person X')
        orig = rqlst.as_string()
        rqlst.save_state()
        rqlst.children[0].undefine_variable(rqlst.children[0].defined_vars['X'])
        var = rqlst.children[0].make_variable()
        rqlst.children[0].add_selected(var)
        # check operations
        self.assertEqual(rqlst.as_string(), 'Any A')
        # check references before recovering
        rqlst.check_references()
        rqlst.recover()
        # check equivalence
        self.assertEqual(rqlst.as_string(), orig)
        # check references after recovering
        rqlst.check_references()

    def test_remove_exists(self):
        rql_request = ('Any U,COUNT(P) GROUPBY U WHERE U is CWUser, '
                       'P? patch_reviewer U, EXISTS(P in_state S AND '
                       'S name "pouet")')
        rqlst = parse(rql_request).children[0]
        orig = rqlst.as_string()
        rqlst.save_state()
        n = [r for r in rqlst.get_nodes(Exists)][0].query
        rqlst.remove_node(n)
        # check operations
        self.assertEqual(
            rqlst.as_string(),
            'Any U,COUNT(P) GROUPBY U WHERE U is CWUser, P? patch_reviewer U'
        )
        # check references before recovering
        rqlst.check_references()
        rqlst.recover()
        # check equivalence
        self.assertEqual(rqlst.as_string(), orig)
        # check references after recovering
        rqlst.check_references()


if __name__ == '__main__':
    unittest_main()
