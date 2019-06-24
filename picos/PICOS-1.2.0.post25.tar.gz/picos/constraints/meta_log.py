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
# This file implements a lower bound on a logarithm.
#-------------------------------------------------------------------------------

from ..tools import expcone
from .. import glyphs

from .constraint import MetaConstraint

class LogConstraint(MetaConstraint):
    """
    A lower bound on a logarithmic expression.
    """
    def __init__(self, log, lowerBound):
        from ..problem     import Problem
        from ..expressions import AffinExp, Logarithm

        assert isinstance(log, Logarithm)
        assert isinstance(lowerBound, AffinExp)
        assert len(lowerBound) == 1

        self.log = log
        self.lb  = lowerBound

        P = Problem()
        x, t = log.Exp, lowerBound
        P.add_constraint(x >= 0)
        P.add_constraint((x // 1.0 // t) << expcone())

        super(LogConstraint, self).__init__(P, "Logarithmic")

    def _expression_names(self):
        yield "log"
        yield "lb"

    def _get_prefix(self):
        return "_log"

    def _str(self):
        return glyphs.ge(self.log.string, self.lb.string)

    def _get_size(self):
        return (1, 1)

    def _get_dual(self):
        raise NotImplementedError

    def _get_slack(self):
        return self.log.value - self.lb.value
