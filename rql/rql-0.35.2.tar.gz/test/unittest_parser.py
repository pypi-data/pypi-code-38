# -*- coding: iso-8859-1 -*-
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

from six import text_type, PY2

from yapps.runtime import print_error, SyntaxError

from rql.parser import Hercule, HerculeScanner
from rql import BadRQLQuery, RQLSyntaxError, nodes
from rql import parse

if PY2:
    import unittest2 as unittest
else:
    import unittest


BAD_SYNTAX_QUERIES = (
    'ANY X WHERE X name Nulll;',
    'ANY X WHERE (X name NULL or X name "chouette";',
    'INSERT Person X : X name "bidule" or X name "chouette";',
    'Any X WHERE "YO" related "UPI";',
    # FIXME: incorrect because X/Y are not bound, not a syntax error
    "Personne P WHERE OFFSET 200;",

    (
        'Any X GROUPBY X ORDERBY X WHERE X nom "toto" UNION Any X GROUPBY X '
        'ORDERBY X WHERE X firstname "toto";'
    ),
    (
        '(Any X GROUPBY X WHERE X nom "toto") UNION '
        '(Any X GROUPBY X WHERE X firstname "toto") ORDERBY X;'
    ),

    'Any X, X/Y FROM (Any SUM(X) WHERE X is Person) WHERE X is Person;',  # missing AS for subquery

    'Any X, X/Y FROM (Any X WHERE X is) WHERE X is Person;',  # missing AS for subquery

    )

BAD_QUERIES = (
    'Person Marcou;',
    'INSERT Any X : X name "bidule";',
    'DELETE Any X;',
    'Person Marcou',
    'INSERT Person X : Y name "bidule" WHERE X work_for Y;',
    'Any X LIMIT -1;',
    'Any X OFFSET -1;',
    'Any X ORDERBY Y;',
    'Any N,COUNT(X) GROUPBY N '
    ' HAVING COUNT(X)>1 '
    ' WITH X,N BEING (Any X, N WHERE X name N, X is State UNION '
    '                 Any X, N WHERE X name N, X is Transition);',

    'Machin 12',
    )

# FIXME: this shoud be generated from the spec file
SPEC_QUERIES = (
    'Any X WHERE X eid 53;',
    'Any X WHERE X eid -53;',
    ("Document X WHERE X occurence_of F, F class C, C name 'Bande dessinée', "
     "X owned_by U, U login 'syt', X available true;"),
    (u"Document X WHERE X occurence_of F, F class C, C name 'Bande dessinée', "
     "X owned_by U, U login 'syt', X available true;"),
    ("Personne P WHERE P travaille_pour S, S nom 'Eurocopter', P interesse_par T, "
     "T nom 'formation';"),
    "Note N WHERE N ecrit_le D, D day > (today -10), N ecrit_par P, P nom 'jphc' or P nom 'ocy';",
    "Personne P WHERE (P interesse_par T, T nom 'formation') or (P ville 'Paris');",
    "Any X ORDERBY S DESC WHERE X is Person, X firstname 'Anne', X surname S;",
    # limit / offset
    "Personne P LIMIT 100 WHERE P nom N;",
    "Personne P LIMIT 100 OFFSET 200 WHERE P nom N;",
    'Any X OFFSET 6 WHERE X is Person;',
    # optional relation support (left|right outer join)
    'Any X,Y,A WHERE X? concerns Y, Y title A;',
    'Any X,Y,A WHERE X concerns Y?, Y title A;',
    'Any X,Y,A WHERE X? concerns Y?, Y title A;',
    # data modification query
    "INSERT Personne X: X nom 'bidule';",
    "INSERT Personne X, Personne Y: X nom 'bidule', Y nom 'chouette', X ami Y;",
    "INSERT Person X: X nom 'bidule', X ami Y WHERE Y nom 'chouette';",
    "SET X nom 'toto', X prenom 'original' WHERE X is Person, X nom 'bidule';",
    "SET X know Y WHERE X ami Y;",
    "SET X value -Y WHERE X value Y;",
    "DELETE Person X WHERE X nom 'toto';",
    "DELETE X ami Y WHERE X is Person, X nom 'toto';",

    # some additional cases
    'INSERT Person X : X name "bidule", Y workfor X WHERE Y name "logilab";',
    (
        'DISTINCT Any X,A,B,C,D ORDERBY A ASC WHERE P eid 41, X concerns P, '
        'P is Project, X is Story,X title A,X state B,X priority C,X cost D;'
    ),
    'Any X WHERE X has_text "2.12.0";',
    'Any X,A,B,C,D ORDERBY A ASC WHERE X concerns 41,X title A,X state B,X priority C,X cost D;',

    "Any X, COUNT(B) GROUPBY X ORDERBY 1 where B concerns X;",

    "Any X ORDERBY RANDOM();",
    "Any X ORDERBY F(1, 2);",

    "Any X, COUNT(B) GROUPBY X ORDERBY 1 WHERE B concerns X HAVING COUNT(B) > 2;",

    'Any X, MAX(COUNT(B)) GROUPBY X WHERE B concerns X;',  # syntaxically correct

    'Any X WHERE X eid > 12;',
    'DELETE Any X WHERE X eid > 12;',

    '(Any X WHERE X eid > 12) UNION (Any X WHERE X eid < 23);',
    '(Any X WHERE X nom "toto") UNION (Any X WHERE X firstname "toto");',
    (
        '(Any X GROUPBY X WHERE X nom "toto") UNION '
        '(Any X GROUPBY X ORDERBY X WHERE X firstname "toto");'
    ),

    'Any X, X/Y WHERE X is Person WITH Y BEING (Any SUM(X) WHERE X is Person);',
    'Any Y, COUNT(X) GROUPBY Y WHERE X bla Y WITH Y BEING ((Person X) UNION (Document X));',

    'Any T2, COUNT(T1)'
    ' GROUPBY T1'
    ' ORDERBY 2 DESC, T2;'
    ' WITH T1,T2 BEING ('
    '      (Any X,N WHERE X name N, X transition_of E, E name %(name)s)'
    '       UNION '
    '      (Any X,N WHERE X name N, X state_of E, E name %(name)s));',


    'Any T2'
    ' GROUPBY T2'
    ' WHERE T1 relation T2'
    ' HAVING COUNT(T1) IN (1,2);',

    'Any T2'
    ' GROUPBY T2'
    ' WHERE T1 relation T2'
    ' HAVING COUNT(T1) IN (1,2) OR COUNT(T1) IN (3,4);',

    'Any T2'
    ' GROUPBY T2'
    ' WHERE T1 relation T2'
    ' HAVING 1 < COUNT(T1) OR COUNT(T1) IN (3,4);',

    'Any T2'
    ' GROUPBY T2'
    ' WHERE T1 relation T2'
    ' HAVING (COUNT(T1) IN (1,2)) OR (COUNT(T1) IN (3,4));',

    'Any T2'
    ' GROUPBY T2'
    ' WHERE T1 relation T2'
    ' HAVING (1 < COUNT(T1) OR COUNT(T1) IN (3,4));',

    'Any T2'
    ' GROUPBY T2'
    ' WHERE T1 relation T2'
    ' HAVING 1+2 < COUNT(T1);',

    'Any X,Y,A ORDERBY Y '
    'WHERE A done_for Y, X split_into Y, A diem D '
    'HAVING MIN(D) < "2010-07-01", MAX(D) >= "2010-07-01";',

    'Any YEAR(XD),COUNT(X) GROUPBY YEAR(XD) ORDERBY YEAR(XD) WHERE X date XD;',
    'Any YEAR(XD),COUNT(X) GROUPBY 1 ORDERBY 1 WHERE X date XD;',

    'Any -1.0;',

    'Any U,G WHERE U login UL, G name GL, G is CWGroup HAVING UPPER(UL)=UPPER(GL)?;',

    'Any U,G WHERE U login UL, G name GL, G is CWGroup HAVING UPPER(UL)?=UPPER(GL);',
    )


class ParserHercule(unittest.TestCase):
    _syntaxerr = SyntaxError

    def parse(self, string, print_errors=False):
        try:
            parser = Hercule(HerculeScanner(string))
            return parser.goal()
        except SyntaxError as ex:
            if print_errors:
                # try to get error message from yapps
                print_error(ex, parser._scanner)
                print
            raise
        except Exception as ex:
            if print_errors:
                print(string, ex)
            raise

    def test_unicode_constant(self):
        tree = self.parse(u"Any X WHERE X name 'Ångström';")
        base = tree.children[0].where
        comparison = base.children[1]
        self.assertIsInstance(comparison, nodes.Comparison)
        rhs = comparison.children[0]
        self.assertIsInstance(rhs.value, text_type)

    def test_precedence_1(self):
        tree = self.parse("Any X WHERE X firstname 'lulu' AND X name 'toto' OR X name 'tutu';")
        base = tree.children[0].where
        self.assertEqual(isinstance(base, nodes.Or), 1)
        self.assertEqual(isinstance(base.children[0], nodes.And), 1)
        self.assertEqual(isinstance(base.children[1], nodes.Relation), 1)
        self.assertEqual(
            str(tree),
            'Any X WHERE (X firstname "lulu", X name "toto") OR (X name "tutu")',
        )

    def test_precedence_2(self):
        tree = self.parse("Any X WHERE X firstname 'lulu', X name 'toto' OR X name 'tutu';")
        base = tree.children[0].where
        self.assertEqual(isinstance(base, nodes.And), 1)
        self.assertEqual(isinstance(base.children[0], nodes.Relation), 1)
        self.assertEqual(isinstance(base.children[1], nodes.Or), 1)
        self.assertEqual(
            str(tree),
            'Any X WHERE X firstname "lulu", (X name "toto") OR (X name "tutu")',
        )

    def test_precedence_3(self):
        tree = self.parse("Any X WHERE X firstname 'lulu' AND (X name 'toto' or X name 'tutu');")
        base = tree.children[0].where
        self.assertEqual(isinstance(base, nodes.And), 1)
        self.assertEqual(isinstance(base.children[0], nodes.Relation), 1)
        self.assertEqual(isinstance(base.children[1], nodes.Or), 1)
        self.assertEqual(
            str(tree),
            'Any X WHERE X firstname "lulu", (X name "toto") OR (X name "tutu")',
        )

    def test_precedence_4(self):
        tree = self.parse("Any X WHERE X firstname 'lulu' OR X name 'toto' AND X name 'tutu';")
        base = tree.children[0].where
        self.assertEqual(isinstance(base, nodes.Or), 1)
        self.assertEqual(isinstance(base.children[0], nodes.Relation), 1)
        self.assertEqual(isinstance(base.children[1], nodes.And), 1)

    def test_not_precedence_0(self):
        tree = self.parse("Any X WHERE NOT X firstname 'lulu', X name 'toto';")
        self.assertEqual(str(tree), 'Any X WHERE NOT X firstname "lulu", X name "toto"')

    def test_not_precedence_1(self):
        tree = self.parse("Any X WHERE NOT X firstname 'lulu' AND X name 'toto';")
        self.assertEqual(str(tree), 'Any X WHERE NOT X firstname "lulu", X name "toto"')

    def test_not_precedence_2(self):
        tree = self.parse("Any X WHERE NOT X firstname 'lulu' OR X name 'toto';")
        self.assertEqual(str(tree), 'Any X WHERE (NOT X firstname "lulu") OR (X name "toto")')

    def test_string_1(self):
        tree = self.parse(r"Any X WHERE X firstname 'lu\"lu';")
        const = tree.children[0].where.children[1].children[0]
        self.assertEqual(const.value, r'lu\"lu')

    def test_string_2(self):
        tree = self.parse(r"Any X WHERE X firstname 'lu\'lu';")
        const = tree.children[0].where.children[1].children[0]
        self.assertEqual(const.value, 'lu\'lu')

    def test_string_3(self):
        tree = self.parse(r'Any X WHERE X firstname "lu\'lu";')
        const = tree.children[0].where.children[1].children[0]
        self.assertEqual(const.value, r"lu\'lu")

    def test_string_4(self):
        tree = self.parse(r'Any X WHERE X firstname "lu\"lu";')
        const = tree.children[0].where.children[1].children[0]
        self.assertEqual(const.value, "lu\"lu")

    def test_math_1(self):
        tree = self.parse(r'Any X WHERE X date (TODAY + 1);')
        math = tree.children[0].where.children[1].children[0]
        self.assertIsInstance(math, nodes.MathExpression)
        self.assertEqual(math.operator, '+')

    def test_math_2(self):
        tree = self.parse(r'Any X WHERE X date (TODAY + 1 * 2);')
        math = tree.children[0].where.children[1].children[0]
        self.assertIsInstance(math, nodes.MathExpression)
        self.assertEqual(math.operator, '+')
        math2 = math.children[1]
        self.assertIsInstance(math2, nodes.MathExpression)
        self.assertEqual(math2.operator, '*')

    def test_math_3(self):
        tree = self.parse(r'Any X WHERE X date (TODAY + 1) * 2;')
        math = tree.children[0].where.children[1].children[0]
        self.assertIsInstance(math, nodes.MathExpression)
        self.assertEqual(math.operator, '*')
        math2 = math.children[0]
        self.assertIsInstance(math2, nodes.MathExpression)
        self.assertEqual(math2.operator, '+')

    def test_substitute(self):
        tree = self.parse("Any X WHERE X firstname %(firstname)s;")
        cste = tree.children[0].where.children[1].children[0]
        self.assertIsInstance(cste, nodes.Constant)
        self.assertEqual(cste.type, 'Substitute')
        self.assertEqual(cste.value, 'firstname')

    def test_optional_relation(self):
        tree = self.parse(r'Any X WHERE X related Y;')
        related = tree.children[0].where
        self.assertEqual(related.optional, None)
        tree = self.parse(r'Any X WHERE X? related Y;')
        related = tree.children[0].where
        self.assertEqual(related.optional, 'left')
        tree = self.parse(r'Any X WHERE X related Y?;')
        related = tree.children[0].where
        self.assertEqual(related.optional, 'right')
        tree = self.parse(r'Any X WHERE X? related Y?;')
        related = tree.children[0].where
        self.assertEqual(related.optional, 'both')

    def test_exists(self):
        tree = self.parse(
            "Any X WHERE X firstname 'lulu',"
            "EXISTS (X owned_by U, U in_group G, G name 'lulufanclub' OR G name 'managers');"
        )
        self.assertEqual(
            tree.as_string(),
            'Any X WHERE X firstname "lulu", '
            'EXISTS(X owned_by U, U in_group G, (G name "lulufanclub") OR (G name "managers"))',
        )
        exists = tree.children[0].where.get_nodes(nodes.Exists)[0]
        self.assertTrue(exists.children[0].parent is exists)
        self.assertTrue(exists.parent)

    def test_etype(self):
        tree = self.parse('EmailAddress X;')
        self.assertEqual(tree.as_string(), 'Any X WHERE X is EmailAddress')
        tree = self.parse('EUser X;')
        self.assertEqual(tree.as_string(), 'Any X WHERE X is EUser')

    def test_spec(self):
        """test all RQL string found in the specification and test they are well parsed"""
        for rql in SPEC_QUERIES:
            with self.subTest(rql=rql):
                self.parse(rql, True)

    def test_raise_badsyntax_error(self):
        for rql in BAD_SYNTAX_QUERIES:
            with self.subTest(rql=rql):
                self.assertRaises(self._syntaxerr, self.parse, rql)

    def test_raise_badrqlquery(self):
        BAD_QUERIES = ('Person Marcou;',)
        for rql in BAD_QUERIES:
            with self.subTest(rql=rql):
                self.assertRaises(BadRQLQuery, self.parse, rql)


class ParserRQLHelper(ParserHercule):
    _syntaxerr = RQLSyntaxError

    def parse(self, string, print_errors=False):
        try:
            return parse(string, print_errors)
        except Exception:
            raise


if __name__ == '__main__':
    unittest.main()
