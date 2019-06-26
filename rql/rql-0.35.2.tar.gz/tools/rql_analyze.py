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
from __future__ import print_function

from ginco.server.schema_readers import load_schema
from rql import RQLHelper
from rql.analyze import ETypeResolver, ETypeResolver2
import sys


SCHEMA_DIRECTORY = "/home/ludal/SB/prive/soft/ginco/applications/crm/schema"
APP_NAME = "toto"

schema = load_schema(SCHEMA_DIRECTORY, APP_NAME)

# print(schema)


def cmp_sol(sol1, sol2):
    ret = True
    for l in sol1:
        if l not in sol2:
            ret = False
            print("Sol1", l)
    for l in sol2:
        if l not in sol1:
            ret = False
            print("Sol2", l)
    return ret


def analyze_rq(rq):
    print("RQL:", rq)
    helper1 = RQLHelper(schema, Resolver=ETypeResolver)
    helper2 = RQLHelper(schema, Resolver=ETypeResolver2)
    node1 = helper1.parse(rq)
    node2 = helper2.parse(rq)
    sol1 = helper1.get_solutions(node1)
    sol2 = helper2.get_solutions(node2)
    return helper1, helper2, node1, node2, sol1, sol2


if len(sys.argv) < 2:
    print("Usage: rql_analyze.py file")
    sys.exit(1)


for l in open(sys.argv[1]):
    helper1, helper2, node1, node2, sol1, sol2 = analyze_rq(l)
    an1 = helper1._rql_analyser
    an2 = helper2._rql_analyser
    if not cmp_sol(sol1, sol2):
        break
