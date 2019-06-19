# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
# Copyright (C)      2018 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This file implements a (symmetrized) (truncated) simplex constraint.
#-------------------------------------------------------------------------------

import cvxopt

from ..tools import norm
from .. import glyphs

from .constraint import MetaConstraint

class SymTruncSimplexConstraint(MetaConstraint):
    def __init__(self, simplex, element):
        from ..problem import Problem
        from ..expressions import AffinExp, TruncatedSimplex

        assert isinstance(simplex, TruncatedSimplex)
        assert isinstance(element, AffinExp)

        self.simplex = simplex
        self.element = element

        P = Problem()
        n = len(element)

        if simplex.truncated:
            if simplex.nonneg:
                if simplex.radius <= 1:
                    aff = (-element[:]) // (1 | element[:])
                    rhs = cvxopt.sparse([0] * n + [simplex.radius])
                else:
                    aff = (element[:]) // (-element[:]) // (1 | element[:])
                    rhs = cvxopt.sparse([1] * n + [0] * n + [simplex.radius])

                P.add_constraint(aff <= rhs)
            else:
                v = P.add_variable('v', n)
                P.add_constraint(element[:] < v)
                P.add_constraint(-element[:] < v)
                P.add_constraint((1 | v) < simplex.radius)

                if simplex.radius > 1:
                    P.add_constraint(v < 1)
        else:
            if simplex.nonneg:
                aff = (-element[:]) // (1 | element[:])
                rhs = cvxopt.sparse([0] * n + [simplex.radius])

                P.add_constraint(aff <= rhs)
            else:
                P.add_constraint(norm(element, 1) < simplex.radius)

        super(SymTruncSimplexConstraint, self).__init__(P, simplex.typeStr)

    def _expression_names(self):
        yield "simplex"
        yield "element"

    def _get_prefix(self):
        return "_nts"

    def _str(self):
        return glyphs.element(self.element.string, self.simplex.string)

    def _get_slack(self):
        return cvxopt.matrix([1 - norm(self.element, 'inf').value,
            self.simplex.radius - norm(self.element, 1).value])
