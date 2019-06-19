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
# This file implements second order cone (SOC) constraints.
#-------------------------------------------------------------------------------

import cvxopt

from .. import glyphs

from .constraint import Constraint

class SOCConstraint(Constraint):
    """
    A second order cone (2-norm cone, Lorentz cone) constraint.
    """
    def __init__(self, normedExpression, upperBound, customString = None):
        from ..expressions import AffinExp

        assert isinstance(normedExpression, AffinExp)
        assert isinstance(upperBound, AffinExp)
        assert len(normedExpression) > 1, \
            "Tried to form an SOC constraint for an affine inequality."
        assert len(upperBound) == 1

        self.ne = normedExpression
        self.ub = upperBound

        super(SOCConstraint, self).__init__(
            "SOC", customString, printSize = True)

    def _expression_names(self):
        yield "ne"
        yield "ub"

    def _str(self):
        return glyphs.le(glyphs.norm(self.ne.string), self.ub.string)

    def _get_size(self):
        return (len(self.ne) + 1, 1)

    def _get_slack(self):
        return (self.ub.eval() - abs(self.ne).eval())[0]
