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
# This file implements a (p,q)-norm inequality constraint.
#-------------------------------------------------------------------------------

from ..tools import norm
from .. import glyphs

from .constraint import MetaConstraint

class PQNormConstraint(MetaConstraint):
    def __init__(self, pqNorm, upperBound):
        from ..problem import Problem
        from ..expressions import AffinExp, NormP_Exp

        assert isinstance(pqNorm, NormP_Exp)
        assert isinstance(upperBound, AffinExp)
        assert len(upperBound) == 1
        assert pqNorm.num2 is not None, \
            "Won't create a (p,q)-norm constraint for a p-norm."

        self.p = float(pqNorm.numerator) / float(pqNorm.denominator)
        self.q = float(pqNorm.num2)      / float(pqNorm.den2)

        assert self.p >= 1, \
            "Upper bounding (p,q)-norm requires p s.t. the norm is convex."

        self.pqNorm     = pqNorm
        self.upperBound = upperBound

        m = len(pqNorm.exp)
        N = pqNorm.exp.size[0]

        P = Problem()
        u = P.add_variable('v', N)

        for i in range(N):
            P.add_constraint(norm(pqNorm.exp[i, :], self.q) <= u[i])

        if self.p == 1:
            P.add_constraint(1 | u <= upperBound)
        elif self.p == float('inf'):
            P.add_constraint(u <= upperBound)
        elif self.p == 2:
            P.add_constraint(abs(u) <= upperBound)
        else:
            P.add_constraint(norm(u, p) <= upperBound)

        super(PQNormConstraint, self).__init__(P, pqNorm.typeStr)

    def _expression_names(self):
        yield "pqNorm"
        yield "upperBound"

    def _get_prefix(self):
        return "_npq"

    def _str(self):
        return glyphs.le(self.pqNorm.string, self.upperBound.string)

    def _get_slack(self):
        return self.upperBound.value - self.pqNorm.value
