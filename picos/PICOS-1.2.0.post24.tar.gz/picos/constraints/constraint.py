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
# This file implements the base class for all constraints as well as a
# specialized subclass for metaconstraints.
#-------------------------------------------------------------------------------

import cvxopt

from .. import glyphs

# Import abstract base class support for both Pythons.
from abc import ABCMeta, abstractmethod
ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

class Constraint(ABC):
    """
    An abstract base class for optimization constraints.

    Implementations

        * need to implement the abstract methods :meth:`_str`,
          :meth:`_expression_names`, :meth:`_get_size`, :meth:`_get_slack` and
          :meth:`_set_dual`,
        * need to oberwrite :meth:`_variable_names`, if applicable, and
        * are supposed to call :meth:`Constraint.__init__ <Constraint>` from
          within their own implementation of :meth:`__init__ <Constraint>`.
    """
    LE = "<"
    GE = ">"
    EQ = "="

    def __init__(self, typeTerm, customString = None, printSize = False):
        self.typeTerm     = typeTerm
        self.customString = customString
        self.printSize    = printSize

        self.problem = None
        self.id      = None
        self.name    = None
        self._dual   = None

        # The metaconstraint that created this, if any.
        self.origin  = None

    def __repr__(self):
        if self.printSize:
            return glyphs.repr2("{} {} Constraint".format(
                glyphs.size(*self.size), self.typeTerm), self.__str__())
        else:
            return glyphs.repr2("{} Constraint".format(self.typeTerm),
                self.__str__())

    def __str__(self):
        return "{}{}".format(
            self.customString if self.customString else self._str(),
            " ({})".format(self.name) if self.name else "")

    def __len__(self):
        """
        The number of Lagrange dual variables needed to dualize the constraint.
        """
        return self.size[0] * self.size[1]

    @abstractmethod
    def _expression_names(self):
        """
        The **attribute names** of the expressions stored in the constraint.
        """
        pass

    def _variable_names(self):
        """
        The **attribute names** of variable references stored in the constraint.
        """
        return
        yield

    @abstractmethod
    def _str(self):
        """
        The algebraic representation of the constraint.
        """
        pass

    @abstractmethod
    def _get_size(self):
        """
        The dimensionality of the constraint, more precisely the dimensionality
        of its Lagrange dual variable, as a pair.
        """
        pass

    @abstractmethod
    def _get_slack(self):
        """
        A negative value whose absolute value corresponds to the amount of
        violation, if the constraint is violated, or a non-negative value that
        corresponds to the value of a slack variable, otherwise.
        """
        pass

    def _wrap_get_slack(self):
        """
        A wrapper retrieving the slack in a consistent manner: If it is a scalar
        value, it is returned as a float, otherwise as a
        :class:`CVXOPT matrix <cvxopt.matrix>`.
        """
        slack = self._get_slack()

        if isinstance(slack, float):
            return slack

        assert isinstance(slack, cvxopt.matrix), "Constraints need to return " \
            "the slack as either a float or a CVXOPT matrix."

        if slack.size == (1, 1):
            return float(slack[0])
        else:
            return slack

    def _get_dual(self):
        return self._dual

    def _set_dual(self, value):
        """
        Stores a dual solution value for the dual variable corresponding to the
        constraint in a consistent manner.

        Duals for multidmensional constraints are stored as a
        :class:`CVXOPT matrix <cvxopt.matrix>` while duals for scalar
        constraints are stored as a float.
        """
        if value is None:
            self._dual = None
        elif type(value) in (int, float, complex):
            if len(self) != 1:
                raise ValueError("Incompatible dimensions of dual value: "
                    "Expected {} but got a scalar.".format(self.size))

            self._dual = value
        else:
            try:
                dual = cvxopt.matrix(value, self.size)
            except TypeError:
                raise ValueError("Incompatible dimensions of dual value for {}:"
                    " Expected {} and got container of size {}."
                    .format(self.__class__.__name__, glyphs.size(*self.size),
                    len(value)))

            self._dual = dual[0] if len(dual) == 1 else dual

    size  = property(lambda self: self._get_size())
    slack = property(lambda self: self._wrap_get_slack())
    dual  = property(lambda self: self._get_dual(), _set_dual)

    def delete(self):
        """
        Deletes the constraint from the problem it is assigned to.
        """
        if not self.problem:
            return

        # TODO: Allow removing constraints by constraint object.
        index = self.problem.constraints.index(self)
        assert type(index) is int
        self.problem.remove_constraint(index)

    def expressions(self):
        for name in self._expression_names():
            yield getattr(self, name)

    def copy_with_new_vars(self, newVars, newCons = None):
        from copy import copy
        from ..tools import copy_exp_to_new_vars

        assert newCons is None, \
            "'newCons' may only be set when copying a metaconstraint."

        # NOTE: This is intentially a flat copy to give more control over the
        #       deep copy that is achieved in this method.
        other = copy(self)

        # Convert all expressions stored in the constraint to use the new set of
        # variables.
        for name in self._expression_names():
            expression = getattr(self, name)
            newExpression = copy_exp_to_new_vars(expression, newVars)
            setattr(other, name, newExpression)

        # Redirect all variable references stored in the constraint to the new
        # variables.
        for name in self._variable_names():
            variable = getattr(self, name)
            newVariable = newVars[variable.name]
            setattr(other, name, newVariable)

        return other

    # TODO: Evaluate uses of this method.
    def constring(self):
        return self._str()

    # TODO: Re-implement pretty printing for problems.
    def keyconstring(self):
        return self.__str__()

    def is_meta(self):
        return False

    def is_real(self):
        for expression_name in self._expression_names():
            expression = getattr(self, expression_name)
            if hasattr(expression, "is_real"):
                if not expression.is_real():
                    return False
            else:
                raise TypeError("{}.{} of type {} does not define 'is_real'."
                    .format(self.__class__.__name__, expression_name,
                    expression.__class__.__name__))
        return True

    def is_complex(self):
        return not self.is_real()

    def _assure_lhs_rhs_relation(self):
        if not hasattr(self, "relation") or not hasattr(self, "lhs") \
        or not hasattr(self, "rhs"):
            raise TypeError("{} does not explicitly define a relation " \
                "between a left hand side and a right hand side expression."
                .format(self.__class__.__name__))

    def is_equality(self):
        """Whether the constraints states the equality between the left hand
        side and the right hand side."""
        self._assure_lhs_rhs_relation()
        return self.relation is self.EQ

    def is_inequality(self):
        """Whether the constraints states an inequality between the left hand
        side and the right hand side."""
        self._assure_lhs_rhs_relation()
        return self.relation is not self.EQ

    def is_increasing(self):
        """Whether the constraint states exactly that the left hand side is
        smaller or equal than the right hand side."""
        self._assure_lhs_rhs_relation()
        return self.relation is self.LE

    def is_decreasing(self):
        """Whether the constraint states exactly that the left hand side is
        greater or equal than the right hand side."""
        self._assure_lhs_rhs_relation()
        return self.relation is self.GE


class MetaConstraint(Constraint):
    """
    An abstract base class for optimization constraints that are comprised of
    auxiliary variables and constraints.

    Implementations

        * need to implement the abstract method :meth:`_get_prefix`,
        * need to implement :class:`Constraint`'s abstract methods :meth:`_str`
          and :meth:`_get_slack`,
        * may overwrite the default implementation for :class:`Constraint`'s
          abstract methods :meth:`_get_size` and :meth:`_get_dual`, and
        * are supposed to receive or construct a temporary problem containing
          the auxiliary objects and pass it to :meth:`MetaConstraint.__init__
          <MetaConstraint>` (along with a number of standard parameters that are
          dispatched to :meth:`Constraint.__init__ <Constraint>`) from within
          their own implementation of :meth:`__init__ <MetaConstraint>`.
    """
    def __init__(self, tmpProblem, typeTerm, customString = None):
        super(MetaConstraint, self).__init__(typeTerm, customString)

        self.tmpProblem = tmpProblem
        """A temporary problem used to store blueprints of auxiliary constraints
        and auxiliary variables. It is destroyed when the
        :class:`MetaConstraint` is added to a proper problem."""

        self.auxCons = []
        """Auxiliary constraints that are known to the parent problem after the
        :class:`MetaConstraint` was added to it."""

        self.auxVars = {}
        """A mapping from variable names to variables that are known to the
        parent problem after the :class:`MetaConstraint` was added to it."""

    def _get_size(self):
        raise NotImplementedError(
            "{} does not define a constraint dimensionality."
            .format(self.__class__.__name__))

    def _get_dual(self):
        raise NotImplementedError(
            "{} does not define a dual value. Access its 'auxCons' instead."
            .format(self.__class__.__name__))

    def _set_dual(self, value):
        raise TypeError("Cannot set the dual value of a metaconstraint.")

    @abstractmethod
    def _get_prefix(self):
        pass

    prefix = property(lambda self: self._get_prefix())

    def is_meta(self):
        return True

    def copy_with_new_vars(self, newVars, newCons = None):
        assert newCons is not None, \
            "'newCons' must be set when copying a metaconstraint."

        other = super(MetaConstraint, self).copy_with_new_vars(newVars)

        # Constraint.copy_with_new_vars makes a flat copy except for also
        # copying expressions and variables referenced in the constraint
        # implementation. So we first need to make a flat copy of the additional
        # containers stored in a MetaConstraint instance.
        other.auxVars = other.auxVars.copy()
        other.auxCons = other.auxCons[:] # Python 2 does not have list.copy.

        # Update the auxVars copy with the new variables.
        for varName in other.auxVars.keys():
            other.auxVars[varName] = newVars[varName]

        # Update the auxCons copy with the new constraints.
        for i in range(len(other.auxCons)):
            other.auxCons[i] = newCons[other.auxCons[i]]

        return other

    def delete(self):
        # TODO: Remove the whole MetaConstraint from the problem. It is probably
        #       best to do this in a rewrite of Problem.remove_constraint.
        raise NotImplementedError(
            "Deleting MetaConstraints is not yet implemented.")

        # for constraint in self.auxCons:
        #     constraint.delete()
        #
        # # TODO: Add Variable.delete.
        # for name, variable in self.auxVars.items():
        #     variable.parent_problem.remove_variable(name)

    constraints   = property(lambda self: tuple(self.auxCons))
    variableNames = property(lambda self: tuple(self.auxVars.keys()))
    variables     = property(lambda self: tuple(self.auxVars.values()))
