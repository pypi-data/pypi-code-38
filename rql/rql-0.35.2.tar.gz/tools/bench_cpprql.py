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

from rql.rqlparse import parse
import sys

from rql.nodes import *
from rql.stmts import *

builder = {
    "Constant": Constant,
    "Function": Function,
    "Relation": Relation,
    "Comparison": Comparison,
    "And": AND,
    "Or": OR,
    "VariableRef": VariableRef,
    "Insert": Insert,
    "Select": Select,
    "Delete": Delete,
    "Update": Update,
    "MathExpression": MathExpression,
    "Sort": Sort,
    "Sortterm": SortTerm,
}

if len(sys.argv) < 2:
    print("Usage: bench_cpprql file")
    print("     file: a file containing rql queries")
    sys.exit(1)

f = open(sys.argv[1])
for l in f:
    # print(l, end="")
    x = parse(l, builder)
    print(".", end="")
