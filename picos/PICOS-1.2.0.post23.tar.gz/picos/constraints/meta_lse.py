# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2018 Maximilian Stahlberg
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
# This file implements convex geometric programming (GP) constraints via a
# logarithm of sum of exponentials (LSE) expression.
#-------------------------------------------------------------------------------

from ..tools import expcone
from .. import glyphs

from .constraint import MetaConstraint

class LSEConstraint(MetaConstraint):
    """
    An upper bound on a log-sum-exp expression.
    """
    def __init__(self, lse, upperBound):
        from ..problem import Problem
        from ..expressions import AffinExp, LogSumExp

        assert isinstance(lse, LogSumExp)
        assert isinstance(upperBound, AffinExp)
        assert len(upperBound) == 1

        self.lse = lse
        self.ub  = upperBound

        P = Problem()
        u = P.add_variable("u", len(self.exponents))
        P.add_constraint((1.0 | u) <= 1.0)
        for i in range(len(self.exponents)):
            P.add_constraint(
                (u[i] // 1.0 // (self.exponents[i] - self.ub)) << expcone())

        super(LSEConstraint, self).__init__(P, "LSE")

    exponents = property(lambda self: self.lse.Exp)
    """The exponents of the logarithm of sum of exponentials expression."""

    le0Exponents = property(lambda self: self.lse.Exp - self.ub)
    """The exponents of the logarithm of sum of exponentials expression after
    the constraint was reformulated to have an upper bound of zero."""

    def _le0(self):
        from ..expressions import LogSumExp
        return LogSumExp(self.le0Exponents)

    le0 = property(lambda self: self._le0())
    """The logarithm of sum of exponentials expression after the constraint was
    reformulated to have an upper bound of zero."""

    def has_zero_bound(self):
        return self.ub.is0()

    def _expression_names(self):
        yield "lse"
        yield "ub"

    def _get_prefix(self):
        return "_lse"

    def _str(self):
        return glyphs.le(self.lse.string, self.ub.string)

    def _get_size(self):
        return (1, 1)

    def _get_dual(self):
        # TODO: Is this the dual?
        return self.auxCons[0].dual

    def _get_slack(self):
        return -self.le0.value
