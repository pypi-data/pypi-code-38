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
# This file implements quadratic constraints.
#-------------------------------------------------------------------------------

from .. import glyphs

from .constraint import Constraint

class QuadConstraint(Constraint):
    """
    An upper bound on a scalar quadratic expression.
    """
    def __init__(self, lowerEqualZero, customString = None):
        from ..expressions import QuadExp

        assert isinstance(lowerEqualZero, QuadExp)

        self.le0 = lowerEqualZero

        super(QuadConstraint, self).__init__(
            "Quadratic", customString, printSize = False)

    def _expression_names(self):
        yield "le0"

    def _str(self):
        return glyphs.le(self.le0.string, 0)

    def _get_size(self):
        return (1, 1)

    def _get_slack(self):
        return -self.le0.eval()[0]
