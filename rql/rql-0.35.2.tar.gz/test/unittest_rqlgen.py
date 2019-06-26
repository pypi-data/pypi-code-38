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

import doctest
import unittest

from rql import rqlgen


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(rqlgen))
    return tests


class RQLGenTC(unittest.TestCase):
    """tests the rqlgen behaviour
    """

    def setUp(self):
        """Only defines a rql generator
        """
        self.rql_generator = rqlgen.RQLGenerator()

    def test_select_etype(self):
        """tests select with entity type only
        """
        rql = self.rql_generator.select('Person')
        self.assertEqual(rql, 'Person X')

    def test_select_group(self):
        """tests select with group
        """
        rql = self.rql_generator.select('Person', groups=('X',))
        self.assertEqual(rql, 'Person X\nGROUPBY X')

    def test_select_sort(self):
        """tests select with sort
        """
        rql = self.rql_generator.select('Person', sorts=('X ASC',))
        self.assertEqual(rql, 'Person X\nSORTBY X ASC')

    def test_select(self):
        """tests select with e_type, attributes, sort, and group
        """
        rql = self.rql_generator.select('Person',
                                        (('X', 'work_for', 'S'),
                                         ('S', 'name', '"Logilab"'),
                                         ('X', 'firstname', 'F'),
                                         ('X', 'surname', 'S')),
                                        ('X',),
                                        ('F ASC', 'S DESC'))
        self.assertEqual(rql, 'Person X\nWHERE X work_for S , S name "Logilab"'
                         ' , X firstname F , X surname S\nGROUPBY X'
                         '\nSORTBY F ASC, S DESC')

    def test_where(self):
        """tests the where() method behaviour
        """
        rql = self.rql_generator.where((('X', 'work_for', 'S'),
                                        ('S', 'name', '"Logilab"'),
                                        ('X', 'firstname', 'F'),
                                        ('X', 'surname', 'S')))
        self.assertEqual(rql, 'WHERE X work_for S , S name "Logilab" '
                         ', X firstname F , X surname S')

    def test_groupby(self):
        """tests the groupby() method behaviour
        """
        rql = self.rql_generator.groupby(('F', 'S'))
        self.assertEqual(rql, 'GROUPBY F, S')

    def test_sortby(self):
        """tests the sortby() method behaviour
        """
        rql = self.rql_generator.sortby(('F ASC', 'S DESC'))
        self.assertEqual(rql, 'SORTBY F ASC, S DESC')

    def test_insert(self):
        """tests the insert() method behaviour
        """
        rql = self.rql_generator.insert('Person', (('firstname', "Clark"),
                                                   ('lastname', "Kent")))
        self.assertEqual(rql, 'INSERT Person X: X firstname "Clark",'
                         ' X lastname "Kent"')

    def test_update(self):
        """tests the update() method behaviour
        """
        rql = self.rql_generator.update('Person',
                                        (('firstname', "Clark"),
                                         ('lastname', "Kent")),
                                        (('job', "superhero"),
                                         ('nick', "superman")))
        self.assertEqual(rql, 'SET X job "superhero", X nick "superman" '
                         'WHERE X is "Person", X firstname "Clark", X '
                         'lastname "Kent"')

    def test_delete(self):
        """tests the delete() method behaviour
        """
        rql = self.rql_generator.delete('Person',
                                        (('firstname', "Clark"),
                                         ('lastname', "Kent")))
        self.assertEqual(rql, 'DELETE Person X where X firstname "Clark", '
                         'X lastname "Kent"')


if __name__ == '__main__':
    unittest.main()
