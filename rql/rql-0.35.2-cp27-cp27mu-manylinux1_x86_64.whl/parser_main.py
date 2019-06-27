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
"""Main parser command.

"""
from __future__ import print_function

__docformat__ = "restructuredtext en"

if __name__ == '__main__':
    from sys import argv
    from rql.parser import Hercule, HerculeScanner

    parser = Hercule(HerculeScanner(argv[1]))
    e_types = {}
    # parse the RQL string
    try:
        tree = parser.goal(e_types)
        print('-'*80)
        print(tree)
        print('-'*80)
        print(repr(tree))
        print(e_types)
    except SyntaxError as ex:
        # try to get error message from yapps
        from yapps.runtime import print_error
        print_error(ex, parser._scanner)
