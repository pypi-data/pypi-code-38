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
# This file implements a (trace of) n-th power constraint.
#-------------------------------------------------------------------------------

from ..tools import geomean, ltrim1, diag, diag_vect
from .. import glyphs

from .constraint import MetaConstraint

class DetRootNConstraint(MetaConstraint):
    def __init__(self, detRootN, lowerBound):
        from ..problem import Problem
        from ..expressions import AffinExp, DetRootN_Exp

        assert isinstance(detRootN, DetRootN_Exp)
        assert isinstance(lowerBound, AffinExp)
        assert len(lowerBound) == 1

        self.detRootN   = detRootN
        self.lowerBound = lowerBound

        P   = Problem()
        nr  = self.detRootN.dim * (self.detRootN.dim + 1) // 2
        l   = P.add_variable('l', (nr, 1))
        L   = ltrim1(l, uptri=0)
        dl  = diag_vect(L)
        ddL = diag(dl)

        P.add_constraint((self.detRootN.exp & L) // (L.T & ddL) >> 0)
        P.add_constraint(lowerBound < geomean(dl))

        super(DetRootNConstraint, self).__init__(P, detRootN.typeStr)

    def _expression_names(self):
        yield "detRootN"
        yield "lowerBound"

    def _get_prefix(self):
        return "_ndt"

    def _str(self):
        return glyphs.ge(self.detRootN.string, self.lowerBound.string)

    def _get_slack(self):
        return self.detRootN.value - self.lowerBound.value
