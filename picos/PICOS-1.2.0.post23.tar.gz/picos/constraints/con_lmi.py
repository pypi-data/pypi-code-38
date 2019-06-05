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
# This file implements linear matrix inequality (SDP) constraints.
#-------------------------------------------------------------------------------

from ..tools import svecm1_identity_factor
from .. import glyphs

from .constraint import Constraint

class LMIConstraint(Constraint):
    """
    An inequality with respect to the positive semidefinite cone, also known as
    a Linear Matrix Inequality (LMI) or an SDP constraint.
    """
    def __init__(self, lhs, relation, rhs, customString = None):
        from ..expressions import AffinExp

        assert isinstance(lhs, AffinExp)
        assert isinstance(rhs, AffinExp)
        assert relation in self.LE + self.GE

        if lhs.size != rhs.size:
            raise ValueError("Failed to form a constraint: "
                "Expressions have incompatible dimensions.")

        if lhs.size[0] != lhs.size[1]:
            raise ValueError("Failed to form a constraint: "
                "LMI expressions are not square.")

        self.lhs      = lhs
        self.rhs      = rhs
        self.relation = relation

        # Check if the constraint simply poses positive semidefiniteness on a
        # matrix variable, as certain solvers can handle this more effeciently
        # than a general linear matrix inequality.
        self.semidefVar = None
        psd = self.psd
        if len(psd.factors) == 1 and not psd.constant:
            variable = list(psd.factors.keys())[0]

            if svecm1_identity_factor(psd.factors, variable):
                if variable.vtype == "continuous":
                    raise ValueError(
                        "A matrix variable that has not been declared as "
                        "symmetric is constrained to be positive semidefinite.")
                elif variable.vtype == "complex":
                    raise ValueError(
                        "A complex matrix variable that has not been declared "
                        "hermitian is constrained to be positive semidefinite.")
                elif variable.vtype in ("symmetric", "hermitian"):
                    self.semidefVar = variable

        super(LMIConstraint, self).__init__(
            "LMI", customString, printSize = True)

    smaller = property(
        lambda self: self.rhs if self.relation is self.GE else self.lhs)
    """The smaller-or-equal side expression."""

    greater = property(
        lambda self: self.lhs if self.relation is self.GE else self.rhs)
    """The greater-or-equal side expression."""

    psd = property(lambda self:
        self.lhs-self.rhs if self.relation is self.GE else self.rhs-self.lhs)
    """The matrix expression posed to be positive semidefinite."""

    nsd = property(lambda self:
        self.rhs-self.lhs if self.relation is self.GE else self.lhs-self.rhs)
    """The matrix expression posed to be negative semidefinite."""

    nnd = psd
    """The matrix expression posed to be nonnegative definite."""

    npd = nsd
    """The matrix expression posed to be nonpositive definite."""

    def _expression_names(self):
        yield "lhs"
        yield "rhs"

    def _variable_names(self):
        if self.semidefVar:
            yield "semidefVar"

    def _str(self):
        if self.relation is self.LE:
            return glyphs.psdle(self.lhs.string, self.rhs.string)
        else:
            return glyphs.psdge(self.lhs.string, self.rhs.string)

    def _get_size(self):
        return self.lhs.size

    def _get_slack(self):
        if self.relation == self.LE:
            return self.rhs.eval() - self.lhs.eval()
        else:
            return self.lhs.eval() - self.rhs.eval()
