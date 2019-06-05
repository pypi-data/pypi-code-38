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
# This file implements affine constraints.
#-------------------------------------------------------------------------------

from .. import glyphs

from .constraint import Constraint

class AffineConstraint(Constraint):
    """
    An equality or inequality between two affine expressions.
    """
    def __init__(self, lhs, relation, rhs, customString = None):
        from ..expressions import AffinExp

        assert isinstance(lhs, AffinExp)
        assert isinstance(rhs, AffinExp)
        assert relation in self.LE + self.GE + self.EQ

        if lhs.size != rhs.size:
            raise ValueError("Failed to form a constraint: "
                "Expressions have incompatible dimensions.")

        self.lhs      = lhs
        self.rhs      = rhs
        self.relation = relation

        super(AffineConstraint, self).__init__(
            "Affine", customString, printSize = True)

    smaller = property(
        lambda self: self.rhs if self.relation is self.GE else self.lhs)
    """The smaller-or-equal side expression in case of an inequality, otherwise
    the left hand side."""

    greater = property(
        lambda self: self.lhs if self.relation is self.GE else self.rhs)
    """The greater-or-equal side expression in case of an inequality, otherwise
    the right hand side."""

    le0 = property(lambda self:
        self.rhs-self.lhs if self.relation is self.GE else self.lhs-self.rhs)
    """The expression posed to be less or equal than zero in case of an
    inequality, otherwise the left hand side minus the right hand side."""

    ge0 = property(lambda self:
        self.lhs-self.rhs if self.relation is self.GE else self.rhs-self.lhs)
    """The expression posed to be greater or equal than zero in case of an
    inequality, otherwise the right hand side minus the left hand side."""

    def _expression_names(self):
        yield "lhs"
        yield "rhs"

    def _str(self):
        if self.relation is self.LE:
            return glyphs.le(self.lhs.string, self.rhs.string)
        elif self.relation is self.GE:
            return glyphs.ge(self.lhs.string, self.rhs.string)
        else:
            return glyphs.eq(self.lhs.string, self.rhs.string)

    def _get_size(self):
        return self.lhs.size

    def _get_slack(self):
        if self.relation is self.LE:
            delta = self.rhs.eval() - self.lhs.eval()
        else:
            delta = self.lhs.eval() - self.rhs.eval()
        return -abs(delta) if self.relation is self.EQ else delta

    def bounded_linear_form(self):
        """
        Separates the constraint into a linear function on the left hand side
        and a constant bound on the right hand side.

        :returns: A pair ``(linear, bound)`` where ``linear`` is a pure linear
            expression and ``bound`` is a constant expression.
        """
        from ..expressions import AffinExp

        linear = self.lhs - self.rhs
        if linear.constant:
            bound = AffinExp(size = linear.size, constant = -linear.constant)
        else:
            bound = AffinExp(size = linear.size) + 0
        linear += bound

        return (linear, bound)

    def sparse_Ab_rows(self, varOffsetMap, indexFunction = None):
        """
        A sparse list representation of the constraint, given a mapping of PICOS
        variables to column offsets (or alternatively given an index function).

        The constraint is brought into a bounded linear form A • b, where • is
        one of ≤, ≥, or =, depending on the constraint relation, and the rows
        returned correspond to the matrix [A|b].

        :param dict varOffsetMap: Maps variables or variable start indices to
            column offsets.
        :param indexFunction: Instead of adding the local variable index to the
            value returned by varOffsetMap, use the return value of this
            function, that takes as argument the variable and its local index,
            as the "column index", which need not be an integer. When this
            parameter is passed, the parameter varOffsetMap is ignored.
        :returns: A list of triples (J, V, c) where J contains column indices
            (representing scalar variables), V contains coefficients for each
            column index and c is a constant term. Each entry of the list
            represents a row in a constraint matrix.
        """
        lhs  = self.lhs - self.rhs
        rows = lhs.sparse_rows(varOffsetMap, indexFunction = indexFunction)

        for localConIndex in range(len(lhs)):
            rows[localConIndex][2] = -rows[localConIndex][2]

        return rows
