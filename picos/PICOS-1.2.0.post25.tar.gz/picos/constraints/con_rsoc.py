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
# This file implements rotated second order cone (RSOC) constraints.
#-------------------------------------------------------------------------------

import cvxopt

from .. import glyphs

from .constraint import Constraint

class RSOCConstraint(Constraint):
    """
    A rotated second order cone constraint.
    """
    def __init__(self, normedExpression, upperBoundFactor1,
            upperBoundFactor2 = None, customString = None):
        from ..expressions import AffinExp

        if upperBoundFactor2 is None:
            upperBoundFactor2 = AffinExp() + 1

        assert isinstance(normedExpression, AffinExp)
        assert isinstance(upperBoundFactor1, AffinExp)
        assert isinstance(upperBoundFactor2, AffinExp)
        assert len(upperBoundFactor1) == 1
        assert len(upperBoundFactor2) == 1

        self.ne  = normedExpression
        self.ub1 = upperBoundFactor1
        self.ub2 = upperBoundFactor2

        super(RSOCConstraint, self).__init__(
            "RSOC", customString, printSize = True)

    def _expression_names(self):
        yield "ne"
        yield "ub1"
        yield "ub2"

    def _str(self):
        if self.ub2.is1():
            return glyphs.le(glyphs.squared(glyphs.norm(self.ne.string)),
                self.ub1.string)
        else:
            return glyphs.le(glyphs.squared(glyphs.norm(self.ne.string)),
                glyphs.mul(self.ub1.string, self.ub2.string))

    def _get_size(self):
        return (len(self.ne) + 2, 1)

    def _get_slack(self):
        return (self.ub1.eval() * self.ub2.eval() - (abs(self.ne)**2).eval())[0]
