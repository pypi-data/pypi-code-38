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
# This file implements a sum of extremes constraint.
#-------------------------------------------------------------------------------

import cvxopt as cvx

from ..tools import new_param
from .. import glyphs

from .constraint import MetaConstraint

class SumExtremesConstraint(MetaConstraint):
    def __init__(self, theSum, relation, rhs):
        from ..problem import Problem
        from ..expressions import AffinExp,Sum_k_Largest_Exp,Sum_k_Smallest_Exp

        assert relation in self.LE + self.GE
        if relation is self.LE:
            assert isinstance(theSum, Sum_k_Largest_Exp)
        else:
            assert isinstance(theSum, Sum_k_Smallest_Exp)
        assert isinstance(rhs, AffinExp)
        assert len(rhs) == 1

        self.theSum   = theSum
        self.relation = relation
        self.rhs      = rhs

        P = Problem()

        if relation is self.LE:
            if theSum.eigenvalues:
                n = theSum.exp.size[0]
                I = new_param('I', cvx.spdiag([1.] * n))

                if theSum.k == n:
                    P.add_constraint((I | theSum.exp) < rhs)
                elif theSum.k == 1:
                    P.add_constraint(theSum.exp << rhs * I)
                else:
                    s = P.add_variable('s', 1)
                    Z = P.add_variable('Z', (n, n), 'symmetric')
                    P.add_constraint(Z >> 0)
                    P.add_constraint(theSum.exp << Z + s * I)
                    P.add_constraint(rhs > (I | Z) + (theSum.k * s))
            else:
                n = len(theSum.exp)

                if theSum.k == 1:
                    P.add_constraint(theSum.exp < rhs)
                elif theSum.k == n:
                    P.add_constraint((1 | theSum.exp) < rhs)
                else:
                    lbda = P.add_variable('lambda', 1)
                    mu = P.add_variable('mu', theSum.exp.size, lower=0)
                    P.add_constraint(theSum.exp < lbda + mu)
                    P.add_constraint(theSum.k * lbda + (1 | mu) < rhs)
        else:
            if theSum.eigenvalues:
                n = theSum.exp.size[0]
                I = new_param('I', cvx.spdiag([1.] * n))

                if theSum.k == n:
                    P.add_constraint((I | theSum.exp) < rhs)
                elif theSum.k == 1:
                    P.add_constraint(theSum.exp >> rhs * I)
                else:
                    s = P.add_variable('s', 1)
                    Z = P.add_variable('Z', (n, n), 'symmetric')
                    P.add_constraint(Z >> 0)
                    P.add_constraint(-theSum.exp << Z + s * I)
                    P.add_constraint(-rhs > (I | Z) + (theSum.k * s))
            else:
                n = len(theSum.exp)

                if theSum.k == 1:
                    P.add_constraint(theSum.exp > rhs)
                elif theSum.k == n:
                    P.add_constraint((1 | theSum.exp) > rhs)
                else:
                    lbda = P.add_variable('lambda', 1)
                    mu = P.add_variable('mu', theSum.exp.size, lower=0)
                    P.add_constraint(-theSum.exp < lbda + mu)
                    P.add_constraint(theSum.k * lbda + (1 | mu) < -rhs)

        super(SumExtremesConstraint, self).__init__(P, theSum.typeStr)

    def _expression_names(self):
        yield "theSum"
        yield "rhs"

    def _get_prefix(self):
        return "_nsk"

    def _str(self):
        if self.relation is self.LE:
            return glyphs.le(self.theSum.string, self.rhs.string)
        else:
            return glyphs.ge(self.theSum.string, self.rhs.string)

    def _get_slack(self):
        if self.isLargest:
            return self.rhs.value - self.theSum.value
        else:
            return self.theSum.value - self.rhs.value
