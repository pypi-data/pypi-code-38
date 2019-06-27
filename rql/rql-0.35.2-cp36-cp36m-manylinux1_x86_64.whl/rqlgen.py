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
"""Generation of RQL strings.

"""
__docformat__ = "restructuredtext en"

from six.moves import range

NOT = 1


class RQLGenerator(object):
    """
    Helper class to generate RQL strings.
    """

    def select(self, etype, nupplets=(), groups=(), sorts=()):
        """
        Return a RQL selection query.

        :Parameters:
         * `etype`: the desired entity type (can be 'Any')

         * `nupplets`: a list of 4-uples (subject, relation, object, not).
           <subject> and <object> may be a string representing a variable
           or a constant. The special variable X represents the searched set
           of entities.
           <relation> is the statement axis.
           <not> is a boolean indicating it should be a negative statement
           (0 -> positive statement, 1 -> negative statement). You may omit
           this parameter, it default to 0.

         * `groups`: a list of variables to use in groups

         * `sorts`: a list of sort term. A sort term is a string designing a
           variable and optionnaly the sort order ('ASC' or 'DESC'). If the
           sort order is omitted default to 'ASC'

        Example:

        >>> s = RQLGenerator()
        >>> s.select('Any', (('X', 'eid', 14),) )
        'Any X\\nWHERE X eid 14'
        >>> s.select('Person',
        ...          ( ('X','work_for','S'), ('S','name','"Logilab"'),
        ...            ('X','firstname','F'), ('X','surname','S') ),
        ...          sorts=('F ASC', 'S DESC')
        ...          )
        'Person X\\nWHERE X work_for S , S name "Logilab" , X firstname F , X surname S\\nSORTBY F ASC, S DESC' # noqa
        """
        result = [etype + ' X']
        if nupplets:
            result.append(self.where(nupplets))
        if groups:
            result.append(self.groupby(groups))
        if sorts:
            result.append(self.sortby(sorts))
        return '\n'.join(result)

    def where(self, nupplets):
        """Return a WHERE statement.

        :Parameters:
         * `nupplets`: a list of 4-uples (subject, relation, object, not)
           <subject> and <object> maybe a string designing a variable or a
           constant. The special variable X represents the searched set of
           entities
           <relation> is the statement axis
           <not> is a boolean indicating it should be a negative statement
           (0 -> positive statement, 1 -> negative statement). You may omit
           this parameter, it default to 0.

        Example:

        >>> s = RQLGenerator()
        >>> s.where( (('X', 'eid', 14),) )
        'WHERE X eid 14'
        >>> s.where( ( ('X','work_for','S'), ('S','name','"Logilab"'),
        ...            ('X','firstname','F'), ('X','surname','S') ) )
        'WHERE X work_for S , S name "Logilab" , X firstname F , X surname S'
        """
        result = ['WHERE']
        total = len(nupplets)
        for i in range(total):
            nupplet = nupplets[i]
            if len(nupplet) == 4 and nupplet[3] == NOT:
                result.append('NOT')
            result.append(str(nupplet[0]))
            result.append(str(nupplet[1]))
            result.append(str(nupplet[2]))
            if i < total - 1:
                result.append(',')
        return ' '.join(result)

    def groupby(self, groups):
        """Return a GROUPBY statement.

        :param groups: a list of variables to use in groups

        Example:

        >>> s = RQLGenerator()
        >>> s.groupby(('F', 'S'))
        'GROUPBY F, S'
        """
        return 'GROUPBY %s' % ', '.join(groups)

    def sortby(self, sorts):
        """Return a SORTBY statement.

        :param sorts: a list of sort term. A sort term is a string designing a
          variable and optionnaly the sort order ('ASC' or 'DESC'). If the
          sort order is omitted default to 'ASC'


        Example:

        >>> s = RQLGenerator()
        >>> s.sortby(('F ASC', 'S DESC'))
        'SORTBY F ASC, S DESC'
        """
        return 'SORTBY %s' % ', '.join(sorts)

    def insert(self, etype, attributes):
        """Return an INSERT statement.

        :Parameters:
         * `etype`: the entity type to insert
         * `attributes`: a list of tuples (attr_name, attr_value)

        Example:

        >>> s = RQLGenerator()
        >>> s.insert('Person', (('firstname', "Clark"), ('lastname', "Kent")))
        'INSERT Person X: X firstname "Clark", X lastname "Kent"'
        """
        restrictions = ['X %s "%s"' % (attr_name, attr_value)
                        for attr_name, attr_value in attributes]  # .items()]
        return 'INSERT %s X: %s' % (etype, ', '.join(restrictions))

    def delete(self, etype, attributes):
        """Return a DELETE statement.

        :Parameters:
         * `etype`: the entity type to delete
         * `attributes`: a list of tuples (attr_name, attr_value)

        Example:

        >>> s = RQLGenerator()
        >>> s.delete('Person', (('firstname', "Clark"), ('lastname', "Kent")))
        'DELETE Person X where X firstname "Clark", X lastname "Kent"'
        """
        restrictions = ['X %s "%s"' % (attr_name, attr_value)
                        for attr_name, attr_value in attributes]  # .items()]
        return 'DELETE %s X where %s' % (etype, ', '.join(restrictions))

    def update(self, etype, old_descr, new_descr):
        """Return a SET statement.

        :Parameters:
         * `etype`: the entity type to update
         * `old_descr`: a list of tuples (attr_name, attr_value)
           that identifies the entity to update
         * `new_descr`: a list of tuples (attr_name, attr_value)
           that defines the attributes to update

        Example:

        >>> s = RQLGenerator()
        >>> s.update('Person', (('firstname', "Clark"), ('lastname', "Kent")),
        ...         (('job', "superhero"), ('nickname', "superman")))
        'SET X job "superhero", X nickname "superman" WHERE X is "Person", X firstname "Clark", X lastname "Kent"' # noqa
        """
        old_restrictions = ['X is "%s"' % etype]
        old_restrictions += ['X %s "%s"' % (attr_name, attr_value)
                             for attr_name, attr_value in old_descr]
        new_restrictions = ['X %s "%s"' % (attr_name, attr_value)
                            for attr_name, attr_value in new_descr]
        return 'SET %s WHERE %s' % (', '.join(new_restrictions),
                                    ', '.join(old_restrictions))


RQLGENERATOR = RQLGenerator()


def _test():
    """
    Launch doctest
    """
    import doctest
    import sys
    return doctest.testmod(sys.modules[__name__])


if __name__ == "__main__":
    _test()
