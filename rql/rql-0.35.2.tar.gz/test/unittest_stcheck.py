# copyright 2004-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from __future__ import print_function
import six

from rql import RQLHelper, BadRQLQuery, stmts, nodes
from unittest_analyze import DummySchema

if six.PY2:
    import unittest2 as unittest
else:
    import unittest

BAD_QUERIES = (
    'Any X, Y GROUPBY X',

    'Any X WHERE X name Person',

    'Any X WHERE X name nofunction(Y)',

    'Any X WHERE X name nofunction(Y)',

    'Any Y WHERE X name "toto"',

    'Any X WHERE X noattr "toto"',

    'Any X WHERE X is NonExistant',

    'Any UPPER(Y) WHERE X name "toto"',

    'Any C ORDERBY N where C located P, P eid %(x)s',

    'Any X, MAX(COUNT(B)) GROUPBY X WHERE B concerns X;',

    '(Any X WHERE X nom "toto") UNION (Any X,F WHERE X firstname F);',

    'Any X, X/Z WHERE X is Person; WITH Y BEING (Any SUM(X) WHERE X is Person)',

    'Any X WHERE X name "Toto", P is Person',

    "Any X WHERE X eid 0, X eid 1",

    # DISTINCT+ORDERBY tests ###################################################
    # cant sort on Y, B <- work_for X is multivalued
    'DISTINCT Any X ORDERBY Y WHERE B work_for X, B name Y',
    # cant sort on PN, there may be different PF values for the same PN value
    # XXX untrue if PF or PN is marked as unique
    'DISTINCT Any PF ORDERBY PN WHERE P firstname PF, P name PN',
    # cant sort on XN, there may be different PF values for the same PF value
    'DISTINCT Any PF ORDERBY X WHERE P work_for X, P firstname PF',
    'DISTINCT Any PF ORDERBY XN WHERE P work_for X, P firstname PF, X name XN',
)

OK_QUERIES = (
    '(Any N,COUNT(X) GROUPBY N WHERE X name N)'
    ' UNION '
    '(Any N,COUNT(X) GROUPBY N WHERE X firstname N)',

    'DISTINCT Any X, MAX(Y) GROUPBY X WHERE X is Person, Y is Company',

    # DISTINCT+ORDERBY tests ###################################################
    # sorting allowed since order variable reachable from a selected
    # variable with only ?1 cardinality
    'DISTINCT Any P ORDERBY PN WHERE P work_for X, P name PN',
    'DISTINCT Any P ORDERBY XN WHERE P work_for X, X name XN',
    'Any X WHERE X eid > 0, X eid < 42',
    'Any X WHERE X eid 1, X eid < 42',
    'Any X WHERE X number CAST(Int, Y), X name Y',
    'SET X number CAST(Int, Y) WHERE X name Y',
)


class CheckClassTest(unittest.TestCase):
    """check wrong queries are correctly detected"""

    def setUp(self):
        helper = RQLHelper(DummySchema(), None, {'eid': 'uid'})
        self.parse = helper.parse
        self.simplify = helper.simplify

    def _test(self, rql):
        try:
            self.assertRaises(BadRQLQuery, self.parse, rql)
        except Exception:
            print(rql)
            raise

    def test_raise(self):
        for rql in BAD_QUERIES:
            with self.subTest(rql=rql):
                self._test(rql)

    def test_ok(self):
        for rql in OK_QUERIES:
            with self.subTest(rql=rql):
                self.parse(rql)

    def _test_rewrite(self, rql, expected):
        rqlst = self.parse(rql)
        self.simplify(rqlst)
        self.assertEqual(rqlst.as_string(), expected)

    def test_rewrite(self):
        for rql, expected in (
            ('Person X',
             'Any X WHERE X is Person'),
            ("Any X WHERE X eid IN (12), X name 'toto'",
             'Any X WHERE X eid 12, X name "toto"'),
            ('Any X WHERE X work_for Y, Y eid 12',
             'Any X WHERE X work_for 12'),
            ('Any X WHERE Y work_for X, Y eid 12',
             'Any X WHERE 12 work_for X'),
            ('Any X WHERE X work_for Y, Y eid IN (12)',
             'Any X WHERE X work_for 12'),
            ('Any X ORDERBY Y WHERE X work_for Y, Y eid IN (12)',
             'Any X WHERE X work_for 12'),
            ('Any X WHERE X eid 12',
             'Any 12'),
            ('Any X WHERE X is Person, X eid 12',
             'Any 12'),
            ('Any X,Y WHERE X eid 0, Y eid 1, X work_for Y',
             'Any 0,1 WHERE 0 work_for 1'),
            # test symmetric OR rewrite
            ("DISTINCT Any P WHERE P connait S OR S connait P, S name 'chouette'",
             'DISTINCT Any P WHERE P connait S, S name "chouette"'),
            # queries that should not be rewritten
            ('DELETE Person X WHERE X eid 12',
             'DELETE Person X WHERE X eid 12'),
            ('Any X WHERE X work_for Y, Y eid IN (12, 13)',
             'Any X WHERE X work_for Y, Y eid IN(12, 13)'),
            ('Any X WHERE X work_for Y, NOT Y eid 12',
             'Any X WHERE X work_for Y, NOT Y eid 12'),
            ('Any X WHERE NOT X eid 12',
             'Any X WHERE NOT X eid 12'),
            ('Any N WHERE X eid 12, X name N',
             'Any N WHERE X eid 12, X name N'),

            ('Any X WHERE X eid > 12',
             'Any X WHERE X eid > 12'),

            ('Any X WHERE X eid 12, X connait P?, X work_for Y',
             'Any X WHERE X eid 12, X connait P?, X work_for Y'),
            ('Any X WHERE X eid 12, P? connait X',
             'Any X WHERE X eid 12, P? connait X'),

            ("Any X WHERE X firstname 'lulu',"
             "EXISTS (X owned_by U, U name 'lulufanclub' OR U name 'managers');",
             'Any X WHERE X firstname "lulu", '
             'EXISTS(X owned_by U, (U name "lulufanclub") OR (U name "managers"))'),

            ('Any X WHERE X eid 12, EXISTS(X name "hop" OR X work_for Y?)',
             'Any 12 WHERE EXISTS((A name "hop") OR (A work_for Y?), 12 identity A)'),

            ('(Any X WHERE X eid 12) UNION (Any X ORDERBY X WHERE X eid 13)',
             '(Any 12) UNION (Any 13)'),

            ('Any X WITH X BEING (Any X WHERE X eid 12)',
             'Any X WITH X BEING (Any 12)'),

            ('Any X GROUPBY X WHERE X eid 12, X connait Y HAVING COUNT(Y) > 10',
             'Any X GROUPBY X WHERE X eid 12, X connait Y HAVING COUNT(Y) > 10'),

            # A eid 12 can be removed since the type analyzer checked its existence
            ('Any X WHERE A eid 12, X connait Y',
             'Any X WHERE X connait Y'),

            ('Any X WHERE EXISTS(X work_for Y, Y eid 12) OR X eid 12',
             'Any X WHERE (EXISTS(X work_for 12)) OR (X eid 12)'),

            ('Any X WHERE EXISTS(X work_for Y, Y eid IN (12)) OR X eid IN (12)',
             'Any X WHERE (EXISTS(X work_for 12)) OR (X eid 12)'),
        ):
            with self.subTest(rql=rql):
                self._test_rewrite(rql, expected)

    def test_subquery_graphdict(self):
        # test two things:
        # * we get graph information from subquery
        # * we see that we can sort on VCS (eg we have a unique value path from VF to VCD)
        rqlst = self.parse(('DISTINCT Any VF ORDERBY VCD DESC WHERE '
                            'VC work_for S, S name "draft" '
                            'WITH VF, VC, VCD BEING (Any VF, MAX(VC), VCD GROUPBY VF, VCD '
                            '                        WHERE VC connait VF, VC creation_date VCD)'))
        self.assertEqual(rqlst.children[0].vargraph,
                         {'VCD': ['VC'], 'VF': ['VC'], 'S': ['VC'], 'VC': ['S', 'VF', 'VCD'],
                          ('VC', 'S'): 'work_for',
                          ('VC', 'VF'): 'connait',
                          ('VC', 'VCD'): 'creation_date'})
        self.assertEqual(rqlst.children[0].aggregated, set(('VC',)))


class CopyTest(unittest.TestCase):

    def setUp(self):
        helper = RQLHelper(DummySchema(), None, {'eid': 'uid'})
        self.parse = helper.parse
        self.simplify = helper.simplify
        self.annotate = helper.annotate

    def test_copy_exists(self):
        tree = self.parse(
            "Any X WHERE X firstname 'lulu',"
            "EXISTS (X owned_by U, U work_for G, G name 'lulufanclub' OR G name 'managers');"
        )
        self.simplify(tree)
        copy = tree.copy()
        exists = copy.get_nodes(nodes.Exists)[0]
        self.assertTrue(exists.children[0].parent is exists)
        self.assertTrue(exists.parent)

    def test_copy_internals(self):
        root = self.parse('Any X,U WHERE C owned_by U, NOT X owned_by U, X eid 1, C eid 2')
        self.simplify(root)
        stmt = root.children[0]
        self.assertEqual(stmt.defined_vars['U'].valuable_references(), 3)
        copy = stmts.Select()
        copy.append_selected(stmt.selection[0].copy(copy))
        copy.append_selected(stmt.selection[1].copy(copy))
        copy.set_where(stmt.where.copy(copy))
        newroot = stmts.Union()
        newroot.append(copy)
        self.annotate(newroot)
        self.simplify(newroot)
        self.assertEqual(
            newroot.as_string(),
            'Any 1,U WHERE 2 owned_by U, NOT EXISTS(1 owned_by U)',
        )
        self.assertEqual(copy.defined_vars['U'].valuable_references(), 3)


class AnnotateTest(unittest.TestCase):

    def setUp(self):
        helper = RQLHelper(DummySchema(), None, {'eid': 'uid'})
        self.parse = helper.parse

    def test_is_rel_no_scope_1(self):
        """is relation used as type restriction should not affect variable's
        scope, and should not be included in stinfo['relations']
        """
        rqlst = self.parse('Any X WHERE C is Company, EXISTS(X work_for C)').children[0]
        C = rqlst.defined_vars['C']
        self.assertFalse(C.scope is rqlst, C.scope)
        self.assertEqual(len(C.stinfo['relations']), 1)

    def test_is_rel_no_scope_2(self):
        rqlst = self.parse('Any X, ET WHERE C is ET, EXISTS(X work_for C)').children[0]
        C = rqlst.defined_vars['C']
        self.assertTrue(C.scope is rqlst, C.scope)
        self.assertEqual(len(C.stinfo['relations']), 2)

    def test_not_rel_normalization_1(self):
        rqlst = self.parse('Any X WHERE C is Company, NOT X work_for C').children[0]
        self.assertEqual(rqlst.as_string(), 'Any X WHERE C is Company, NOT EXISTS(X work_for C)')
        C = rqlst.defined_vars['C']
        self.assertFalse(C.scope is rqlst, C.scope)

    def test_not_rel_normalization_2(self):
        rqlst = self.parse('Any X, ET WHERE C is ET, NOT X work_for C').children[0]
        self.assertEqual(rqlst.as_string(), 'Any X,ET WHERE C is ET, NOT EXISTS(X work_for C)')
        C = rqlst.defined_vars['C']
        self.assertTrue(C.scope is rqlst, C.scope)

    def test_not_rel_normalization_3(self):
        rqlst = self.parse(
            'Any X WHERE C is Company, X work_for C, NOT C name "World Company"'
        ).children[0]
        self.assertEqual(
            rqlst.as_string(),
            'Any X WHERE C is Company, X work_for C, NOT C name "World Company"',
        )
        C = rqlst.defined_vars['C']
        self.assertTrue(C.scope is rqlst, C.scope)

    def test_not_rel_normalization_4(self):
        rqlst = self.parse(
            'Any X WHERE C is Company, NOT (X work_for C, C name "World Company")'
        ).children[0]
        self.assertEqual(
            rqlst.as_string(),
            'Any X WHERE C is Company, NOT EXISTS(X work_for C, C name "World Company")',
        )
        C = rqlst.defined_vars['C']
        self.assertFalse(C.scope is rqlst, C.scope)

    def test_not_rel_normalization_5(self):
        rqlst = self.parse(
            'Any X WHERE X work_for C, '
            'EXISTS(C identity D, NOT Y work_for D, D name "World Company")'
        ).children[0]
        self.assertEqual(
            rqlst.as_string(),
            'Any X WHERE X work_for C, '
            'EXISTS(C identity D, NOT EXISTS(Y work_for D), D name "World Company")',
        )
        D = rqlst.defined_vars['D']
        D = rqlst.defined_vars['D']
        self.assertFalse(D.scope is rqlst, D.scope)
        self.assertTrue(D.scope.parent.scope is rqlst, D.scope.parent.scope)

    def test_subquery_annotation_1(self):
        rqlst = self.parse(
            'Any X WITH X BEING (Any X WHERE C is Company, EXISTS(X work_for C))'
        ).children[0]
        C = rqlst.with_[0].query.children[0].defined_vars['C']
        self.assertFalse(C.scope is rqlst, C.scope)
        self.assertEqual(len(C.stinfo['relations']), 1)

    def test_subquery_annotation_2(self):
        rqlst = self.parse(
            'Any X,ET WITH X,ET BEING (Any X, ET WHERE C is ET, EXISTS(X work_for C))'
        ).children[0]
        C = rqlst.with_[0].query.children[0].defined_vars['C']
        self.assertTrue(C.scope is rqlst.with_[0].query.children[0], C.scope)
        self.assertEqual(len(C.stinfo['relations']), 2)
        X = rqlst.get_variable('X')
        self.assertTrue(X.scope is rqlst, X.scope)

    def test_no_attr_var_if_uid_rel(self):
        with self.assertRaises(BadRQLQuery) as cm:
            self.parse('Any X, Y WHERE X work_for Z, Y work_for Z, X eid > Y')
        self.assertEqual(
            str(cm.exception),
            'variable Y should not be used as rhs of attribute relation X eid > Y',
        )

    def test_no_uid_rel_if_not_constant(self):
        rqlst = self.parse('Any X,EID WHERE X eid EID').children[0]
        self.assertEqual(rqlst.defined_vars['X'].stinfo['uidrel'], None)
        rqlst = self.parse('Any X WHERE X eid IN (1,2,3)').children[0]
        self.assertTrue(rqlst.defined_vars['X'].stinfo['uidrel'])


if __name__ == '__main__':
    unittest.main()
