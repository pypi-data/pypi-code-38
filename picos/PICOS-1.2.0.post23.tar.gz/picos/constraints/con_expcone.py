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
# This file implements exponential cone constraints.
#-------------------------------------------------------------------------------

import numpy as np

from .. import glyphs

from .constraint import Constraint

class ExpConeConstraint(Constraint):
    """
    An exponential cone constraint stating that :math:`(x, y, z)` fulfills
    :math:`x \\geq y e^{\\frac{z}{y}} \\land x > 0 \\land y > 0`.
    """
    def __init__(self, element, customString = None):
        from ..expressions import AffinExp

        assert isinstance(element, AffinExp)
        assert len(element) == 3

        self.element = element

        super(ExpConeConstraint, self).__init__(
            "Exponential Cone", customString, printSize = False)

    x = property(lambda self: self.element[0])
    y = property(lambda self: self.element[1])
    z = property(lambda self: self.element[2])

    def _expression_names(self):
        yield "element"

    def _str(self):
        return glyphs.ge(self.element[0].string,
            glyphs.mul(self.element[1].string, glyphs.exp(glyphs.div(
            self.element[2].string, self.element[1].string))))

    def _get_size(self):
        return (3, 1)

    def _get_slack(self):
        x = self.element.value

        # TODO: Also consider x_1 > 0 and x_2 > 0 by projecting x on the cone's
        #       surface and measuring the distance between the projection and x.
        return x[0] - x[1] * np.exp(x[2] / x[1])
