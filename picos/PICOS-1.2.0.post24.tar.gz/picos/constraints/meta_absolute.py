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
# This file implements an absolute value constraint.
#-------------------------------------------------------------------------------

from .. import glyphs

from .constraint import MetaConstraint

class AbsoluteValueConstraint(MetaConstraint):
    def __init__(self, signedScalar, upperBound):
        from ..problem import Problem
        from ..expressions import AffinExp

        assert isinstance(signedScalar, AffinExp)
        assert isinstance(upperBound, AffinExp)
        assert len(signedScalar) == 1
        assert len(upperBound) == 1

        self.signedScalar = signedScalar
        self.upperBound   = upperBound

        P = Problem()

        if signedScalar.is_real():
            P.add_constraint(
                (signedScalar // -signedScalar) < (upperBound // upperBound))
        else:
            P.add_constraint(
                abs(signedScalar.real // signedScalar.imag) < upperBound)

        super(AbsoluteValueConstraint, self).__init__(P, "Absolute Value")

    def _expression_names(self):
        yield "signedScalar"
        yield "upperBound"

    def _get_prefix(self):
        return "_abs"

    def _str(self):
        return glyphs.le(
            glyphs.abs(self.signedScalar.string), self.upperBound.string)

    def _get_size(self):
        return (1, 1)

    def _get_dual(self):
        if self.auxCons[0].dual is None:
            return None
        elif self.signedScalar.is_real():
            return self.auxCons[0].dual[1] - self.auxCons[0].dual[0]
        else:
            return self.auxCons[0].dual[0]

    def _get_slack(self):
        return self.upperBound.value - abs(self.signedScalar.value)
