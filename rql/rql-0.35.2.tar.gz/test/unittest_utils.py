# copyright 2004-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from six.moves import range

from logilab.common.testlib import TestCase, unittest_main

from rql import utils, nodes, parse


class Visitor(utils.RQLVisitorHandler):
    def visit(self, node):
        node.accept(self)
        for c in node.children:
            self.visit(c)


class RQLHandlerClassTest(TestCase):
    """tests that the default handler implements a method for each possible node
    """

    def setUp(self):
        self.visitor = Visitor()

    def test_methods_1(self):
        tree = parse('Any X where X name "turlututu", X born <= TODAY - 2 OR X born = NULL', {})
        self.visitor.visit(tree)

    def test_methods_2(self):
        tree = parse('Insert Person X', {})
        self.visitor.visit(tree)

    def test_methods_3(self):
        tree = parse(
            'Set X nom "yo" WHERE X is Person',
            {'Person': nodes.Constant('Person', 'etype')},
        )
        self.visitor.visit(tree)

    def test_methods_4(self):
        tree = parse('Delete Person X', {})
        self.visitor.visit(tree)


class RQLVarMakerTC(TestCase):

    def test_rqlvar_maker(self):
        varlist = list(utils.rqlvar_maker(27))
        self.assertEqual(varlist, list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['AA'])
        varlist = list(utils.rqlvar_maker(27*26+1))
        self.assertEqual(varlist[-2], 'ZZ')
        self.assertEqual(varlist[-1], 'AAA')

    def test_rqlvar_maker_dontstop(self):
        varlist = utils.rqlvar_maker()
        self.assertEqual(next(varlist), 'A')
        self.assertEqual(next(varlist), 'B')
        for i in range(24):
            next(varlist)
        self.assertEqual(next(varlist), 'AA')
        self.assertEqual(next(varlist), 'AB')


if __name__ == '__main__':
    unittest_main()
