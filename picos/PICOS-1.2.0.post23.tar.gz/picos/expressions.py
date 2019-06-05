# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
# Copyright (C) 2017-2018 Maximilian Stahlberg
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
# This file implements all mathematical expressions handeled by PICOS.
# TODO: Split this into multiple files.
# TODO: Add operators.py with basic math functions such as sum, log, exp, max,
#       replacing the functions in tools.py that create expressions. All
#       meaningful combinations of these functions and standard operators should
#       give an expression, so that e.g. a KL-divergence can be constructed by
#       writing `x*exp(x/y) + 2*p*exp((2*p)/q)`.
# TODO: Add SumNonlinear which serves as a container for sums of nonequal
#       expressions. Likewise for the maximum and minimum of expressions.
# TODO: Make all expressions (and constraints) immutable, because modifications
#       of either break re-solving with solvers that support it.
# TODO: Add a copy interface where composite expressions yield which affine
#       expressions they store so that they can be copied more easily.
#-------------------------------------------------------------------------------

from __future__ import print_function, division

import cvxopt as cvx
import numpy as np
import sys
import itertools

from . import glyphs
from .tools import *
from .constraints import *
from .constraints.constraint import Constraint

INFINITY = 1e16

def _needs_conversion(object):
    """
    A helper used by operator decorators to decide whether an object needs to
    be converted to an affine expression.
    """
    return not (isinstance(object, Expression) or isinstance(object, Set))

def _conversion_wrapper(operator, lhs, rhs, scalar, same, strict):
    """
    A helper used by operator decorators to convert the right hand side of the
    operation to an affine expression (of any size, the same size as the left
    hand side, or to a scalar) before performing the operation.

    If the right hand side is already some kind of expression, it is not
    converted, but potentially validated.

    :param bool scalar: Whether the right hand side needs to be a scalar.

    :param bool same: Whether the right hand side will be broadcasted to the
        same size as the left hand side.

    :param bool strict: Whether, if the argument is already an affine
        expression, its size must match the desired size.
    """
    assert not (same and scalar)
    assert not strict or (same or scalar)

    if hasattr(operator, "__qualname__"): # Python 3
        opQualName = operator.__qualname__
    else: # Python 2
        opQualName = "{}.{}".format(lhs.__class__.__name__, operator.__name__)

    if scalar:
        size = (1, 1)
        sizeStr = "a scalar"
    elif same:
        assert hasattr(lhs, "size"), "Can only use same size conversion " \
            "wrapper with expressions that have a 'size' attribute."

        size = lhs.size
        sizeStr = "a matrix of size {}".format(glyphs.size(*size))
    else:
        size = None
        sizeStr = "an affine expression"

    if strict and isinstance(rhs, AffinExp) and rhs.size != size:
        raise TypeError(
            "An affine expression of size {} was given but {} expects {}."
            .format(glyphs.size(*rhs.size), opQualName, sizeStr))

    if not _needs_conversion(rhs):
        return operator(lhs, rhs)

    try:
        converted = AffinExp.fromMatrix(rhs, size)

        # FIXME: This should be raised somewhere below fromMatrix.
        if size is not None and converted.size != size:
            raise Exception(
                "Converted expression has size {}, but {} was requested."
                .format(glyphs.size(*converted.size), glyphs.size(*size)))
    except Exception as error:
        raise TypeError("Failed to convert object of type '{}' to {} as an "
            "argument for {}: {}".format(type(rhs).__name__, sizeStr,
            opQualName, str(error)))
    else:
        return operator(lhs, converted)


def _scalar_argument(operator):
    """
    A decorator for binary operators that transforms the argument to a scalar
    affine expression if it is not already some kind of expression.

    If the argument already is an affine expression, then its size is validated.
    """
    def wrapper(self, other):
        return _conversion_wrapper(operator, self, other, True, False, True)
    return wrapper

def _matrix_argument(operator):
    """
    A decorator for binary operators that transforms the argument to an affine
    expression, if it is not already some kind of expression.
    """
    def wrapper(self, other):
        return _conversion_wrapper(operator, self, other, False, False, False)
    return wrapper

def _same_size_argument(operator):
    """
    A decorator for binary operators that transforms the argument to an affine
    expression of the same size as the expression that the operator is invoked
    on, if the argument is not already some kind of expression.
    """
    def wrapper(self, other):
        return _conversion_wrapper(operator, self, other, False, True, False)
    return wrapper

def _strict_same_size_argument(operator):
    """
    A decorator for binary operators that transforms the argument to an affine
    expression of the same size as the expression that the operator is invoked
    on, if the argument is not already some kind of expression.

    If the argument already is an affine expression, then its size is validated.
    """
    def wrapper(self, other):
        return _conversion_wrapper(operator, self, other, False, True, True)
    return wrapper


class Expression(object):
    """
    The parent class of all expressions, including variables.
    """
    def __init__(self, typeStr, symbStr):
        self.typeStr = typeStr
        """A string describing the expression type."""

        self.string  = symbStr
        """A symbolic string representation of the expression. It is always used
        by __descr__, and it is equivalent to the value returned by __str__ when
        the expression is not fully valued."""

    def eval(self):
        pass

    def get_value(self):
        value = self.eval()

        if type(value) in (int, float, complex):
            return value

        if type(value) not in (cvx.base.matrix, cvx.base.spmatrix):
            value = cvx.matrix(value)

        return value[0] if len(value) == 1 else value

    def get_value_as_matrix(self):
        value = self.eval()

        if type(value) not in (cvx.base.matrix, cvx.base.spmatrix):
            value = cvx.matrix(value)

        return value

    def set_value(self, value):
        raise TypeError("You can only set the value on a variable.")

    def del_value(self):
        raise TypeError("You can only reset the value of a variable.")

    # TODO: This is bound to break; refactor it to use OOP properly.
    def has_complex_coef(self):
        hcc = False
        if hasattr(self,'quad'):
            hcc = 'z' in [m.typecode for m in self.quad.values()]
        if hasattr(self,'aff'):
            hcc = hcc or 'z' in [m.typecode for m in self.aff.factors.values()]
            if self.aff.constant:
                hcc = hcc or ('z' == self.aff.constant.typecode)
        if hasattr(self,'factors'):
            hcc = hcc or 'z' in [m.typecode for m in self.factors.values()]
            if self.constant:
                hcc = hcc or 'z' == self.constant.typecode
        return hcc

    value = property(
        lambda self: self.get_value(),
        lambda self, x: self.set_value(x),
        lambda self: self.del_value())
    """
    Value of the expression.

    It is defined (not None) in the following three situations:

        * The expression is constant.
        * Every variable involved in the expression is valued (this can be done
          by setting ``value`` on each of the variables).
        * The expression involves variables of a problem that has already been
          solved, so that their values are set to some optimum value.

    Unlike :func:`valueAsMatrix`, scalars are returned as scalar types.
    """

    valueAsMatrix = property(
        lambda self: self.get_value_as_matrix(),
        lambda self, x: self.set_value(x),
        lambda self: self.del_value())
    """
    Value of the expression.

    Refer to :func:`value` for when it is available.

    Unlike :func:`value`, scalars are returned in the form of 1x1 matrices.
    """

    def is_valued(self):
        """
        :returns: Whether the expression is valued.

        **Example**

        >>> import picos as pic
        >>> prob=pic.Problem()
        >>> x=prob.add_variable('x',2)
        >>> x.is_valued()
        False
        >>> print(abs(x))
        ‖x‖
        >>> x.value=[3,4]
        >>> abs(x).is_valued()
        True
        >>> print(abs(x))
        5.0
        """
        try:
            val = self.value
            return val is not None
        except:
            return False

    def __le__(self, exp):
        return self.__lt__(exp)

    def __ge__(self, exp):
        return self.__gt__(exp)

    def __lt__(self, other):
        # HACK: Mimic Python 3's exception when neither a.__lt__(b) nor
        #       b.__gt__(a) are implemented.
        if sys.version_info[0] is 2:
            setattr(self, "LT_HACK_TOKEN", None)
            try:
                if hasattr(other, "__gt__") \
                and not hasattr(other, "GT_HACK_TOKEN"):
                    retval = other.__gt__(self)
                    if retval is not NotImplemented:
                        return retval

                raise TypeError(
                    "Constraints of the form '{} < {}' are not supported."
                    .format(type(self).__name__, type(other).__name__))
            finally:
                delattr(self, "LT_HACK_TOKEN")
        else:
            return NotImplemented

    def __gt__(self, other):
        # HACK: Mimic Python 3's exception when neither a.__lt__(b) nor
        #       b.__gt__(a) are implemented.
        if sys.version_info[0] is 2:
            setattr(self, "GT_HACK_TOKEN", None)
            print(dir(self))
            try:
                if hasattr(other, "__lt__") \
                and not hasattr(other, "LT_HACK_TOKEN"):
                    retval = other.__lt__(self)
                    if retval is not NotImplemented:
                        return retval

                raise TypeError(
                    "Constraints of the form '{} > {}' are not supported."
                    .format(type(self).__name__, type(other).__name__))
            finally:
                print(dir(self))
                delattr(self, "GT_HACK_TOKEN")
        else:
            return NotImplemented

    def __eq__(self, exp):
        raise NotImplementedError("PICOS supports equality comparison only "
            "between affine expressions, as otherwise the problem would "
            "become non-convex. Choose either <= or >= if possible.")

    def __repr__(self):
        return glyphs.repr2(self.typeStr, self.string)

    def __str__(self):
        """
        Returns a string description of the expression, based on whether the
        expression is valued. If it is valued, then a string representation of
        the value is returned. Otherwise, the symbolic description of the
        expression is returned.
        """
        if self.is_valued():
            return str(self.value)
        else:
            # Note that self.string is stored as a glyphs.OpStr. We don't want
            # the user to be confused about it, so we return a string copy.
            return str(self.string)

    def __format__(self, format_spec):
        if self.is_valued():
            return self.value.__format__(format_spec)
        else:
            return self.string.__format__(format_spec)

    def _casting_helper(self, theType):
        assert theType in (int, float)

        if not self.is_valued():
            raise TypeError("Tried to cast unvalued expression {} as {}."
                .format(self, "an int" if theType is int else "a float"))

        value = self.get_value_as_matrix()

        if len(value) != 1:
            raise TypeError(
                "Tried to cast multidimensional expression {} as {}."
                .format(self, "an int" if theType is int else "a float"))

        return theType(value[0])

    def __float__(self):
        return self._casting_helper(float)

    def __int__(self):
        return self._casting_helper(int)

    def __round__(self, ndigits=None):
        return round(float(self), ndigits)

    # Since we define __eq__, __hash__ is not inherited. Do this manually.
    __hash__ = object.__hash__

    # HACK: This prevents NumPy operators from iterating over PICOS expressions.
    __array_priority__ = float("inf")


class AffinExp(Expression):
    """
    A class for defining vectorial (or matrix) affine expressions.

    **Overloaded operators**

        :``+``: sum (with an affine or quadratic expression)
        :``+=``: in-place sum (with an affine or quadratic expression)
        :``-``: unitary minus or substraction (of an affine or quadratic
            expression) or unitary
        :``*``: multiplication (by another affine expression or a scalar)
        :``^``: hadamard product (elementwise multiplication with another affine
            expression, similarly as MATLAB operator ``.*``)
        :``/``: division (by a scalar)
        :``|``: scalar product (with another affine expression)
        :``[·]``: slice of an affine expression
        :``abs(·)``: Euclidean norm (Frobenius norm for matrices)
        :``**``: exponentiation (works with arbitrary powers for constant affine
            expressions, and any nonzero exponent otherwise). In the case of a
            nonconstant affine expression, the exponentiation returns a
            quadratic expression if the exponent is :math:`2`, or a
            :class:`TracePow_Exp <picos.expressions.TracePow_Exp>` object for
            other exponents. A rational approximation of the exponent is used,
            and the power inequality is internally replaced by an equivalent set
            of second order cone inequalities.
        :``&``: horizontal concatenation (with another affine expression)
        :``//``: vertical concatenation (with another affine expression)
        :``<``: less **or equal** (than an affine or quadratic expression)
        :``>``: greater **or equal** (than an affine or quadratic expression)
        :``==``: is equal (to another affine expression)
        :``<<``: less than inequality in the Loewner ordering (linear matrix
            inequality :math:`\\preceq`); or, if the right hand side is a
            :class:`Set`, membership in this set.
        :``>>``: greater than inequality in the Loewner ordering (linear matrix
            inequality :math:`\\succeq` )

    .. Warning::

        We recall here the implicit assumptions that are made when using
        relation operator overloads:

            * The rotated second order cone constraint
              ``abs(exp1)**2 < exp2 * exp3`` implicitely assumes that the scalar
              expression ``exp2`` (and hence ``exp3``) **is nonnegative**.

            * Inequalities involving an exponentiation of the form ``x**p``
              where ``p`` is not an even positive integer impose nonnegativity
              on ``x``.

            * The linear matrix inequality ``exp1 >> exp2`` only tells picos
              that the symmetric matrix whose lower triangular elements are
              those of ``exp1-exp2`` is positive semidefinite. The matrix
              ``exp1-exp2`` **is not constrained to be symmetric**. Hence, you
              should manually add the constraint ``exp1-exp2 == (exp1-exp2).T``
              if it is not clear from the data that this matrix is symmetric.
    """
    def __init__(self, factors=None, constant=None, size=(1, 1), string='0',
            typeBaseStr = "Affine Expression"):
        assert len(size)==2 and is_integer(size[0]) and is_integer(size[1])

        # FIXME: The default string of '0' only works in conjunction with the
        #        default values of factors and constant.

        # TODO: This should not be necessary, instead make the default
        #       parameter the empty dictionary.
        if factors is None:
            factors = {}

        # HACK: Affine expressions support in-place operations, so we can't fix
        #       the descriptive strings now. The following thus replaces the
        #       super constructor.
        self.string      = string
        self.typeBaseStr = typeBaseStr

        self.factors = factors
        """
        Dictionary storing the matrix of coefficients of the linear part of the
        affine expressions. The matrices of coefficients are always stored with
        respect to vectorized variables (for the case of matrix variables), and
        are indexed by instances of the class :class:`Variable
        <picos.expressions.Variable>`.
        """

        self.constant = constant
        """
        Constant of the affine expression, stored as a
        :func:`cvxopt sparse matrix <cvxopt:cvxopt.spmatrix>`.
        """

        self._size = (int(size[0]), int(size[1]))
        """Size of the affine expression."""

    # HACK: Affine expressions support in-place operations, so overwrite
    #       Expression's typeStr member.
    typeStr = property(lambda self: "{} {}".format(
        glyphs.size(*self.size), self.typeBaseStr))

    @classmethod
    def fromScalar(cls, scalar):
        const, string = retrieve_matrix(scalar, (1, 1))
        return cls(constant = const, string = string)

    @classmethod
    def fromMatrix(cls, matrix, size = None):
        const, string = retrieve_matrix(matrix, size)
        return cls(constant = const[:], size = const.size, string = string)

    @classmethod
    def zero(cls, size = (1, 1)):
        string = glyphs.scalar(0) if size == (1, 1) else glyphs.matrix(0)
        return cls(constant=cvx.matrix(0.0, size), size=size, string=string)

    @property
    def size(self):
        """Size of the affine expression."""
        return self._size

    def __len__(self):
        return self.size[0] * self.size[1]

    def sparse_rows(
            self, varOffsetMap, lowerTriangle = False, upperTriangle = False,
            indexFunction = None):
        """
        A sparse list representation of the expression, given a mapping of PICOS
        variables to column offsets (or alternatively given an index function).

        :param dict varOffsetMap: Maps variables or variable start indices to
            column offsets.
        :param bool lowerTriangle: Whether to return only the lower triangular
            part of the expression.
        :param bool lowerTriangle: Whether to return only the upper triangular
            part of the expression.
        :param indexFunction: Instead of adding the local variable index to the
            value returned by varOffsetMap, use the return value of this
            function, that takes as argument the variable and its local index,
            as the "column index", which need not be an integer. When this
            parameter is passed, the parameter varOffsetMap is ignored.
        :returns: A list of triples (J, V, c) where J contains column indices
            (representing scalar variables), V contains coefficients for each
            column index and c is a constant term. Each entry of the list
            represents a row in the vectorization of the expression.
        """
        if lowerTriangle and upperTriangle:
            lowerTriangle = False
            upperTriangle = False

        numRows = len(self)
        rows    = []
        for row in range(numRows):
            rows.append([[], [], 0.0])

        for variable, coefficients in self.factors.items():
            if not indexFunction:
                try:
                    varOffset = varOffsetMap[variable]
                except KeyError:
                    varOffset = varOffsetMap[variable.startIndex]

            for localConIndex, localVarIndex, coefficient in \
                    zip(coefficients.I, coefficients.J, coefficients.V):
                if lowerTriangle and localConIndex < localVarIndex:
                    continue
                elif upperTriangle and localVarIndex < localConIndex:
                    continue

                row = rows[localConIndex]

                if indexFunction:
                    row[0].append(indexFunction(variable, localVarIndex))
                else:
                    row[0].append(varOffset + localVarIndex)

                row[1].append(coefficient)

        if self.constant:
            for localConIndex in range(numRows):
                rows[localConIndex][2] = self.constant[localConIndex]

        return rows

    def copy(self):
        excopy = 1*self
        excopy.string = self.string
        return excopy

    def soft_copy(self):
        return AffinExp(self.factors, self.constant, self.size, self.string)

    def eval(self, ind=None):
        if self.is0():
            return cvx.matrix(0.0, self.size)

        if self.constant is None:
            val = spmatrix([], [], [], (self.size[0] * self.size[1], 1))
        else:
            val = self.constant

        for k in self.factors:
            # ignore this factor if the coef is 0
            if not(self.factors[k]):
                continue

            if ind is None:
                if k.is_valued():
                    if k.vtype == 'symmetric':
                        val = val + self.factors[k] * svec(k.value)
                    else:
                        val = val + self.factors[k] * k.valueAsMatrix[:]
                else:
                    raise Exception(k + ' is not valued')
            else:
                if ind in k.value_alt:
                    if k.vtype == 'symmetric':
                        val = val + self.factors[k] * svec(k.value_alt[ind])
                    else:
                        val = val + self.factors[k] * k.value_alt[ind][:]
                else:
                    raise Exception(
                        k + ' does not have a value for the index ' + str(ind))

        return cvx.matrix(val, self.size)

    def set_value(self, value):
        # is it a complex variable?
        if self.is_pure_complex_var():
            facs = list(self.factors.keys())
            if facs[0].name.endswith('_RE'):
                Zr = facs[0]
                Zi = facs[1]
            else:
                Zr = facs[1]
                Zi = facs[1]
            Zr.value = value.real()
            if value.typecode == 'z':
                Zi.value = value.imag()
            else:
                Zi.value = 0
            return
        # is it an antisym variable ?
        if self.is_pure_antisym_var():
            facs = list(self.factors.keys())
            vutri = facs[0]
            n = int((vutri.size[0])**0.5)
            value = retrieve_matrix(value, (n, n))[0]
            vutri.value = utri(value)
            return
        raise Exception('set_value can only be called on a Variable')

    def del_value(self):
        # is it a complex variable?
        if self.is_pure_complex_var():
            facs = list(self.factors.keys())
            if facs[0].name.endswith('_RE'):
                Zr = facs[0]
                Zi = facs[1]
            else:
                Zr = facs[1]
                Zi = facs[1]
            del Zi.value
            del Zr.value
            return
        # is it an antisym variable ?
        if self.is_pure_antisym_var():
            facs = list(self.factors.keys())
            vutri = facs[0]
            del vutri.value
            return
        raise Exception('del_value can only be called on a Variable')

    def get_type(self):
        # is it a complex variable?
        if self.is_pure_complex_var():
            return 'complex'
        elif self.is_pure_antisym_var():
            return 'antisym'
        raise Exception('get_type can only be called on a Variable')

    def set_type(self, value):
        raise Exception('set_type can only be called on a Variable')

    def del_type(self):
        raise Exception('vtype cannot be deleted')

    vtype = property(
        get_type,
        set_type,
        del_type,
        "vtype (for complex and antisym variables)")

    def get_real(self):
        # is it a complex variable?
        if self.is_pure_complex_var():
            facs = list(self.factors.keys())
            if facs[0].name.endswith('_RE'):
                return facs[0]
            else:
                return facs[1]
        else:
            return 0.5 * (self + self.conj)

    def set_real(self, value):
        raise Exception('real is not writable')

    def del_real(self):
        raise Exception('real is not writable')

    real = property(
        get_real,
        set_real,
        del_real,
        "real part (for complex expressions)")

    def get_imag(self):
        # is it a complex variable?
        if self.is_pure_complex_var():
            facs = list(self.factors.keys())
            if facs[0].name.endswith('_RE'):
                return facs[1]
            else:
                return facs[0]
        else:
            return -1j * 0.5 * (self - self.conj)

    def set_imag(self, value):
        raise Exception('imag is not writable')

    def del_imag(self):
        raise Exception('imag is not writable')

    imag = property(
        get_imag,
        set_imag,
        del_imag,
        "imaginary part (for complex expressions)")

    def is_pure_complex_var(self):
        if self.constant:
            return False
        if (len(self.factors) == 2):
            facs = list(self.factors.keys())
            if facs[0].name.endswith('_RE') and is_idty(
                    self.factors[facs[0]]):
                if facs[1].name.endswith(
                        '_IM') and is_idty(-1j * self.factors[facs[1]]):
                    return True
            if facs[1].name.endswith('_RE') and is_idty(
                    self.factors[facs[1]]):
                if facs[0].name.endswith(
                        '_IM') and is_idty(-1j * self.factors[facs[0]]):
                    return True
        return False

    def is_pure_antisym_var(self):
        if self.constant:
            return False
        if (len(self.factors) == 1):
            facs = list(self.factors.keys())
            if facs[0].name.endswith('_utri') and is_idty(
                    self.factors[facs[0]], 'antisym'):
                return True
        return False

    def is_real(self):
        real = True
        for (x, A) in self.factors.items():
            if x.vtype == 'complex':
                return False
            if A.typecode == 'z' and bool(A.imag()):
                if x.vtype != 'hermitian':
                    return False
            if x.vtype == 'hermitian':
                # test if this is an expression of the form P|Z with P
                # Hermitian
                n = int(A.size[1]**(0.5))
                for i in range(A.size[0]):
                    vv = A[i, :]
                    P = cvx.matrix(vv, (n, n))
                    vr = (P.real() - P.real().T)[:]
                    if P.typecode == 'z':
                        vi = (P.imag() + P.imag().T)[:]
                    else:
                        vi = cvx.matrix(0., (1, 1))
                    if (vi.T * vi)[0] + (vr.T * vr)[0] > 1e-6:
                        return False
        if self.constant is None:
            return True
        if self.constant.typecode == 'z' and bool(self.constant.imag()):
            return False
        return True

    def is_valued(self, ind=None):
        try:
            for k in self.factors:
                if ind is None:
                    if k.value is None:
                        return False
                else:
                    if ind not in k.value_alt:
                        return False
        except:
            return False

        # Yes, you can call eval(ind) without any problem.
        return True

    def is0(self):
        """:returns: Whether this is a scalar, vector or matrix of all zeros."""
        # May not have a nonzero constant term.
        if bool(self.constant):
            return False

        # May not have nonzero factors.
        for f in self.factors:
            if bool(self.factors[f]):
                return False

        return True

    def is1(self):
        """:returns: Whether this is a scalar or vector of all ones."""
        # Must have a nonzero constant term.
        if not bool(self.constant):
            return False

        # Must be a scalar or vector.
        if not (self.size[0] == 1 or self.size[1] == 1):
            return False

        # Constant term must be all ones.
        for index in range(len(self)):
            if self.constant[index] != 1.0:
                return False

        # May not have nonzero factors.
        for f in self.factors:
            if bool(self.factors[f]):
                return False

        return True

    def isconstant(self):
        """is the expression constant (no variable involved) ?"""
        for f in self.factors:
            if bool(self.factors[f]):
                return False
        return True

    def same_as(self, other):
        # Note that CVXOPT (sparse) matrices do not support equality comparison.

        if self.size != other.size:
            return False

        if bool(self.constant) != bool(other.constant):
            return False

        if self.constant:
            for i in range(len(self)):
                if self.constant[i] != other.constant[i]:
                    return False

        for f in self.factors:
            if f not in other.factors:
                return False

            s = self.factors[f]
            o = other.factors[f]

            for i in range(len(s)):
                if s[i] != o[i]:
                    return False

        for f in other.factors:
            if f not in self.factors:
                return False

        return True

    def __index__(self):
        if self.is_valued() and self.size == (1, 1) \
        and int(self.value) == self.value:
            return int(self.value)
        else:
            raise Exception(
                'unexpected index (nonvalued, multidimensional, or noninteger)')

    def conjugate(self):
        """Complex conjugate."""
        selfcopy = self.copy()
        selfcopy.inplace_conjugate()
        return selfcopy

    def transpose(self):
        """Matrix transposition."""
        selfcopy = self.copy()
        selfcopy.inplace_transpose()
        return selfcopy

    def Htranspose(self):
        """Hermitian (or conjugate) transposition."""
        selfcopy = self.copy()
        selfcopy.inplace_Htranspose()
        return selfcopy

    def partial_transpose(self, dim_1 = None, subsystems = None, dim_2 = None):
        """Partial transposition."""
        selfcopy = self.copy()
        selfcopy.inplace_partial_transpose(dim_1, subsystems, dim_2)
        return selfcopy

    conj = property(conjugate)
    """Complex conjugate."""

    T = property(transpose)
    """Matrix transposition."""

    H = property(Htranspose)
    """Hermitian (or conjugate) transposition."""

    Tx = property(partial_transpose)
    """Partial transposition for an n²×n² matrix, assuming subblocks of size
    n×n. Refer to :func:`partial_transpose <picos.tools.partial_transpose>`."""

    def inplace_conjugate(self):
        if isinstance(self, Variable):
            raise Exception(
                'inplace_conjugate should not be called on a Variable object')

        for k in self.factors:
            if k.vtype == 'hermitian':
                fack = self.factors[k]
                I = fack.I
                J = fack.J
                V = fack.V
                J0 = []
                V0 = []
                n = int(fack.size[1]**0.5)
                for j, v in zip(J, V):
                    col, row = divmod(j, n)
                    J0.append(row * n + col)
                    V0.append(v.conjugate())
                self.factors[k] = spmatrix(V0, I, J0, fack.size)
            elif self.factors[k].typecode == 'z':
                Fr = self.factors[k].real()
                Fi = self.factors[k].imag()
                self.factors[k] = Fr - 1j * Fi

        if self.constant is not None and self.constant.typecode == 'z':
            Fr = self.constant.real()
            Fi = self.constant.imag()
            self.constant = Fr - 1j * Fi

        self.string = glyphs.conj(self.string)

    def inplace_transpose(self):
        if isinstance(self, Variable):
            raise Exception(
                'inplace_transpose should not be called on a Variable object')

        for k in self.factors:
            bsize = self.size[0]
            bsize2 = self.size[1]
            I0 = [(i // bsize) + (i % bsize) *
                  bsize2 for i in self.factors[k].I]
            J = self.factors[k].J
            V = self.factors[k].V
            self.factors[k] = spmatrix(V, I0, J, self.factors[k].size)

        if not (self.constant is None):
            self.constant = cvx.matrix(self.constant, self.size).T[:]

        self._size = (self.size[1], self.size[0])

        self.string = glyphs.transp(self.string)

    def inplace_Htranspose(self):
        if isinstance(self, Variable):
            raise Exception(
                'inplace_transpose should not be called on a Variable object')

        for k in self.factors:
            if k.vtype == 'hermitian':
                bsize = self.size[0]
                bsize2 = self.size[1]
                vsize = k.size[0]
                vsize2 = k.size[1]
                I0 = [(i // bsize) + (i % bsize) *
                      bsize2 for i in self.factors[k].I]
                J0 = [(j // vsize) + (j % vsize) *
                      vsize2 for j in self.factors[k].J]
                V0 = [v.conjugate() for v in self.factors[k].V]
                self.factors[k] = spmatrix(
                    V0, I0, J0, self.factors[k].size)
            else:
                F = self.factors[k]
                bsize = self.size[0]
                bsize2 = self.size[1]
                I0 = [(i // bsize) + (i % bsize) * bsize2 for i in F.I]
                J = F.J
                V = [v.conjugate() for v in F.V]
                self.factors[k] = spmatrix(V, I0, J, F.size)

        if self.constant is not None:
            if self.constant.typecode == 'z':
                self.constant = cvx.matrix(self.constant, self.size).H[:]
            else:
                self.constant = cvx.matrix(self.constant, self.size).T[:]

        self._size = (self.size[1], self.size[0])

        self.string = glyphs.htransp(self.string)

    def inplace_partial_transpose(
            self, dim_1 = None, subsystems = None, dim_2 = None):
        if isinstance(self, Variable):
            raise Exception(
                'partial_transpose should not be called on a Variable object')

        size = self.size

        if dim_1 is None:
            try :
                s0 = size[0]
                k = [s0**(1.0/i) == int(s0**(1.0/i)) for i in range(2,7)] \
                    .index(True)+2
                subsize = int(s0**(1./k))
                dim_1 = (subsize,)*k
            except ValueError:
                raise ValueError("Partial transposition can only be applied to "
                    "{} matrices when the dimensions of subsystems are not "
                    "defined.".format(glyphs.size(*[glyphs.power("n", "k")]*2)))

        if dim_2 is None:
            dim_2 = dim_1

        if not isinstance(dim_1, tuple) or not isinstance(dim_2, tuple):
            raise TypeError("Dimensions must be tuples.")

        if len(dim_1) != len(dim_2):
            raise ValueError("Dimensions do not match.")

        if np.product(dim_1) != size[0] or np.product(dim_2) != size[1]:
            raise ValueError("Size of subsystems does not match the matrix.")

        N = len(dim_1)

        if subsystems is None:
            subsystems = (N-1,)

        if isinstance(subsystems, int):
            subsystems = (subsystems,)

        if not all([i in range(N) for i in subsystems]):
            raise ValueError("Out of bound subsystem.")

        newdim_1 = ()
        newdim_2 = ()
        for i in range(N):
            if i in subsystems:
                newdim_1 += (dim_2[i],)
                newdim_2 += (dim_1[i],)
            else:
                newdim_2 += (dim_2[i],)
                newdim_1 += (dim_1[i],)

        newsize = (int(np.product(newdim_1)), int(np.product(newdim_2)))

        def block_indices(dims,ii):
            inds = []
            rem = ii
            for k in range(len(dims)):
                blk,rem = divmod(rem,np.product(dims[k+1:]))
                inds.append(int(blk))

            return inds

        for k in self.factors:
            I0 = []
            J = self.factors[k].J
            V = self.factors[k].V

            for i in self.factors[k].I:
                column, row = divmod(i, size[0])
                row_blocks = block_indices(dim_1,row)
                col_blocks = block_indices(dim_2,column)
                new_rblock = [col_blocks[l] if l in subsystems
                    else row_blocks[l] for l in range(N)]
                new_cblock = [row_blocks[l] if l in subsystems
                    else col_blocks[l] for l in range(N)]
                newrow = int(sum([new_rblock[l] * np.product(newdim_1[l+1:])
                    for l in range(N)]))
                newcol = int(sum([new_cblock[l] * np.product(newdim_2[l+1:])
                    for l in range(N)]))
                I0.append(newcol * newsize[0] + newrow)

            self.factors[k] = spmatrix(V, I0, J, self.factors[k].size)

        if not (self.constant is None):
            spconstant = cvx.sparse(self.constant)
            J = spconstant.J
            V = spconstant.V
            I0 = []

            for i in spconstant.I:
                column, row = divmod(i, size[0])
                row_blocks = block_indices(dim_1,row)
                col_blocks = block_indices(dim_2,column)
                new_rblock = [col_blocks[l] if l in subsystems
                    else row_blocks[l] for l in range(N)]
                new_cblock = [row_blocks[l] if l in subsystems
                    else col_blocks[l] for l in range(N)]
                newrow = int(sum([new_rblock[l] * np.product(dim_1[l+1:])
                    for l in range(N)]))
                newcol = int(sum([new_cblock[l] * np.product(dim_2[l+1:])
                    for l in range(N)]))
                I0.append(newcol * newsize[0] + newrow)

            self.constant = spmatrix(V, I0, J, spconstant.size)

        self._size = newsize

        self.string = glyphs.ptransp(self.string)

    def partial_trace(self, k=1, dim=None):
        """
        Partial trace, see also :func:`the partial_trace tool
        <picos.tools.partial_trace>`
        Ref. J. Maziero, Computing partial traces and reduced density matrices, Int. J. Mod. Phys. C 28, 1750005 (2017)
        """
        T = [list,tuple]
        sz = self.size
        #If dim is None, we assume a bipartite system
        if dim is None:
            if type(k) in T:
                if len(k) > 1:
                    raise UserWarning("For partial_trace over mutliple system, dim is required")
            if sz[0] == sz[1] and (sz[0]**0.5) == int(sz[0]**0.5) \
            and (sz[1]**0.5) == int(sz[1]**0.5):
                dim = (int(sz[0]**0.5), int(sz[1]**0.5))
            else:
                raise Exception("The default parameter dim=None assumes X is a "
                    "{} matrix".format(glyphs.size(*[glyphs.cubed("n")]*2)))
        else:
            dim_ = list(dim)

        # checks if dim is a list (or tuple) of lists (or tuples) of two
        # integers each
        if type(dim) in T and all([type(d) in T and len(d) == 2 for d in dim]) \
        and all([type(n) is int for d in dim for n in d]):
            dim = [d for d in zip(*dim)]
            pdim = np.product(dim[0]),np.product(dim[1])

        # if dim is a single list of integers we assume that no subsystem is
        # rectangular
        elif type(dim) in [list,tuple] and all([type(n) is int for n in dim]):
            pdim = np.product(dim),np.product(dim)
            dim = (dim,dim)
        else:
            raise TypeError('Wrong dim variable')

        if len(dim[0]) != len(dim[1]):
            raise ValueError(
                'Inconsistent number of subsystems, fix dim variable')

        if pdim[0] != sz[0] or pdim[1] != sz[1]:
            raise ValueError(
                'The product of the subdimensions does not match the size of X')

        if type(k) in T:
            if len(k) == 1:
                k = k[0]
            elif len(k) >= len(dim_):
                raise ValueError(
                        'Size of k has to be strictly less than the number of subsystems')
            elif len(k) == 0:
                raise ValueError(
                        'k has to contain at least one element')
            elif not all(len(dim_) >= e for e in k):
                raise ValueError(
                        'At least one element of k exceed the number of subsystems')
            else:
                str_ = self.string
                for i,partition in enumerate(sorted(k)):
                    self = self.partial_trace(k=partition-i,dim=dim_)
                    del dim_[partition-i]
                self.string = glyphs.ptrace(",".join([str(p) for p in k]), str_)
                return self

        if type(k) is int:
            if k > len(dim[0])-1:
                raise ValueError(
                    'There is no k-th subsystem, fix k or dim variable')

            if dim[0][k] != dim[1][k] :
                raise ValueError(
                    'The dimensions of the subsystem to trace over don\'t match')

        dim_reduced = [list(d) for d in dim]
        del dim_reduced[0][k]
        del dim_reduced[1][k]
        dim_reduced = tuple(tuple(d) for d in dim_reduced)
        pdimred = tuple([np.product(d) for d in dim_reduced])
        fact = cvx.spmatrix([], [], [], (np.product(pdimred), np.product(pdim)))

        for iii in itertools.product(*[range(i) for i in dim_reduced[0]]):
            for jjj in itertools.product(*[range(j) for j in dim_reduced[1]]):
            # element iii,jjj of the partial trace

                row = int(sum([iii[j] * np.product(dim_reduced[0][j + 1:])
                    for j in range(len(dim_reduced[0]))]))
                col = int(sum([jjj[j] * np.product(dim_reduced[1][j + 1:])
                    for j in range(len(dim_reduced[1]))]))
                # this corresponds to the element row,col in the matrix basis
                rowij = col * pdimred[0] + row
                # this corresponds to the elem rowij in vectorized form

                # computes the partial trace for iii,jjj
                for l in range(dim[0][k]):
                    iili = list(iii)
                    iili.insert(k, l)
                    iili = tuple(iili)

                    jjlj = list(jjj)
                    jjlj.insert(k, l)
                    jjlj = tuple(jjlj)

                    row_l = int(sum([iili[j] * np.product(dim[0][j + 1:])
                        for j in range(len(dim[0]))]))
                    col_l = int(sum([jjlj[j] * np.product(dim[1][j + 1:])
                        for j in range(len(dim[1]))]))

                    colij_l = col_l * pdim[0] + row_l
                    fact[int(rowij), int(colij_l)] = 1

        newfacs = {}
        for x in self.factors:
            newfacs[x] = fact * self.factors[x]
        if self.constant:
            cons = fact * self.constant
        else:
            cons = None

        return AffinExp(newfacs, cons, (pdimred[0], pdimred[1]),
            glyphs.ptrace(k, self.string))

    def hadamard(self, fact):
        """hadamard (elementwise) product"""
        return self ^ fact

    @_same_size_argument
    def __xor__(self, fact):
        """hadamard (elementwise) product"""
        if isinstance(fact, AffinExp):
            ret = self.copy()

            if fact.isconstant():
                ret = self.copy()
                fac = cvx.sparse(fact.valueAsMatrix)
            elif self.isconstant():
                ret = fact.copy()
                fac = cvx.sparse(self.valueAsMatrix)
            else:
                raise NotImplementedError("Hadamard product is only supported "
                    "if one of the factors is constant.")

            if fac.size == (1, 1) and ret.size[0] != 1:
                fac = fac[0] * cvx.spdiag([1.] * ret.size[0])

            if self.size == (1, 1) and fac.size[1] != 1:
                ret = ret.diag(fac.size[1])

            if ret.size != fac.size:
                raise TypeError("Incompatible dimensions.")

            mm, nn = ret.size
            sptype = 'd' if self.is_real() and fact.is_real() else 'z'
            bfac   = spmatrix([], [], [], (mm * nn, mm * nn), tc=sptype)

            for i, j, v in zip(fac.I, fac.J, fac.V):
                bfac[j * mm + i, j * mm + i] = v

            for k in ret.factors:
                ret.factors[k] = bfac * ret.factors[k]

            if ret.constant is None:
                ret.constant = None
            else:
                ret.constant = bfac * ret.constant

            ret.string = glyphs.hadamard(self.string, fact.string)

            return ret
        else:
            return NotImplemented

    # TODO: Refactor __mul__ and __rmul__.
    def __rmul__(self, fact):
        # TODO: The following should never be true; validate this.
        if isinstance(fact, AffinExp):
            if fact.isconstant():
                fac, facString = cvx.sparse(fact.eval()), fact.string

                if fac.size == (1, 1) and self.size[0] != 1:
                    fac = blocdiag(fac, self.size[0])
            else:
                raise Exception('not implemented')

        # fast handling for the most standard case (no need to go inside
        # retrieve_matrix)
        if isinstance(self,Variable) \
        and self.vtype not in ('symmetric', 'antisym') \
        and hasattr(fact, 'size') and isinstance(fact.size, tuple) \
        and len(fact.size) is 2 and fact.size[1] == self.size[0]:
            if not isinstance(fact, AffinExp):
                facString = glyphs.matrix(glyphs.size(*fact.size))
                fac = fact

            bfac = blocdiag(fac, self.size[1])

            return AffinExp(
                factors = {self: bfac}, size = (fac.size[0], self.size[1]),
                string = glyphs.mul(facString, self.string))

        if not isinstance(fact, AffinExp):
            # TODO: Handle this with decorators, if possible.
            fac, facString = retrieve_matrix(fact, self.size[0])

            # HACK: Remove 'I' from the factor's string representation if self
            # is a matrix.
            if  self.size != (1, 1) \
            and isinstance(facString, glyphs.GlStr) \
            and facString.glyph is glyphs.mul \
            and isinstance(facString.operands[1], glyphs.GlStr) \
            and facString.operands[1].glyph is glyphs.idmatrix:
                facString = facString.operands[0]

        if isinstance(self, Variable) \
        and self.vtype not in ('symmetric', 'antisym') \
        and self.size[0] == fac.size[1]:
            bfac = blocdiag(fac, self.size[1])

            return AffinExp(
                factors = {self: bfac}, size = (fac.size[0], self.size[1]),
                string = glyphs.mul(facString, self.string))

        selfcopy = self.soft_copy()

        # TODO: This is inconsistent with the respective code in __mul__.
        is_scalar_mult = (
            isinstance(fact, float)
            or isinstance(fact, INTEGER_TYPES)
            or isinstance(fact, np.float64)
            or isinstance(fact, np.int64)
            or isinstance(fact, np.complex128)
            or isinstance(fact, complex)
            or (hasattr(fact, 'size')  and fact.size == (1,1))
            or (hasattr(fact, 'shape') and fact.shape in ((1,), (1,1))))

        if self.size == (1, 1) and fac.size[1] != 1:
            oldstring = selfcopy.string
            selfcopy = selfcopy.diag(fac.size[1])
            selfcopy.string = oldstring

        if selfcopy.size[0] != fac.size[1]:
            raise Exception('incompatible dimensions')

        if is_scalar_mult:
            bfac = fac[0]
        else:
            bfac = blocdiag(fac, selfcopy.size[1])

        newfac = {}
        for k in selfcopy.factors:
            newfac[k] = bfac * selfcopy.factors[k]

        if selfcopy.constant is None:
            newcons = None
        else:
            newcons = bfac * selfcopy.constant

        selfcopy = AffinExp(factors = newfac, constant = newcons,
            size = (fac.size[0], selfcopy.size[1]), string = selfcopy.string)

        if len(facString) > 0:
            selfcopy.string = glyphs.mul(facString, selfcopy.string)

        return selfcopy

    # TODO: Refactor __mul__ and __rmul__.
    def __mul__(self, fact):
        """product of 2 affine expressions"""
        if isinstance(fact, AffinExp):
            if fact.isconstant():
                fac, facString = cvx.sparse(fact.eval()), fact.string
            elif self.isconstant():
                return fact.__rmul__(self)
            elif self.size[0] == 1 and fact.size[1] == 1 \
            and self.size[1] == fact.size[0]:
                # quadratic expression
                linpart = AffinExp({}, constant=None, size=(1, 1))
                if self.constant is not None:
                    linpart = linpart + self.constant.T * fact
                if fact.constant is not None:
                    linpart = linpart + self * fact.constant
                if fact.constant is not None and self.constant is not None:
                    linpart = linpart - self.constant.T * fact.constant

                quadpart = {}
                for i in self.factors:
                    for j in fact.factors:
                        quadpart[i, j] = self.factors[i].T * fact.factors[j]

                string = glyphs.mul(self.string, fact.string)

                if self.size[1] == 1:
                    return QuadExp(quadpart, linpart, string, LR=(self, fact))
                else:
                    return QuadExp(quadpart, linpart, string)
            else:
                raise NotImplementedError(
                    "Multiplying two matrix expressions is not supported.")
        elif isinstance(fact, QuadExp):
            # TODO: This should be the job of QuadExp.
            return fact * self
        else:
            # TODO: Handle this with decorators, if possible.
            if self.size == (1, 1): # scalar mult. of the constant
                fac, facString = retrieve_matrix(fact, None)
            else:  # normal matrix multiplication, we expect a size
                fac, facString = retrieve_matrix(fact, self.size[1])

        # TODO: This is inconsistent with the respective code in __rmul__.
        is_scalar_mult = (
            is_numeric(fact)
            or (hasattr(fact, 'size')  and fact.size == (1,1))
            or (hasattr(fact, 'shape') and fact.shape in ((1,), (1,1))))

        if is_scalar_mult:
            alpha = fac[0]
            newfacs = {}
            for k, M in self.factors.items():
                newfacs[k] = alpha * M
            if self.constant is None:
                newcons = None
            else:
                newcons = alpha * self.constant

            return AffinExp(newfacs, newcons, self.size,
                glyphs.mul(self.string, facString))

        selfcopy = self.soft_copy()

        if self.size == (1, 1) and fac.size[0] != 1:
            oldstring = selfcopy.string
            selfcopy = selfcopy.diag(fac.size[0])
            selfcopy.string = oldstring

        prod = (selfcopy.T.__rmul__(fac.T)).T
        prod._size = (selfcopy.size[0], fac.size[1])

        # HACK: Remove 'I' from the factor's string representation if self is a
        # matrix.
        if  self.size != (1, 1) \
        and isinstance(facString, glyphs.GlStr) \
        and facString.glyph is glyphs.mul \
        and isinstance(facString.operands[1], glyphs.GlStr) \
        and facString.operands[1].glyph is glyphs.idmatrix:
            facString = facString.operands[0]

        if len(facString) > 0:
            prod.string = glyphs.mul(selfcopy.string, facString)
        else:
            prod.string = selfcopy.string

        return prod

    @_strict_same_size_argument
    def __or__(self, fact):
        """Scalar product."""
        if isinstance(fact, AffinExp):
            dotp = fact[:].H * self[:]
            if isinstance(fact.string, glyphs.GlStr) \
            and fact.string.glyph is glyphs.idmatrix:
                dotp.string = glyphs.trace(self.string)
            elif isinstance(self.string, glyphs.GlStr) \
            and self.string.glyph is glyphs.idmatrix:
                dotp.string = glyphs.trace(fact.string)
            else:
                dotp.string = glyphs.dotp(self.string, fact.string)
            return dotp
        else:
            return NotImplemented

    @_strict_same_size_argument
    def __ror__(self, fact):
        """Scalar product."""
        if isinstance(fact, AffinExp):
            # The argument was cast from a non-expression type, as otherwise the
            # operation would have been handled in __or__.
            return fact.__or__(self)
        else:
            return NotImplemented

    @_same_size_argument
    def __add__(self, term):
        if isinstance(term, AffinExp) or isinstance(term, QuadExp):
            selfcopy = self.copy()
            selfcopy += term
            return selfcopy
        else:
            return NotImplemented

    def __radd__(self, term):
        # TODO: Revisit this once __add__ only handles affine expressions.
        #       expressions, because then the other expression should rather
        #       implement __add__.
        return self.__add__(term)

    def __iadd__(self, term):
        if isinstance(term, AffinExp):
            if term.size != self.size and (1, 1) not in (term.size, self.size):
                raise TypeError(
                    "Cannot add an expression of size {} to one of size {}."
                    .format(glyphs.size(*term.size), glyphs.size(*self.size)))
            elif self.is0():
                # HACK: Variables are also affine expressions, but we don't want
                #       to change type (it would break tools.sum as variables do
                #       not support in-place modification).
                return 1.0 * term
            elif term.is0():
                return self
            elif term.size == (1, 1) and self.size != (1, 1):
                # Cast term to same size as self.
                oldTermString = term.string
                # TODO: The use of diag() seems to work around a shortcoming of
                #       __mul__/__rmul__ w.r.t. scalar/matrix multiplication.
                term = cvx.matrix(1.0, self.size) * term.diag(self.size[1])
                term.string = glyphs.matrix(oldTermString)
            elif self.size == (1, 1) and term.size != (1, 1):
                # Cast self to same size as term and recurse.
                # TODO: The use of diag() seems to work around a shortcoming of
                #       __mul__/__rmul__ w.r.t. scalar/matrix multiplication.
                newSelf = cvx.matrix(1.0, term.size) * self.diag(term.size[1])
                newSelf.string = glyphs.matrix(self.string)
                newSelf += term

                return newSelf

            # Add variable term.
            for k in term.factors:
                if k in self.factors:
                    try:
                        self.factors[k] += term.factors[k]
                    except TypeError:
                        self.factors[k] = self.factors[k] + term.factors[k]
                else:
                    self.factors[k] = term.factors[k]

            # Add constant term.
            if term.constant is not None:
                if self.constant is None:
                    self.constant = cvx.matrix(
                        0.0, self.size, term.constant.typecode)[:]

                try:
                    self.constant += term.constant
                except TypeError:
                    self.constant = self.constant + term.constant

            # Update string.
            self.string = glyphs.cleverAdd(self.string, term.string)

            return self
        elif isinstance(term, QuadExp):
            # TODO: This should be the job of QuadExp.
            if self.size != (1, 1):
                raise TypeError("Can only add a scalar quadratic expression to "
                    "a scalar expression.")

            if self.is0():
                return term
            # TODO: Add QuadExp.is0.
            #elif term.is0():
            #    return self
            else:
                newSelf = QuadExp({}, self, self.string)
                newSelf += term
                return newSelf
        else:
            try:
                term = AffinExp.fromMatrix(term)
            except TypeError:
                return NotImplemented

            if self.is0():
                return term
            elif term.is0():
                return self
            else:
                self += term
                return self

    def __neg__(self):
        negation = (-1) * self
        negation.string = glyphs.cleverNeg(self.string)
        return negation

    @_same_size_argument
    def __sub__(self, term):
        if isinstance(term, AffinExp) or isinstance(term, QuadExp):
            return self + (-term)
        else:
            return NotImplemented

    def __rsub__(self, term):
        """
        Reverse substraction.

        This method ensures that other expressions don't need to implement
        :func:`__sub__` with respect to affine expressions, as long as they
        implement :func:`__add__` for affine expressions.
        """
        return term + (-self)

    def __truediv__(self, divisor):
        return self.__div__(divisor)

    @_scalar_argument
    def __div__(self, divisor):
        if isinstance(divisor, AffinExp):
            if divisor.isconstant():
                value = divisor.value
            else:
                raise TypeError(
                    "You may only divide an affine expression by a constant.")

            if value == 0:
                raise ValueError(
                    "Tried to divide {} by zero.".format(self.string))

            division = self * (1.0 / value)
            division.string = glyphs.div(self.string, divisor.string)
            return division
        else:
            return NotImplemented

    @_matrix_argument
    def __rdiv__(self, divider):
        if isinstance(divider, AffinExp):
            # The argument was cast from a non-expression type, as otherwise the
            # operation would have been handled in __div__.
            return divider.__div__(self)
        else:
            return NotImplemented

    def __getitem__(self, index):
        def indexstr(idx):
            if isinstance(idx, int):
                return str(idx)
            elif isinstance(idx, Expression):
                return idx.string

        def slicestr(sli):
            # single element
            if not (sli.start is None or sli.stop is None):
                sta = sli.start
                sto = sli.stop
                if isinstance(sta, int):
                    sta = new_param(str(sta), sta)
                if isinstance(sto, int):
                    sto = new_param(str(sto), sto)
                if (sto.__index__() == sta.__index__() + 1):
                    return sta.string
            # single element -1 (Expression)
            if (isinstance(sli.start, Expression) and sli.start.__index__()
                    == -1 and sli.stop is None and sli.step is None):
                return sli.start.string
            # single element -1
            if (isinstance(sli.start, int) and sli.start == -1
                    and sli.stop is None and sli.step is None):
                return '-1'
            ss = ''
            if not sli.start is None:
                ss += indexstr(sli.start)
            ss += ':'
            if not sli.stop is None:
                ss += indexstr(sli.stop)
            if not sli.step is None:
                ss += ':'
                ss += indexstr(sli.step)
            return ss

        if isinstance(index, Expression) or isinstance(index, int):
            ind = index.__index__()
            if ind == -1:  # (-1,0) does not work
                index = slice(ind, None, None)
            else:
                index = slice(ind, ind + 1, None)
        if isinstance(index, slice):
            idx = index.indices(self.size[0] * self.size[1])
            rangeT = list(range(idx[0], idx[1], idx[2]))
            newsize = (len(rangeT), 1)
            indstr = slicestr(index)
        elif isinstance(index, tuple):
            if isinstance(index[0], Expression) or isinstance(index[0], int):
                ind = index[0].__index__()
                if ind == -1:
                    index = (slice(ind, None, None), index[1])
                else:
                    index = (slice(ind, ind + 1, None), index[1])
            if isinstance(index[1], Expression) or isinstance(index[1], int):
                ind = index[1].__index__()
                if ind == -1:
                    index = (index[0], slice(ind, None, None))
                else:
                    index = (index[0], slice(ind, ind + 1, None))
            idx0 = index[0].indices(self.size[0])
            idx1 = index[1].indices(self.size[1])
            rangei = range(idx0[0], idx0[1], idx0[2])
            rangej = range(idx1[0], idx1[1], idx1[2])
            rangeT = []
            for j in rangej:
                rangei_translated = []
                for vi in rangei:
                    rangei_translated.append(
                        vi + (j * self.size[0]))
                rangeT.extend(rangei_translated)

            newsize = (len(range(*idx0)), len(range(*idx1)))
            indstr = slicestr(index[0]) + ',' + slicestr(index[1])

        newfacs = {}
        for k in self.factors:
            Ridx, J, V = self.factors[k].T.CCS  # fast row slicing
            II, VV, JJ = [], [], []
            for l, i in enumerate(rangeT):
                idx = range(Ridx[i], Ridx[i + 1])
                for j in idx:
                    II.append(l)
                    JJ.append(J[j])
                    VV.append(V[j])
            newfacs[k] = spmatrix(
                VV, II, JJ, (len(rangeT), self.factors[k].size[1]))

        if not self.constant is None:
            newcons = self.constant[rangeT]
        else:
            newcons = None

        if indstr == ':' and self.size[1] == 1:
            newstr = self.string
        else:
            newstr = glyphs.slice(self.string, indstr)

        # check size
        if newsize[0] == 0 or newsize[1] == 0:
            raise IndexError('slice of zero-dimension')

        return AffinExp(newfacs, newcons, newsize, newstr)

    def __setitem__(self, key, value):
        raise AttributeError('slices of an expression are not writable')

    def __delitem__(self):
        raise AttributeError('slices of an expression are not writable')

    @_same_size_argument
    def __lt__(self, exp):
        if isinstance(exp, AffinExp):
            # TODO: This broadcasting is also used in __iadd__, it should be
            #       part of the decorator function
            #       (_bcast_same_size_argument vs. _strict_same_size_argument).
            if exp.size == (1, 1) and self.size != (1, 1):
                oldstring = exp.string
                exp = cvx.matrix(1.0, self.size) * exp.diag(self.size[1])
                exp.string = glyphs.matrix(oldstring)
            elif self.size == (1, 1) and exp.size != (1, 1):
                oldstring = self.string
                selfone = cvx.matrix(1.0, exp.size) * self.diag(exp.size[1])
                exp.string = glyphs.matrix(oldstring)

                return (selfone < exp)

            return AffineConstraint(self, Constraint.LE, exp)
        elif isinstance(exp, QuadExp):
            # TODO: This should be the job of QuadExp.
            if self.isconstant() and self.size == (1, 1) \
            and (not exp.LR is None) and (not exp.LR[1] is None):
                cst = AffinExp(factors={}, size=(1, 1), string=self.string,
                    constant=cvx.matrix(np.sqrt(self.eval()), (1, 1)))
                return (Norm(cst)**2) < exp
            elif self.size == (1, 1):
                return (-exp) < (-self)
            else:
                raise TypeError("Can't compare non-scalar affine expression to"
                    " a (scalar) quadratic expression.")
        else:
            return NotImplemented

    @_same_size_argument
    def __gt__(self, exp):
        if isinstance(exp, AffinExp):
            # TODO: See __lt__.
            if exp.size == (1, 1) and self.size != (1, 1):
                oldstring = exp.string
                exp = cvx.matrix(1.0, self.size) * exp.diag(self.size[1])
                exp.string = glyphs.matrix(oldstring)
            elif self.size == (1, 1) and exp.size != (1, 1):
                oldstring = self.string
                selfone = cvx.matrix(1.0, exp.size) * self.diag(exp.size[1])
                exp.string = glyphs.matrix(oldstring)

                return (selfone > exp)

            return AffineConstraint(self, Constraint.GE, exp)
        else:
            return NotImplemented

    @_same_size_argument
    def __eq__(self, exp):
        if isinstance(exp, AffinExp):
            # TODO: See __lt__.
            if exp.size == (1, 1) and self.size != (1, 1):
                oldstring = exp.string
                exp = cvx.matrix(1.0, self.size) * exp.diag(self.size[1])
                exp.string = glyphs.matrix(oldstring)
            elif self.size == (1, 1) and exp.size != (1, 1):
                oldstring = self.string
                selfone = cvx.matrix(1.0, exp.size) * self.diag(exp.size[1])
                exp.string = glyphs.matrix(oldstring)

                return (selfone == exp)

            return AffineConstraint(self, Constraint.EQ, exp)
        else:
            # If NotImplemented was returned here, Python would fall back to
            # builtin comparison instead of raising an exception as with the
            # other comparison operators. We refer to Expression.__eq__, which
            # will raise an appropriate exception.
            return Expression.__eq__(self, exp)

    # Since we define __eq__, __hash__ is not inherited. Do this manually.
    __hash__ = Expression.__hash__

    def __abs__(self):
        return Norm(self)

    @_scalar_argument
    def __pow__(self, exponent):
        if self.size != (1, 1):
            raise TypeError(
                "Exponentiation is only implemented for scalar bases.")

        if isinstance(exponent, AffinExp):
            if not exponent.isconstant():
                raise TypeError("Exponentiation is only implemented for "
                    "constant exponents.")

            value = exponent.value

            if value == 2:
                string = glyphs.squared(self.string)
            elif value == 3:
                string = glyphs.cubed(self.string)
            else:
                string = glyphs.power(self.string, exponent.string)

            if self.isconstant():
                return AffinExp(factors = {}, constant = self.value**value,
                    size = (1,1), string = string)
            elif value == 2:
                Q  = QuadExp({}, AffinExp(), None, None)
                qq = self * self
                Q.quad = qq.quad
                Q.LR = (self, None)
                Q.string = string

                return Q
            else:
                return tracepow(self, value)
        else:
            return NotImplemented

    # TODO: This is redundant w.r.t. tools.diag, make both use the same code.
    # TODO: Decide on 'Diag' vs. 'diag' vs. 'diag_vect' for the vector- and
    #       matrix-valued version.
    def diag(self, dim):
        if self.size != (1, 1):
            raise Exception('not implemented')

        selfcopy = self.copy()
        idx = range(0, dim**2, dim + 1)

        for k in self.factors:
            tc = 'z' if self.factors[k].typecode == 'z' else 'd'
            selfcopy.factors[k] = spmatrix(
                [], [], [], (dim**2, self.factors[k].size[1]), tc=tc)
            for i in idx:
                selfcopy.factors[k][i, :] = self.factors[k]

        if self.constant is not None:
            tc = 'z' if self.constant.typecode == 'z' else 'd'
            selfcopy.constant = cvx.matrix(0.0, (dim**2, 1), tc=tc)
            for i in idx:
                selfcopy.constant[i] = self.constant[0]
        else:
            selfcopy.constant = None

        selfcopy._size = (dim, dim)
        selfcopy.string = glyphs.Diag(selfcopy.string)

        return selfcopy

    def __and__(self, exp):
        """Horizontal concatenation from the right hand side."""
        if not isinstance(exp, Expression):
            exp = AffinExp.fromMatrix(exp, self.size[0])

        if isinstance(exp, AffinExp):
            selfcopy = self.copy()
            selfcopy &= exp
            return selfcopy
        else:
            return NotImplemented

    def __rand__(self, exp):
        """Horizontal concatenation from the left hand side."""
        if not isinstance(exp, Expression):
            exp = AffinExp.fromMatrix(exp, self.size[0])

        if isinstance(exp, AffinExp):
            expcopy = exp.copy()
            expcopy &= self
            return expcopy
        else:
            return NotImplemented

    def __iand__(self, exp):
        if isinstance(exp, AffinExp):
            if exp.size[0] != self.size[0]:
                raise Exception('incompatible size for concatenation')

            for k in list(set(exp.factors.keys()).union(
                    set(self.factors.keys()))):
                if (k in self.factors) and (k in exp.factors):
                    if self.factors[k].typecode == 'z' or exp.factors[
                            k].typecode == 'z':
                        facr = self.factors[k].real()
                        if self.factors[k].typecode == 'z':
                            faci = self.factors[k].imag()
                        else:
                            faci = spmatrix([], [], [], facr.size)
                        expr = exp.factors[k].real()
                        if exp.factors[k].typecode == 'z':
                            expi = exp.factors[k].imag()
                        else:
                            expi = spmatrix([], [], [], expr.size)
                        newfac = (cvx.sparse([[facr, expr]]) +
                                  1j * cvx.sparse([[faci, expi]]))
                    else:
                        newfac = cvx.sparse(
                            [[self.factors[k], exp.factors[k]]])
                    self.factors[k] = newfac
                elif k in exp.factors:
                    s1 = self.size[0] * self.size[1]
                    s2 = exp.factors[k].size[1]
                    if exp.factors[k].typecode == 'z':
                        # it seems there is a bug with sparse with complex input
                        newfac = (
                            cvx.sparse([[spmatrix([], [], [], (s1, s2)),
                                exp.factors[k].real()]]) +
                            1j * cvx.sparse([[spmatrix([], [], [], (s1, s2)),
                                exp.factors[k].imag()]]))
                    else:
                        newfac = cvx.sparse(
                            [[spmatrix([], [], [], (s1, s2)), exp.factors[k]]])
                    self.factors[k] = newfac
                else:
                    s1 = exp.size[0] * exp.size[1]
                    s2 = self.factors[k].size[1]
                    if self.factors[k].typecode == 'z':
                        # it seems there is a bug with sparse with complex input
                        newfac = (
                            cvx.sparse([[self.factors[k].real(),
                                spmatrix([], [], [], (s1, s2))]]) +
                            1j * cvx.sparse([[self.factors[k].imag(),
                                spmatrix([], [], [], (s1, s2))]]))
                    else:
                        newfac = cvx.sparse(
                            [[self.factors[k], spmatrix([], [], [], (s1, s2))]])
                    self.factors[k] = newfac

            if self.constant is not None or exp.constant is not None:
                s1 = self.size[0] * self.size[1]
                s2 = exp.size[0] * exp.size[1]

                if not self.constant is None:
                    newCons = self.constant
                else:
                    newCons = spmatrix([], [], [], (s1, 1))

                if not exp.constant is None:
                    # it seems there is a bug with sparse with complex inputs
                    if newCons.typecode == 'z' or exp.constant.typecode == 'z':
                        expr = exp.constant.real()
                        if exp.constant.typecode == 'z':
                            expi = exp.constant.imag()
                        else:
                            expi = spmatrix([], [], [], expr.size)
                        csr = newCons.real()
                        if newCons.typecode == 'z':
                            csi = newCons.imag()
                        else:
                            csi = spmatrix([], [], [], csr.size)
                        newCons = (cvx.sparse([[csr, expr]]) +
                                   1j * cvx.sparse([[csi, expi]]))
                    else:
                        newCons = cvx.sparse([[newCons, exp.constant]])
                else:
                    if newCons.typecode == 'z':
                        # it seems there is a bug with sparse with complex input
                        newCons = (
                            cvx.sparse([[newCons.real(),
                                spmatrix([], [], [], (s2, 1))]]) +
                            1j * cvx.sparse([[newCons.imag(),
                                spmatrix([], [], [], (s2, 1))]]))
                    else:
                        newCons = cvx.sparse(
                            [[newCons, spmatrix([], [], [], (s2, 1))]])

                self.constant = newCons

            self._size = (exp.size[0], exp.size[1] + self.size[1])

            self.string = glyphs.matrixCat(self.string, exp.string, True)

            return self
        else:
            self &= AffinExp.fromMatrix(exp, self.size[0])
            return self

    def __floordiv__(self, exp):
        """Vertical concatenation from the right hand side."""
        if not isinstance(exp, Expression):
            exp = AffinExp.fromMatrix(exp, self.size[1])

        if isinstance(exp, AffinExp):
            # TODO: For some reason, the following does not work:
            # selfcopy = self.copy()
            # selfcopy //= exp
            # return selfcopy

            concat = (self.T & exp.T).T
            concat._size = (exp.size[0] + self.size[0], exp.size[1])
            concat.string = glyphs.matrixCat(self.string, exp.string, False)
            return concat
        else:
            return NotImplemented

    def __rfloordiv__(self, exp):
        """Vertical concatenation from the left hand side."""
        if not isinstance(exp, Expression):
            exp = AffinExp.fromMatrix(exp, self.size[1])

        if isinstance(exp, AffinExp):
            # TODO: It is unclear if the following would work, see __floordiv__.
            # expcopy = exp.copy()
            # expcopy //= self
            # return expcopy

            return exp // self
        else:
            return NotImplemented

    def __ifloordiv__(self, exp):
        """inplace vertical concatenation"""
        if isinstance(exp, AffinExp):
            if exp.size[1] != self.size[1]:
                raise Exception('incompatible size for concatenation')
            for k in list(set(exp.factors.keys()).union(
                    set(self.factors.keys()))):
                if (k in self.factors) and (k in exp.factors):
                    if self.factors[k].typecode == 'z' or exp.factors[
                            k].typecode == 'z':
                        facr = self.factors[k].real()
                        if self.factors[k].typecode == 'z':
                            faci = self.factors[k].imag()
                        else:
                            faci = spmatrix([], [], [], facr.size)
                        expr = exp.factors[k].real()
                        if exp.factors[k].typecode == 'z':
                            expi = exp.factors[k].imag()
                        else:
                            expi = spmatrix([], [], [], expr.size)
                        newfac = (cvx.sparse([facr, expr]) +
                                  1j * cvx.sparse([faci, expi]))
                    else:
                        newfac = cvx.sparse([self.factors[k], exp.factors[k]])
                    self.factors[k] = newfac
                elif k in exp.factors:
                    s1 = self.size[0] * self.size[1]
                    s2 = exp.factors[k].size[1]
                    if exp.factors[k].typecode == 'z':
                        # it seems there is a bug with sparse with complex input
                        newfac = (
                            cvx.sparse([spmatrix([], [], [], (s1, s2)),
                                exp.factors[k].real()]) +
                            1j * cvx.sparse([spmatrix([], [], [], (s1, s2)),
                                exp.factors[k].imag()]))
                    else:
                        newfac = cvx.sparse(
                            [spmatrix([], [], [], (s1, s2)), exp.factors[k]])
                    self.factors[k] = newfac
                else:
                    s1 = exp.size[0] * exp.size[1]
                    s2 = self.factors[k].size[1]
                    if self.factors[k].typecode == 'z':
                        # it seems there is a bug with sparse with complex input
                        newfac = (
                            cvx.sparse([self.factors[k].real(),
                                spmatrix([], [], [], (s1, s2))]) +
                            1j * cvx.sparse([self.factors[k].imag(),
                                spmatrix([], [], [], (s1, s2))]))
                    else:
                        newfac = cvx.sparse(
                            [self.factors[k], spmatrix([], [], [], (s1, s2))])
                    self.factors[k] = newfac

            if self.constant is None and exp.constant is None:
                pass
            else:
                s1 = self.size[0] * self.size[1]
                s2 = exp.size[0] * exp.size[1]
                if not self.constant is None:
                    newCons = self.constant
                else:
                    newCons = spmatrix([], [], [], (s1, 1))
                if not exp.constant is None:
                    # it seems there is a bug with sparse with complex inputs
                    if newCons.typecode == 'z' or exp.constant.typecode == 'z':
                        expr = exp.constant.real()
                        if exp.constant.typecode == 'z':
                            expi = exp.constant.imag()
                        else:
                            expi = spmatrix([], [], [], expr.size)
                        csr = newCons.real()
                        if newCons.typecode == 'z':
                            csi = newCons.imag()
                        else:
                            csi = spmatrix([], [], [], csr.size)
                        newCons = (cvx.sparse([csr, expr]) +
                                   1j * cvx.sparse([csi, expi]))
                    else:
                        newCons = cvx.sparse([newCons, exp.constant])
                else:
                    if newCons.typecode == 'z':
                        # it seems there is a bug with sparse with complex input
                        newCons = (
                            cvx.sparse([newCons.real(),
                                spmatrix([], [], [], (s2, 1))]) +
                            1j * cvx.sparse([newCons.imag(),
                                spmatrix([], [], [], (s2, 1))]))
                    else:
                        newCons = cvx.sparse(
                            [newCons, spmatrix([], [], [], (s2, 1))])
                self.constant = newCons

            self._size = (exp.size[0] + self.size[0], exp.size[1])

            self.string = glyphs.matrixCat(self.string, exp.string, False)

            return self
        else:
            self //= AffinExp.fromMatrix(exp, self.size[1])
            return self

    def apply_function(self, fun):
        return GeneralFun(fun, self, fun())

    @_strict_same_size_argument
    def __lshift__(self, exp):
        if isinstance(exp, Set):
            # Sets define __rshift__ as "contains", so here __lshift__ means
            # "is element of".
            return exp >> self
        elif isinstance(exp, AffinExp):
            return LMIConstraint(self, Constraint.LE, exp)
        else:
            return NotImplemented

    @_strict_same_size_argument
    def __rshift__(self, exp):
        if isinstance(exp, AffinExp):
            return LMIConstraint(self, Constraint.GE, exp)
        else:
            return NotImplemented


class Norm(Expression):
    """
    Euclidean (or Frobenius) norm of an Affine Expression.

    **Overloaded operators**

            :``**``: exponentiation (with an exponent of :math:`2`)
            :``<``: less **or equal** (than a scalar affine expression)
    """
    def __init__(self, exp):
        typeStr = "Norm of a {} Expression".format(glyphs.size(*exp.size))
        symbStr = glyphs.norm(exp.string)

        Expression.__init__(self, typeStr, symbStr)

        self.exp = exp
        """The affine expression of which we take the norm."""

    def eval(self, ind=None):
        vec = self.exp.eval(ind)
        return cvx.matrix(np.linalg.norm(vec), (1, 1))

    def __pow__(self, exponent):
        if (exponent != 2):
            raise ValueError("You may only square a norm.")

        qq = self.exp[:].T * self.exp[:]
        if isinstance(qq, AffinExp):
            qq = QuadExp({}, qq, qq.string)

        normSquared = QuadExp(
            qq.quad, qq.aff, glyphs.squared(self.string), LR=(self.exp, None))

        return normSquared

    @_matrix_argument
    def __lt__(self, exp):
        if isinstance(exp, AffinExp):
            if self.exp.size == (1, 1):
                return AbsoluteValueConstraint(self.exp, exp)
            else:
                return SOCConstraint(self.exp, exp)
        else:
            return NotImplemented


class LogSumExp(Expression):
    """
    The logarithm of a sum of exponentials.

    If an affine expression :math:`x` of size :math:`N` with elements
    :math:`x_1, x_2, \\ldots, x_N` is given, then :class:`LogSumExp(x)
    <LogSumExp>` represents the expression :math:`\\log \\sum_{i=1}^N e^{x_i}`.

    **Overloaded operators**

        :``<``: less **or equal** than
    """
    def __init__(self, exp):
        if not isinstance(exp, AffinExp):
            exp = AffinExp.fromMatrix(exp)

        typeStr = "LSE Expression"
        symbStr = glyphs.makeFunction("log", "sum", "exp")(exp.string)

        Expression.__init__(self, typeStr, symbStr)

        self.Exp = exp

    def __len__(self):
        return len(self.Exp)

    def eval(self, ind = None):
        return cvx.matrix(np.log(np.sum(np.exp(self.Exp.eval(ind)))), (1, 1))

    @_scalar_argument
    def __add__(self, exp):
        if isinstance(exp, AffinExp):
            return LogSumExp(self.Exp + exp)
        else:
            return NotImplemented

    def __radd__(self, exp):
        return self.__add__(exp)

    @_scalar_argument
    def __sub__(self, exp):
        if isinstance(exp, AffinExp):
            return LogSumExp(self.Exp - exp)
        else:
            return NotImplemented

    @_scalar_argument
    def __lt__(self, exp):
        if isinstance(exp, AffinExp):
            return LSEConstraint(self, exp)
        else:
            return NotImplemented


class SumExponential(Expression):
    """
    A sum of (perspectives of) exponentials.

    If an affine expression :math:`x` of size :math:`N` with elements
    :math:`x_1, x_2, \\ldots, x_N` is given, then :class:`SumExponential(x)
    <SumExponential>` represents the expression :math:`\\sum_{i=1}^N e^{x_i}`.

    If a second affine expression :math:`y` (of same dimension as :math:`x`) is
    given, then :class:`SumExponential(x, y) <SumExponential>` represents
    :math:`\\sum_{i=1}^N y_i e^{x_i/y_i}`.

    **Overloaded operators**

        :``+``: addition (with a scalar :class:`AffinExp` or another
            :class:`SumExponential`)
        :``*``: multiplication (with a scalar :class:`AffinExp`)
        :``/``: division (by a scalar :class:`AffinExp`)
        :``<``: less **or equal** (than a scalar :class:`AffinExp` or another
            :class:`SumExponential`)

    .. note ::

        Upper-bounding with a nonconstant scalar :math:`t` adds the implicit
        constraint :math:`t > 0`. Upper-bounding a sum of perspectives of
        exponentials (that is in the case of :math:`y \\neq 1` given)
        independently adds the implicit constraint :math:`y > 0`.
    """
    def __init__(self, exp, exp2 = None):
        if not isinstance(exp, AffinExp):
            exp = AffinExp.fromMatrix(exp)

        if exp2 is None:
            exp2 = 1.0

        if not isinstance(exp2, AffinExp):
            exp2 = AffinExp.fromMatrix(exp2, exp.size)

        if exp.size != exp2.size:
            raise TypeError("Expressions given to construct a sum of "
                "perspectives of exponentials must be of same dimension.")

        if exp.size == (1,1):
            if exp2.is1():
                typeStr = "Exponential"
                symbStr = glyphs.exp(exp.string)
            else:
                typeStr = "Exponential Perspective"
                symbStr = glyphs.mul(exp2.string,
                    glyphs.exp(glyphs.div(exp.string, exp2.string)))
        else:
            if exp2.is1():
                typeStr = "Sum of Exponentials"
                symbStr = glyphs.makeFunction("sum", "exp")(exp.string)
            else:
                typeStr = "Sum of Exponential Perspectives"
                symbStr = glyphs.sum(glyphs.mul(exp2.string,
                    glyphs.exp(glyphs.div(exp.string, exp2.string))))

        Expression.__init__(self, typeStr, symbStr)

        self.Exp  = exp
        self.Exp2 = exp2

    def __len__(self):
        return len(self.Exp)

    def eval(self, ind = None):
        x = np.array(self.Exp.eval(ind)).ravel()
        y = np.array(self.Exp2.eval(ind)).ravel()
        return cvx.matrix(y.dot(np.exp(x / y)), (1, 1))

    @_scalar_argument
    def __add__(self, term):
        if isinstance(term, AffinExp):
            if not term.isconstant():
                raise NotImplementedError("Adding a non-constant scalar to a "
                    "sum of exponentials is not supported.")

            value = term.value

            if value < 0:
                raise NotImplementedError("Adding a negative constant to a sum "
                    "of exponentials is not supported.")
            elif value > 0:
                return SumExponential(
                    (self.Exp[:] // np.log(value)),  (self.Exp2[:] // 1.0))
            else:
                return SumExponential(self.Exp.copy(),  self.Exp2.copy())
        elif isinstance(term, SumExponential):
            return SumExponential(
                (self.Exp[:] // term.Exp[:]), (self.Exp2[:] // term.Exp2[:]))
        else:
            return NotImplemented

    def __radd__(self, term):
        return self.__add__(term)

    @_scalar_argument
    def __mul__(self, factor):
        if isinstance(factor, AffinExp):
            if not factor.isconstant():
                raise NotImplementedError("Multiplying a sum of exponentials "
                    "with a nonconstant scalar is not supported.")

            value = factor.value

            if value < 0:
                raise NotImplementedError("Multiplying a sum of exponentials "
                    "with a negative constant is not supported.")
            elif value > 0:
                return SumExponential(
                    self.Exp + np.log(value), self.Exp2.copy())
            else:
                return AffinExp.fromScalar(0.0)
        elif isinstance(factor, SumExponential):
            lenSelf = len(self)
            lenFact = len(factor)

            if lenSelf == 1 or lenFact == 1:
                return SumExponential(
                    self.Exp * factor.Exp2 + factor.Exp * self.Exp2,
                    self.Exp2 * factor.Exp2)
            elif lenSelf <= lenFact:
                theSum = AffinExp.fromScalar(0.0)
                for i in range(lenSelf):
                    theSum += SumExponential(
                        self.Exp[i] + factor.Exp2 + factor.Exp * self.Exp2[i],
                        self.Exp2[i] * factor.Exp2)
                return theSum
            else:
                theSum = AffinExp.fromScalar(0.0)
                for i in range(lenFact):
                    theSum += SumExponential(
                        self.Exp + factor.Exp2[i] + factor.Exp[i] * self.Exp2,
                        self.Exp2 * factor.Exp2[i])
                return theSum
        else:
            return NotImplemented

    def __rmul__(self,fact):
        return self * fact

    @_scalar_argument
    def __div__(self, dividend):
        if isinstance(dividend, AffinExp):
            if not factor.isconstant():
                raise NotImplementedError("Dividing a sum of exponentials "
                    "by a nonconstant scalar is not supported.")

            value = dividend.value

            if value <= 0:
                raise NotImplementedError("Dividing a sum of exponentials "
                    "by a nonpositive constant is not supported.")
            else:
                return self * value**-1
        else:
            return NotImplemented

    @_scalar_argument
    def __lt__(self, rhs):
        if isinstance(rhs, AffinExp):
            if rhs.isconstant() and rhs.constant[0] <= 0.0:
                raise ValueError("Upper bounding a sum of (perspectives of) "
                    "exponentials with a nonpositive constant is infeasible.")

            if self.Exp2.is1() and rhs.isconstant():
                return lse(self.Exp) <= np.log(rhs.constant[0])
            else:
                return SumExpConstraint(self, rhs)
        elif isinstance(rhs, SumExponential):
            if not (self.Exp2.is1() and rhs.Exp2.is1()):
                raise NotImplementedError("Comparing two sums of (perspectives "
                    "of) exponentials is not supported if one of the sums does "
                    "indeed contain a perspective.")

            if len(rhs) != 1:
                raise NotImplementedError(
                    "Upper bounding a sum of exponentials by another sum of "
                    "two or more exponentials is not supported.")

            return lse(self.Exp) <= rhs.Exp
        else:
            return NotImplemented


class Logarithm(Expression):
    """
    The logarithm of a nonconstant scalar affine expression.

    **Overloaded operators**

        :``+``: addition (with a scalar :class:`AffinExp`)
        :``*``: multiplication (with the expression under the logarithm)
        :``>``: greater **or equal** (than a scalar :class:`AffinExp`)

    .. note ::

        Lower-bounding :math:`\\log(x)` adds the implicit constraint
        :math:`x \\geq 0`.
    """
    def __init__(self, exp):
        self.Exp = exp

        assert isinstance(exp, AffinExp), \
            "A Logarithm object should only be created for affine expressions."

        assert len(exp) is 1, \
            "Can only create Logarithm object from a scalar expression."

        assert not exp.isconstant(), \
            "Tried to create a Logarithm object concerning a constant value."

        Expression.__init__(self, "Logarithm", "log({})".format(exp.string))

    def eval(self, ind = None):
        x = self.Exp.eval(ind)[0]
        if x < 0:
            x = complex(x)
        elif x == 0:
            raise ValueError(
                "Cannot evaluate {} because it is log(0).".format(self.string))
        return cvx.matrix(np.log(x), (1, 1))

    @_scalar_argument
    def __add__(self, term):
        if isinstance(term, AffinExp):
            if term.isconstant():
                if not term.constant or not term.constant[0]:
                    return Logarithm(self.Exp.copy())
                else:
                    return Logarithm(exp(term.constant[0]) * self.Exp)
            else:
                raise NotImplementedError(
                    "You may only add a constant to a logarithm.")
        else:
            return NotImplemented

    @_scalar_argument
    def __radd__(self, factor):
        return self.__add__(factor)

    @_scalar_argument
    def __mul__(self, factor):
        if isinstance(factor, AffinExp):
            if factor.is0():
                return 0
            elif factor.is1():
                return Logarithm(self.Exp.copy())
            elif self.Exp.same_as(factor):
                return KullbackLeibler(self.Exp.copy())
            else:
                raise NotImplementedError(
                    "You may multiply {} only with {}, 0, or 1."
                    .format(self.string, self.Exp.string))
        else:
            return NotImplemented

    @_scalar_argument
    def __rmul__(self, factor):
        return self.__mul__(factor)

    @_scalar_argument
    def __gt__(self, rhs):
        if isinstance(rhs, AffinExp):
            return LogConstraint(self, rhs)
        else:
            return NotImplemented


class KullbackLeibler(Expression):
    """
    A Kullback-Leibler divergence.

    If an affine expression :math:`x` of size :math:`N` with elements
    :math:`x_1, x_2, \ldots, x_N` is given, then :class:`KullbackLeibler(x)
    <KullbackLeibler>` represents the (negative) entropy
    :math:`\\sum_{i=1}^N x_i \\log(x_i)`.

    If a second expression :math:`y` (of same dimension as :math:`x`) is given,
    then  :class:`KullbackLeibler(x, y) <KullbackLeibler>` represents
    :math:`\\sum_{i=1}^N x_i \\log{x_i/y_i}`.

    **Overloaded operators**

        :``+``: addition (with a scalar :class:`AffinExp` or another
            :class:`KullbackLeibler`)
        :``<``: less **or equal** (than a scalar :class:`AffinExp`)

    .. note ::
        Upper-bounding a Kullback-Leibler divergence adds the implicit
        constraints :math:`x > 0` and :math:`y > 0`.
    """
    def __init__(self, exp, exp2 = None):
        if not isinstance(exp, AffinExp):
            exp = AffinExp.fromMatrix(exp)

        if exp2 is None:
            exp2 = 1.0

        if not isinstance(exp2, AffinExp):
            exp2 = AffinExp.fromMatrix(exp2, exp.size)

        if exp.size != exp2.size:
            raise TypeError("Expressions given to construct a Kullback-Leibler "
                "divergence must be of same dimension.")

        if exp.size == (1,1):
            if exp2.is1():
                typeStr = "Entropy"
                symbStr = glyphs.mul(exp.string, glyphs.log(exp.string))
            else:
                typeStr = "Logarithm Perspective"
                symbStr = glyphs.mul(exp.string,
                    glyphs.log(glyphs.div(exp.string, exp2.string)))
        else:
            if exp2.is1():
                typeStr = "Entropy"
                symbStr = glyphs.sum(glyphs.mul(
                    exp.string, glyphs.log(exp.string)))
            else:
                typeStr = "Kullback–Leibler divergence"
                symbStr = glyphs.sum(glyphs.mul(exp.string,
                    glyphs.log(glyphs.div(exp.string, exp2.string))))

        Expression.__init__(self, typeStr, symbStr)

        self.Exp  = exp
        self.Exp2 = exp2

    def __len__(self):
        return len(self.Exp)

    def eval(self, ind=None):
        x = np.array(self.Exp.eval(ind)).ravel()
        y = np.array(self.Exp2.eval(ind)).ravel()
        return cvx.matrix(x.dot(np.log(x/y)), (1, 1))

    @_scalar_argument
    def __add__(self, term):
        if isinstance(term, AffinExp):
            return self + KullbackLeibler(term, term / np.e)
        elif isinstance(term, KullbackLeibler):
            return KullbackLeibler(
                (self.Exp[:] // term.Exp[:]), (self.Exp2[:] // term.Exp2[:]))
        else:
            return NotImplemented

    def __radd__(self, term):
        return self.__add__(term)

    @_scalar_argument
    def __lt__(self, rhs):
        if isinstance(rhs, AffinExp):
            return KullbackLeiblerConstraint(self, rhs)
        else:
            return NotImplemented


class QuadExp(Expression):
    """
    Quadratic expression.

    **Overloaded operators**

        :``+``: addition (with an affine or a quadratic expression)
        :``-``: unitary minus or substraction (of an affine or a quadratic
            expression)
        :``*``: multiplication (by a scalar or a constant affine expression)
        :``<``: less **or equal** than (a quadratic or affine expression)
        :``>``: greater **or equal** than (a quadratic or affine expression).
    """
    def __init__(self, quad, aff, string, LR=None):
        Expression.__init__(self, "Quadratic Expression", string)
        self._size = (1,1)
        self.quad = quad
        """Dictionary of quadratic forms, stored as matrices representing
        bilinear forms with respect to two vectorized variables, and indexed by
        tuples of instances of the class :class:`Variable
        <picos.expressions.Variable>`."""
        self.aff = aff
        """The affine part of the quadratic expression."""
        self.LR = LR
        """
        Stores a factorization of the quadratic expression, if the expression
        was entered in a factorized form. We have:

            * ``LR=None`` when no factorization is known,
            * ``LR=(aff,None)`` when the expression is equal to ``‖aff‖²``, and
            * ``LR=(aff1,aff2)`` when the expression is equal to ``aff1*aff2``.
        """

    def copy(self):
        import copy
        qdcopy = {}
        for ij, m in self.quad.items():
            qdcopy[ij] = copy.deepcopy(m)

        if self.aff is None:
            affcopy = None
        else:
            affcopy = self.aff.copy()

        if self.LR is None:
            lrcopy = None
        else:
            if self.LR[1] is None:
                lrcopy = (self.LR[0].copy(), None)
            else:
                lrcopy = (self.LR[0].copy(), self.LR[1].copy())
        return QuadExp(qdcopy, affcopy, self.string, lrcopy)

    def eval(self, ind=None):
        if not self.LR is None:
            ex1 = self.LR[0].eval(ind)
            if self.LR[1] is None:
                val = (ex1.T * ex1)
            else:
                if self.LR[0].size != (1, 1) or self.LR[1].size != (1, 1):
                    raise Exception(
                        'QuadExp of size (1,1) only are implemented')
                else:
                    ex2 = self.LR[1].eval(ind)
                    val = (ex1 * ex2)

        else:
            if not self.aff is None:
                val = self.aff.eval(ind)
            else:
                val = cvx.matrix(0., (1, 1))

            for i, j in self.quad:
                if ind is None:
                    if not i.is_valued():
                        raise Exception(i + ' is not valued')
                    if not j.is_valued():
                        raise Exception(j + ' is not valued')
                    xi = i.valueAsMatrix[:]
                    xj = j.valueAsMatrix[:]
                else:
                    if ind not in i.value_alt:
                        raise Exception(
                            i+' does not have a value for the index '+str(ind))
                    if ind not in j.value_alt:
                        raise Exception(
                            j+' does not have a value for the index '+str(ind))
                    xi = i.value_alt[ind][:]
                    xj = j.value_alt[ind][:]
                val = val + xi.T * self.quad[i, j] * xj

        return cvx.matrix(val, (1, 1))

    def nnz(self):
        nz = 0
        for ij in self.quad:
            nz += len(self.quad[ij].I)
        return nz

    @_scalar_argument
    def __mul__(self, fact):
        if isinstance(fact, AffinExp):
            if not fact.isconstant():
                raise ValueError("May only multiply a quadratic expression with"
                    " a constant.")

            selfcopy = self.copy()

            for ij in selfcopy.quad:
                selfcopy.quad[ij] = fact.eval()[0] * selfcopy.quad[ij]

            selfcopy.aff = fact * selfcopy.aff
            selfcopy.string = glyphs.mul(fact.string, self.string)

            if not self.LR is None:
                if self.LR[1] is None and (
                        fact.eval()[0] >= 0):  # Norm squared
                    selfcopy.LR = (
                        float(np.sqrt(fact.eval())) * self.LR[0], None)
                elif self.LR[1] is None and (fact.eval()[0] < 0):
                    selfcopy.LR = None
                else:
                    selfcopy.LR = (fact * self.LR[0], self.LR[1])

            return selfcopy
        else:
            return NotImplemented

    def __rmul__(self, fact):
        return self * fact

    @_scalar_argument
    def __div__(self, divisor):
        if isinstance(divisor, AffinExp):
            if divisor.isconstant():
                value = divisor.value
            else:
                raise TypeError(
                    "You may only divide a quadratic expression by a constant.")

            if value == 0:
                raise ValueError(
                    "Tried to divide {} by zero.".format(self.string))

            division = self * (1.0 / value)
            division.string = glyphs.div(self.string, divisor.string)
            return division
        else:
            return NotImplemented

    @_scalar_argument
    def __add__(self, term):
        if isinstance(term, AffinExp) or isinstance(term, QuadExp):
            selfcopy = self.copy()
            selfcopy += term
            return selfcopy
        else:
            return NotImplemented

    def __radd__(self, term):
        return self.__add__(term)

    @_scalar_argument
    def __iadd__(self, term):
        if isinstance(term, QuadExp):
            for ij in self.quad:
                if ij in term.quad:
                    try:
                        self.quad[ij] += term.quad[ij]
                    except TypeError as ex:
                        self.quad[ij] = self.quad[ij] + term.quad[ij]

            for ij in term.quad:
                if not (ij in self.quad):
                    self.quad[ij] = term.quad[ij]

            self.aff += term.aff
            self.LR = None
            self.string = glyphs.cleverAdd(self.string, term.string)

            return self
        elif isinstance(term, AffinExp):
            if not term.is0():
                expQE = QuadExp({}, term, term.string)
                self += expQE
            return self
        else:
            return NotImplemented

    def __neg__(self):
        selfneg = self*(-1)
        selfneg.string = glyphs.cleverNeg(self.string)
        return selfneg

    def __sub__(self, term):
        return self + (-term)

    def __rsub__(self, term):
        return term + (-self)

    @_scalar_argument
    def __lt__(self, exp):
        if isinstance(exp, QuadExp):
            if self.LR is not None and self.LR[1] is None \
            and exp.LR is not None:
                if exp.LR[1] is not None:
                    return RSOCConstraint(self.LR[0], exp.LR[0], exp.LR[1])
                else:
                    return SOCConstraint(self.LR[0], exp.LR[0])
            else:
                return QuadConstraint(self - exp)
        elif isinstance(exp, AffinExp):
            R = AffinExp.fromScalar(1.0)

            return self < QuadExp({}, exp, exp.string, LR = (exp, R))
        else:
            return NotImplemented

    @_scalar_argument
    def __gt__(self, exp):
        if isinstance(exp, QuadExp):
            if exp.LR is not None and exp.LR[1] is None:
                # A squared norm.
                return exp < self
            else:
                return -self < -exp
        elif isinstance(exp, AffinExp):
            if exp.isconstant():
                if self.LR is not None:
                    expRoot = AffinExp.fromScalar(exp.value**0.5)
                    expRoot.string = glyphs.power(exp.string, glyphs.div(1, 2))

                    return Norm(expRoot)**2 < self
                else:
                    return exp < self
            else:
                return -self < -exp
        else:
            return NotImplemented


class GeneralFun(Expression):
    """A class storing a scalar function, applied to an affine expression."""
    def __init__(self, fun, Exp, funstring):
        Expression.__init__(self, "General Function",
            glyphs.makeFunction(funstring)(Exp.string))

        self.fun = fun
        r"""The function ``f`` applied to the affine expression.
                This function must take in argument a
                :func:`cvxopt sparse matrix <cvxopt:cvxopt.spmatrix>` ``X``.
                Moreover, the call ``fx,grad,hess=f(X)``
                must return the function value :math:`f(X)` in ``fx``,
                the gradient :math:`\nabla f(X)` in the
                :func:`cvxopt matrix <cvxopt:cvxopt.matrix>` ``grad``,
                and the Hessian :math:`\nabla^2 f(X)` in the
                :func:`cvxopt sparse matrix <cvxopt:cvxopt.spmatrix>` ``hess``.
                """
        self.Exp = Exp
        """The affine expression to which the function is applied"""
        self.funstring = funstring
        """a string representation of the function name"""

    def eval(self, ind=None):
        val = self.Exp.eval(ind)
        o, g, h = self.fun(val)
        return cvx.matrix(o, (1, 1))


class GeoMeanExp(Expression):
    """A class storing the geometric mean of a multidimensional expression.

       **Overloaded operator**

            :``>``: greater **or equal** than (the rhs must be a scalar affine
                expression)
    """
    def __init__(self, exp):
        Expression.__init__(
            self, "Geometric Mean", glyphs.makeFunction("geomean")(exp.string))

        self.exp = exp
        """The affine expression to which the geomean is applied"""

    def eval(self, ind=None):
        val = self.exp.eval(ind)
        dim = self.exp.size[0] * self.exp.size[1]
        return cvx.matrix(np.prod(val)**(1.0 / dim), (1, 1))

    @_scalar_argument
    def __gt__(self, exp):
        if isinstance(exp, AffinExp):
            return GeoMeanConstraint(self, exp)
        else:
            return NotImplemented


class NormP_Exp(Expression):
    """
    A class storing the entrywise p-norm of a multidimensional expression.

    Use the function :func:`picos.norm() <picos.tools.norm>` to create an
    instance of this class. This class can also be used to store the
    :math:`L_{p,q}` norm of a matrix.

    Generalized norms are also defined for :math:`p < 1`, by using the usual
    formula :math:`\operatorname{norm}(\\mathbf{x},p) :=
    \\Big(\\sum_i x_i^p\\Big)^{1/p}`. Note that this function is concave (for
    :math:`p<1`) over the set of vectors with nonnegative coordinates. When a
    constraint of the form :math:`\operatorname{norm}(\\mathbf{x},p) > t` with
    :math:`p \\leq 1` is entered, PICOS implicitely forces :math:`\\mathbf{x}`
    to be a nonnegative vector.

    **Overloaded operator**

        :``<``: less **or equal** than (a scalar affine expression, p >= 1)
        :``>``: greater **or equal** than (a scalar affine expression, p <= 1)
    """
    def __init__(self, exp, numerator, denominator=1, num2=None, den2=1):
        # TODO: Convert numerators and denominators to suitable type here.

        p = float(numerator) / float(denominator)
        q = float(num2) / float(den2) if num2 is not None else None

        # Note that string formatting instead of glyphs is used for p and q as
        # they do not appear as an expression but as part of a function name.
        # TODO: Add a helper function to format fractional numbers.
        if denominator == 1:
            pstr = "{:g}".format(float(numerator))
        else:
            pstr = "{:g}/{:g}".format(float(numerator), float(denominator))

        if q is None:
            pass
        elif den2 == 1:
            qstr = "{:g}".format(float(num2))
        else:
            qstr = "{:g}/{:g}".format(float(num2), float(den2))

        if p < 0 or denominator != 1:
            pstr = "({})".format(pstr)
        if q is not None and (q < 0 or den2 != 1):
            qstr = "({})".format(qstr)

        if q is None:
            symbStr = glyphs.pnorm(exp.string, pstr)
            typeStr = "p-Norm" if p >= 1 else "Generalized p-Norm"
        else:
            if p >= 1 and q >= 1:
                symbStr = glyphs.pqnorm(exp.string, pstr, qstr)
                typeStr = "(p,q)-Norm"
            else:
                raise ValueError('(p,q) norm is only implemented for p,q >=1')

        Expression.__init__(self, typeStr, symbStr)

        self.exp = exp
        """The affine expression to which the p-norm is applied"""

        self.numerator = numerator
        """numerator of p"""

        self.denominator = denominator
        """denominator of p"""

        self.num2 = num2
        """numerator of q"""

        self.den2 = den2
        """denominator of q"""

    def eval(self, ind=None):
        val = self.exp.eval(ind)
        p = float(self.numerator) / float(self.denominator)
        if self.num2 is not None:
            q = float(self.num2) / float(self.den2)
            return np.linalg.norm([np.linalg.norm(list(val[i, :]), q)
                                   for i in range(val.size[0])], p)
        else:
            return np.linalg.norm([vi for vi in val], p)

    @_scalar_argument
    def __lt__(self, exp):
        if float(self.numerator) / float(self.denominator) < 1:
            raise TypeError("May only upper bound a convex p-norm (p >= 1).")

        if isinstance(exp, AffinExp):
            if self.num2 is None:
                return PNormConstraint(self, Constraint.LE, exp)
            else:
                return PQNormConstraint(self, exp)
        else:
            return NotImplemented

    @_scalar_argument
    def __gt__(self, exp):
        p = float(self.numerator) / float(self.denominator)
        if p > 1 or p == 0:
            raise TypeError(
                "May only lower bound a concave p-norm (p <= 1, p != 0).")

        if isinstance(exp, AffinExp):
            return PNormConstraint(self, Constraint.GE, exp)
        else:
            return NotImplemented


class TracePow_Exp(Expression):
    """
    The :math:`p`-th power of a scalar, or more generally the trace of the
    :math:`p`-th power of a symmetric matrix, for some rational :math:`p`.

    The exponent :math:`p` is given in the form of a numerator/denominator pair.

    You can use the shorthand function
    :func:`picos.tracepow() <picos.tools.tracepow>` and the overloaded
    exponentiation operator ``**`` to create an instance of this class.

    Note that this expression is concave for :math:`0 \\leq p \\leq 1` and
    convex for both :math:`p \\leq 0` and `:math:p \\geq 1` for a non-negative
    (positive semidefinite) base. If the expression is concave, then an
    additional positive semdidefinite coefficient matrix :math:`M` may be given
    so that the expression describes :math:`\operatorname{trace}(M X^p)`.

    .. warning ::

        The symmetry of the base matrix and the positive semidefiniteness of the
        optional coefficient matrix are not checked or enforced by PICOS.

    **Overloaded operator**

        :``<``: less **or equal** than (a scalar affine expression, for a convex
            power)
        :``>``: greater **or equal** than (a scalar affine expression, for a
            concave power)
    """
    def __init__(self, exp, numerator, denominator=1, M=None):
        p = float(numerator) / float(denominator)

        if denominator == 1:
            pstr = glyphs.scalar(numerator)
        else:
            pstr = glyphs.div(numerator, denominator)

        if M is None:
            if exp.size == (1, 1):
                typeStr = "Power"
                symbStr = glyphs.power(exp.string, pstr)
            else:
                typeStr = "Trace of Power"
                symbStr = glyphs.trace(glyphs.power(exp.string, pstr))
        else:
            if exp.size == (1, 1):
                typeStr = "Power"
                symbStr = glyphs.mul(M.string, glyphs.power(exp.string, pstr))
            else:
                typeStr = "Trace of Power"
                symbStr = glyphs.trace(glyphs.mul(
                    M.string, glyphs.power(exp.string, pstr)))

        Expression.__init__(self, typeStr, symbStr)

        if exp.size[0] != exp.size[1]:
            raise TypeError('Matrix must be square')

        self.exp = exp
        """The affine expression to which the p-norm is applied"""

        self.numerator = numerator
        """numerator of p"""

        self.denominator = denominator
        """denominator of p"""

        self.dim = exp.size[0]
        """dimension of ``exp``"""

        self.M = None
        """the coef matrix"""

        # TODO: Verify that M is PSD.
        if M is not None:
            if p < 0 or p > 1:
                raise ValueError("A coefficient matrix is only accepted in the "
                    "case of a concave power (0 <= p <= 1).")
            if not M.isconstant():
                raise ValueError("The coefficient matrix must be constant.")
            if not M.size == exp.size:
                raise TypeError("The coefficient matrix must have the same "
                    "size as the bae matrix.")
            self.M = M

    def eval(self, ind=None):
        val = cvx.matrix(self.exp.eval(ind))
        p = float(self.numerator) / float(self.denominator)

        if self.M is None:
            ev = np.linalg.eigvalsh(np.matrix(val))
            return sum([vi**p for vi in ev])
        else:
            Mval = self.M.eval(ind)
            U, S, V = np.linalg.svd(val)
            Xp = cvx.matrix(U) * cvx.spdiag([s**p for s in S]) * cvx.matrix(V)
            return np.trace(Mval * Xp)

    @_scalar_argument
    def __lt__(self, exp):
        p = float(self.numerator) / float(self.denominator)

        if p > 0 and p < 1:
            raise TypeError(
                "May only upper bound a convex power (p <= 0 or p >= 1).")

        if p == 0:
            return AffinExp.fromScalar(self.dim) < exp
        elif p == 1:
            if self.M is not None:
                return (self.M | self.exp) < exp
            elif self.dim == 1:
                return self.exp < exp
            else:
                return ("I" | self.exp) < exp
        elif p == 2 and self.dim == 1:
            return self.exp**2 < exp

        assert p < 0 or p > 1
        assert self.M is None

        if isinstance(exp, AffinExp):
            return TracePowConstraint(self, Constraint.LE, exp)
        else:
            return NotImplemented

    @_scalar_argument
    def __gt__(self, exp):
        p = float(self.numerator) / float(self.denominator)

        if p < 0 or p > 1:
            raise TypeError(
                "May only lower bound a concave power (p >= 0 and p <= 1).")

        if p == 0:
            return AffinExp.fromScalar(self.dim) > exp
        elif p == 1:
            if self.M is not None:
                return (self.M | self.exp) > exp
            elif self.dim == 1:
                return self.exp > exp
            else:
                return ("I" | self.exp) > exp

        if isinstance(exp, AffinExp):
            return TracePowConstraint(self, Constraint.GE, exp)
        else:
            return NotImplemented


class DetRootN_Exp(Expression):
    """
    A class storing the :math:`n`-th root of the determinant of a positive
    semidefinite matrix.

    Use the function :func:`picos.detrootn <picos.tools.detrootn>` to create
    an instance of this class.

    Note that the matrix :math:`X` is forced to be positive semidefinite
    when a constraint of the form ``t < pic.detrootn(X)`` is added.

    **Overloaded operator**

        :``>``: greater **or equal** than (a scalar affine expression)
    """
    def __init__(self, exp):
        if exp.size[0] != exp.size[1]:
            raise TypeError('Matrix must be square')

        Expression.__init__(self, "n-th Root of a Determinant",
            glyphs.power(glyphs.det(exp.string), glyphs.div(1, exp.size[0])))

        self.exp = exp
        """The affine expression to which the det-root-n is applied"""

        self.dim = exp.size[0]
        """dimension of ``exp``"""

    def eval(self, ind=None):
        val = self.exp.eval(ind)
        if not isinstance(val, cvx.base.matrix):
            val = cvx.matrix(val)
        return (np.linalg.det(np.matrix(val)))**(1. / self.dim)

    @_scalar_argument
    def __gt__(self, exp):
        if isinstance(exp, AffinExp):
            return DetRootNConstraint(self, exp)
        else:
            return NotImplemented


class Sum_k_Largest_Exp(Expression):
    """
    A class storing the sum of the :math:`k` largest elements of an
    :class:`AffinExp <picos.expressions.AffinExp>`, or the sum of its :math:`k`
    largest eigenvalues (for a square matrix expression).

    Use the function :func:`picos.sum_k_largest <picos.tools.sum_k_largest>`
    or :func:`picos.sum_k_largest_lambda <picos.tools.sum_k_largest_lambda>`
    to create an instance of this class.

    Note that the matrix :math:`X` is assumed to be symmetric when a constraint
    of the form ``pic.sum_k_largest_lambda(X,k) < t`` is added.

    **Overloaded operator**

        :``<``: smaller **or equal** than (a scalar affine expression)
    """
    def __init__(self, exp, k, eigenvals=False):
        k = int(k)

        if eigenvals:
            if exp.size[0] != exp.size[1]:
                raise TypeError(
                    "Can only sum the largest eigenvalues of a square matrix.")

            typeStr = "Sum of Largest Eigenvalues"
            if k == 1:
                symbStr = glyphs.makeFunction(
                    "{}_max".format(glyphs.lambda_()))(exp.string)
            elif k == exp.size[0]:
                symbStr = glyphs.trace(exp.string)
            else:
                symbStr = glyphs.makeFunction(
                    "sum_{}_largest_{}".format(k, glyphs.lambda_()))(exp.string)
        else:
            typeStr = "Sum of Largest Elements"
            if k == 1:
                symbStr = glyphs.max(exp.string)
            elif k == exp.size[0] * exp.size[1]:
                symbStr = glyphs.sum(exp.string)
            else:
                symbStr = glyphs.makeFunction(
                    "sum_{}_largest".format(k))(exp.string)

        Expression.__init__(self, typeStr, symbStr)

        self.exp = exp
        """The affine expression to which the sum_k_largest is applied"""

        self.k = k
        """The number of elements to sum"""

        self.eigenvalues = eigenvals
        """whether this is a sum of k largest eigenvalues (for symmetric
        matrices)"""

    def eval(self, ind=None):
        val = self.exp.eval(ind)
        if not isinstance(val, cvx.base.matrix):
            val = cvx.matrix(val)

        if self.eigenvalues:
            ev = sorted(np.linalg.eigvalsh(val))
        else:
            ev = sorted(val)

        return sum(ev[-self.k:])

    @_scalar_argument
    def __lt__(self, exp):
        if isinstance(exp, AffinExp):
            return SumExtremesConstraint(self, Constraint.LE, exp)
        else:
            return NotImplemented


class Sum_k_Smallest_Exp(Expression):
    """
    A class storing the sum of the k smallest elements of an :class:`AffinExp
    <picos.expressions.AffinExp>`, or the sum of its k smallest eigenvalues (for
    a square matrix expression).

    Use the function :func:`picos.sum_k_smallest() <picos.tools.sum_k_smallest>`
    or :func:`picos.sum_k_smallest_lambda() <picos.tools.sum_k_smallest_lambda>`
    to create an instance of this class.

    Note that the matrix :math:`X` is assumed to be symmetric when a constraint
    of the form ``pic.sum_k_smallest_lambda(X,k) > t`` is added.

    **Overloaded operator**

        :``>``: greater **or equal** than (a scalar affine expression)
    """
    def __init__(self, exp, k, eigenvals=False):
        if eigenvals:
            if exp.size[0] != exp.size[1]:
                raise TypeError(
                    "Can only sum the smallest eigenvalues of a square matrix.")

            typeStr = "Sum of Smallest Eigenvalues"
            if k == 1:
                symbStr = glyphs.makeFunction(
                    "{}_min".format(glyphs.lambda_()))(exp.string)
            elif k == exp.size[0]:
                symbStr = glyphs.trace(exp.string)
            else:
                symbStr = glyphs.makeFunction(
                    "sum_{}_smallest_{}".format(k, glyphs.lambda_()))(exp.string)
        else:
            typeStr = "Sum of Smallest Elements"
            if k == 1:
                symbStr = glyphs.min(exp.string)
            elif k == exp.size[0] * exp.size[1]:
                symbStr = glyphs.sum(exp.string)
            else:
                symbStr = glyphs.makeFunction(
                    "sum_{}_smallest".format(k))(exp.string)

        Expression.__init__(self, typeStr, symbStr)

        self.exp = exp
        """The affine expression to which sum_k_smallest is applied"""

        self.k = k
        """The number of elements to sum"""

        self.eigenvalues = eigenvals
        """whether this is a sum of k smallest eigenvalues (for symmetric
        matrices)"""

    def eval(self, ind=None):
        val = self.exp.eval(ind)
        if not isinstance(val, cvx.base.matrix):
            val = cvx.matrix(val)

        if self.eigenvalues:
            ev = sorted(np.linalg.eigvalsh(val))
        else:
            ev = sorted(val)

        return sum(ev[:self.k])

    @_scalar_argument
    def __gt__(self, exp):
        if isinstance(exp, AffinExp):
            return SumExtremesConstraint(self, Constraint.GE, exp)
        else:
            return NotImplemented


class Variable(AffinExp):
    """This class stores a variable."""
    def __init__(self, parent_problem, name, size, Id, startIndex,
            vtype='continuous', lower=None, upper=None):
        # This needs to be the first line in `__init__`.
        self._atVariableCreation = True
        """A flag that tells `_handle_late_modification` whether modifications
        to the variable happen during variable creation or at a later time."""

        # attributes of the parent class (AffinExp)
        idmat = svecm1_identity(vtype, size)
        AffinExp.__init__(self, factors={self: idmat}, constant=None, size=size,
            string=name, typeBaseStr = "Variable")

        self.name = name
        """The name of the variable (str)"""

        self.parent_problem = parent_problem
        """The Problem instance to which this variable belongs"""

        self.origin = None
        """The metaconstraint that created this variable, if any."""

        self.Id = Id
        """An integer index (obsolete)"""
        self._vtype = vtype

        self._startIndex = startIndex

        self._endIndex = None
        """end position in the global vector of all variables"""

        if vtype in ('symmetric',):
            self._endIndex = startIndex + \
                (size[0] * (size[0] + 1)) // 2  # end position +1
        else:
            self._endIndex = startIndex + size[0] * size[1]  # end position +1

        self._value = None

        self.value_alt = {}  # alternative values for solution pools

        # dictionary of (lower,upper) bounds ( +/-infinite if the index is not
        # in the dict)
        self._bnd = NonWritableDict()

        self.semiDef = 0
        """Conditionally evaluates to True if this is a symmetric variable
        subject to X >> 0. Counts the number of constraints stating this."""

        self._bndtext = ''

        if not(lower is None):
            self.set_lower(lower)

        if not(upper is None):
            self.set_upper(upper)

        # This needs to be the last line in `__init__`.
        self._atVariableCreation = False

    # HACK: Variables support some modifications, so overwrite Expression's
    #       typeStr member.
    typeStr = property(lambda self: "{} {} {}".format(
        glyphs.size(*self.size), self.vtype.title(), self.typeBaseStr))

    def __iadd__(self, term):
        raise NotImplementedError(
            'variable must not be changed inplace. Try to cast the first term '
            'of the sum as an AffinExp, e.g. by adding 0 to it.')

    def _handle_late_modification(self):
        """
        Informs or resets solver instances if the variable is critically altered
        after creation, for instance when the bounds change.
        """
        # TODO: Reset only solvers that already know about the variable. This
        #       requires a common interface for the variables known to a solver.
        if not self._atVariableCreation:
            self.parent_problem.reset_solver_instances()

    @property
    def dim(self):
        """
        The algebraic dimension of the variable.
        """
        n, m = self.size
        if self.vtype is "symmetric":
            return (n*(n + 1)) // 2
        elif self.vtype is "antisym":
            return (n*(n - 1)) // 2
        else:
            return n*m

    @property
    def bnd(self):
        """
        ``var.bnd[i]`` returns a tuple ``(lo,up)`` of lower and upper bounds for
        the i-th element of the variable ``var``. None means +/- infinite.
        if ``var.bnd[i]`` is not defined, then ``var[i]`` is unbounded.
        """
        return self._bnd

    def bound_constraint(self):
        """
        Returns the variable bounds in the form of a PICOS multidimensional
        :class:`affine constraint <picos.constraints.AffineConstraint>`.
        """
        J, V, b = [], [], []
        for localVarIndex, (lower, upper) in self._bnd.items():
            if lower is not None:
                J.append(localVarIndex)
                V.append(-1.0)
                b.append(-lower)

            if upper is not None:
                J.append(localVarIndex)
                V.append(1.0)
                b.append(upper)

        numCons = len(b)
        I = range(numCons)
        A = AffinExp(
            factors = {self: cvx.spmatrix(V, I, J)}, size = (numCons, 1),
            string = self.string + "_bounds_lhs")

        return A < b

    @property
    def startIndex(self):
        """starting position in the global vector of all variables"""
        return self._startIndex

    @property
    def endIndex(self):
        """end position in the global vector of all variables"""
        return self._endIndex

    @property
    def vtype(self):
        """
        one of the following strings:

            * 'continuous' (continuous variable)
            * 'binary'     (binary 0/1 variable)
            * 'integer'    (integer variable)
            * 'symmetric'  (symmetric matrix variable)
            * 'antisym'    (antisymmetric matrix variable)
            * 'complex'    (complex matrix variable)
            * 'hermitian'  (complex hermitian matrix variable)
            * 'semicont'   (semicontinuous variable
                [can take the value 0 or any other admissible value])
            * 'semiint'    (semi integer variable
                [can take the value 0 or any other integer admissible value])
        """
        return self._vtype

    @vtype.setter
    def vtype(self, value):
        if not(
            value in [
                'symmetric',
                'antisym',
                'hermitian',
                'complex',
                'continuous',
                'binary',
                'integer',
                'semicont',
                'semiint']):
            raise ValueError('unknown variable type')
        if self._vtype not in ('symmetric',) and value in ('symmetric',):
            raise Exception(
                'change to symmetric is forbiden because of sym-vectorization')
        if self._vtype in ('symmetric',) and value not in ('symmetric',):
            raise Exception('change from symmetric is forbiden because of '
                'sym-vectorization')
        if self._vtype not in ('antisym',) and value in ('antisym',):
            raise Exception(
                'change to antisym is forbiden because of sym-vectorization')
        if self._vtype in ('antisym',) and value not in ('antisym',):
            raise Exception(
                'change from antisym is forbiden because of sym-vectorization')
        self._vtype = value
        if ('[' in self.name and
                ']' in self.name and
                self.name.split('[')[0] in self.parent_problem.listOfVars):
            vlist = self.name.split('[')[0]
            if all([vi.vtype == value
                    for vi in self.parent_problem.get_variable(vlist)]):
                self.parent_problem.listOfVars[vlist]['vtype'] = value
            else:
                self.parent_problem.listOfVars[vlist]['vtype'] = 'different'

    def set_lower(self, lo):
        """
        sets a lower bound to the variable (lo may be scalar or a matrix of the
        same size as the variable ``self``). Entries smaller than -INFINITY =
        -1e16 are ignored
        """
        lowexp = retrieve_matrix(lo, self.size)[0]
        if self.vtype in ('symmetric',):
            lowexp = svec(lowexp)
        if self.vtype in ('hermitian', 'complex'):
            raise Exception('lower bound not supported for complex variables')
        for i in range(lowexp.size[0] * lowexp.size[1]):
            li = lowexp[i]
            if li > -INFINITY:
                bil, biu = self.bnd.get(i, (None, None))
                self.bnd._set(i, (li, biu))

        if ('low' not in self._bndtext) and (
                'nonnegative' not in self._bndtext):
            if lowexp:
                self._bndtext += ', bounded below'
            else:
                self._bndtext += ', nonnegative'
        elif ('low' in self._bndtext):
            if not(lowexp):
                self._bndtext.replace('bounded below', 'nonnegative')
            elif ('lower' in self._bndtext):
                self._bndtext.replace('some lower bounds', 'bounded below')
        else:
            if lowexp:
                self._bndtext.replace('nonnegative', 'bounded below')

        self._handle_late_modification()

    def set_sparse_lower(self, indices, bnds):
        """
        sets the lower bound bnds[i] to the index indices[i] of the variable.

        For a symmetric matrix variable, bounds on elements in the upper
        triangle are ignored.

        :param indices: list of indices, given as integers (column major order)
            or tuples (i,j).
        :type indices: ``list``
        :param bnds: list of lower bounds.
        :type lower: ``list``

        .. Warning::

            This function does not modify the existing bounds on elements other
            than those specified in ``indices``.

        **Example:**

        >>> import picos as pic
        >>> P = pic.Problem()
        >>> X = P.add_variable('X',(3,2),lower = 0)
        >>> X.set_sparse_upper([0,(0,1),1],[1,2,0])
        >>> X.bnd #doctest: +NORMALIZE_WHITESPACE
        {0: (0.0, 1.0),
         1: (0.0, 0.0),
         2: (0.0, None),
         3: (0.0, 2.0),
         4: (0.0, None),
         5: (0.0, None)}
        """
        if self.vtype in ('hermitian', 'complex'):
            raise Exception('lower bound not supported for complex variables')
        s0 = self.size[0]
        vv = []
        ii = []
        jj = []
        for idx, lo in zip(indices, bnds):
            if isinstance(idx, int):
                idx = (idx % s0, idx // s0)
            if self.vtype in ('symmetric',):
                (i, j) = idx
                if i > j:
                    ii.append(i)
                    jj.append(j)
                    vv.append(lo)
                    ii.append(j)
                    jj.append(i)
                    vv.append(lo)
                elif i == j:
                    ii.append(i)
                    jj.append(i)
                    vv.append(lo)
            ii.append(idx[0])
            jj.append(idx[1])
            vv.append(lo)
        spLO = spmatrix(vv, ii, jj, self.size)
        if self.vtype in ('symmetric',):
            spLO = svec(spLO)
        for i, j, v in zip(spLO.I, spLO.J, spLO.V):
            ii = s0 * j + i
            bil, biu = self.bnd.get(ii, (None, None))
            self.bnd._set(ii, (v, biu))

        if ('nonnegative' in self._bndtext):
            self._bndtext.replace('nonnegative', 'bounded below')
        elif ('low' not in self._bndtext):
            self._bndtext += ', some lower bounds'

        self._handle_late_modification()

    def set_upper(self, up):
        """
        sets an upper bound to the variable (up may be scalar or a matrix of the
        same size as the variable ``self``). Entries larger than INFINITY = 1e16
        are ignored
        """
        upexp = retrieve_matrix(up, self.size)[0]
        if self.vtype in ('symmetric',):
            upexp = svec(upexp)
        if self.vtype in ('hermitian', 'complex'):
            raise Exception('lower bound not supported for complex variables')
        for i in range(upexp.size[0] * upexp.size[1]):
            ui = upexp[i]
            if ui < INFINITY:
                bil, biu = self.bnd.get(i, (None, None))
                self.bnd._set(i, (bil, ui))
        if 'above' not in self._bndtext and 'upper' not in self._bndtext \
        and 'nonpositive' not in self._bndtext:
            if upexp:
                self._bndtext += ', bounded above'
            else:
                self._bndtext += ', nonpositive'
        elif ('above' in self._bndtext):
            if not(upexp):
                self._bndtext.replace('bounded above', 'nonpositive')
        elif ('upper' in self._bndtext):
            self._bndtext.replace('some upper bounds', 'bounded above')
        else:
            if upexp:
                self._bndtext.replace('nonpositive', 'bounded above')

        self._handle_late_modification()

    def set_sparse_upper(self, indices, bnds):
        """
        sets the upper bound bnds[i] to the index indices[i] of the variable.

        For a symmetric matrix variable, bounds on elements in the upper
        triangle are ignored.

        :param indices: list of indices, given as integers (column major order)
            or tuples (i,j).
        :type indices: ``list``
        :param bnds: list of upper bounds.
        :type lower: ``list``

        .. Warning::

            This function does not modify the existing bounds on elements other
            than those specified in ``indices``.
        """
        if self.vtype in ('hermitian', 'complex'):
            raise Exception('lower bound not supported for complex variables')
        s0 = self.size[0]
        vv = []
        ii = []
        jj = []
        for idx, up in zip(indices, bnds):
            if isinstance(idx, int):
                idx = (idx % s0, idx // s0)
            if self.vtype in ('symmetric',):
                (i, j) = idx
                if i > j:
                    ii.append(i)
                    jj.append(j)
                    vv.append(up)
                    ii.append(j)
                    jj.append(i)
                    vv.append(up)
                elif i == j:
                    ii.append(i)
                    jj.append(i)
                    vv.append(up)
            else:
                ii.append(idx[0])
                jj.append(idx[1])
                vv.append(up)
        spUP = spmatrix(vv, ii, jj, self.size)
        if self.vtype in ('symmetric',):
            spUP = svec(spUP)
        for i, j, v in zip(spUP.I, spUP.J, spUP.V):
            ii = s0 * j + i
            bil, biu = self.bnd.get(ii, (None, None))
            self.bnd._set(ii, (bil, v))
        if ('nonpositive' in self._bndtext):
            self._bndtext.replace('nonpositive', 'bounded above')
        elif ('above' not in self._bndtext) and ('upper' not in self._bndtext):
            self._bndtext += ', some upper bounds'

        self._handle_late_modification()

    def eval(self, ind=None):
        if ind is None:
            if self._value is None:
                raise Exception(self.name + ' is not valued')
            else:
                if self.vtype in ('symmetric',):
                    return cvx.matrix(svecm1(self._value))
                else:
                    return cvx.matrix(self._value)
        else:
            if ind in self.value_alt:
                if self.vtype in ('symmetric',):
                    return cvx.matrix(svecm1(self.value_alt[ind]))
                else:
                    return cvx.matrix(self.value_alt[ind])
            else:
                raise Exception(
                    self.name +
                    ' does not have a value for the index ' +
                    str(ind))

    def set_value(self, value, index = None):
        value, _ = retrieve_matrix(value, self.size)
        n, m = self.size

        if self.vtype is "symmetric":
            s = (n*(n+1)) // 2

            if value.size == self.size:
                value = svec(value)
            elif value.size[0] == s:
                assert value.size[1] is 1, \
                    "retrieve_matrix was supposed to return a column vector."
            else:
                raise TypeError(
                    "Value for symmetric variable {} must be matrix of size {} "
                    "or vector of size {} (Dattorro's svec format)."
                    .format(self.string, glyphs.size(n, m), s))
        elif value.size != self.size:
            raise TypeError(
                "Value for variable {} must be matrix of size {}."
                .format(self.string, glyphs.size(n, m)))

        if self.vtype is "hermitian":
            v = (value - value.H)[:]

            if (v.H * v)[0].real > 1e-6:
                raise ValueError("Value for variable {} must be hermitian."
                    .format(self.string))
            else:
                value = 0.5 * (value + value.H)

        if index is not None:
            self.value_alt[index] = value
        else:
            self._value = value

    def del_value(self, index = None):
        if index is not None:
            self.value_alt.pop(index)
        else:
            self._value = None

    def __getitem__(self, index):
        """faster implementation of getitem for variable"""
        if self.vtype in ('symmetric',):
            return AffinExp.__getitem__(self, index)

        def indexstr(idx):
            if isinstance(idx, int):
                return str(idx)
            elif isinstance(idx, Expression):
                return idx.string

        def slicestr(sli):
            # single element
            if not (sli.start is None or sli.stop is None):
                sta = sli.start
                sto = sli.stop
                if isinstance(sta, int):
                    sta = new_param(str(sta), sta)
                if isinstance(sto, int):
                    sto = new_param(str(sto), sto)
                if (sto.__index__() == sta.__index__() + 1):
                    return sta.string
            # single element -1 (Expression)
            if (isinstance(sli.start, Expression) and sli.start.__index__()
                    == -1 and sli.stop is None and sli.step is None):
                return sli.start.string
            # single element -1
            if (isinstance(sli.start, int) and sli.start == -1
                    and sli.stop is None and sli.step is None):
                return '-1'
            ss = ''
            if not sli.start is None:
                ss += indexstr(sli.start)
            ss += ':'
            if not sli.stop is None:
                ss += indexstr(sli.stop)
            if not sli.step is None:
                ss += ':'
                ss += indexstr(sli.step)
            return ss

        if isinstance(index, Expression) or isinstance(index, int):
            ind = index.__index__()
            if ind < 0:
                rangeT = [self.size[0] * self.size[1] + ind]
            else:
                rangeT = [ind]
            newsize = (1, 1)
            indstr = indexstr(index)
        elif isinstance(index, slice):
            idx = index.indices(self.size[0] * self.size[1])
            rangeT = range(idx[0], idx[1], idx[2])
            newsize = (len(rangeT), 1)
            indstr = slicestr(index)
        elif isinstance(index, tuple):
            # simple common cases for fast implementation
            if isinstance(
                    index[0],
                    int) and isinstance(
                    index[1],
                    int):  # element
                ind0 = index[0]
                ind1 = index[1]
                if ind0 < 0:
                    ind0 = self.size[0] + ind0
                if ind1 < 0:
                    ind1 = self.size[1] + ind1
                rangeT = [ind1 * self.size[0] + ind0]
                newsize = (1, 1)
                indstr = indexstr(index[0]) + ',' + indexstr(index[1])
            elif isinstance(index[0], int) \
            and index[1] == slice(None, None, None):  # row
                ind0 = index[0]
                if ind0 < 0:
                    ind0 = self.size[0] + ind0
                rangeT = range(ind0, self.size[0] * self.size[1], self.size[0])
                newsize = (1, self.size[1])
                indstr = indexstr(index[0]) + ',:'

            elif isinstance(index[1], int) \
            and index[0] == slice(None, None, None):  # column
                ind1 = index[1]
                if ind1 < 0:
                    ind1 = self.size[1] + ind1
                rangeT = range(ind1 * self.size[0], (ind1 + 1) * self.size[0])
                newsize = (self.size[0], 1)
                indstr = ':,' + indexstr(index[1])
            else:
                if isinstance(
                        index[0],
                        Expression) or isinstance(
                        index[0],
                        int):
                    ind = index[0].__index__()
                    if ind == -1:
                        index = (slice(ind, None, None), index[1])
                    else:
                        index = (slice(ind, ind + 1, None), index[1])
                if isinstance(
                        index[1],
                        Expression) or isinstance(
                        index[1],
                        int):
                    ind = index[1].__index__()
                    if ind == -1:
                        index = (index[0], slice(ind, None, None))
                    else:
                        index = (index[0], slice(ind, ind + 1, None))
                idx0 = index[0].indices(self.size[0])
                idx1 = index[1].indices(self.size[1])
                rangei = range(idx0[0], idx0[1], idx0[2])
                rangej = range(idx1[0], idx1[1], idx1[2])
                rangeT = []
                for j in rangej:
                    rangei_translated = []
                    for vi in rangei:
                        rangei_translated.append(
                            vi + (j * self.size[0]))
                    rangeT.extend(rangei_translated)

                newsize = (len(rangei), len(rangej))
                indstr = slicestr(index[0]) + ',' + slicestr(index[1])

        sz = self.size[0] * self.size[1]
        nsz = len(rangeT)
        newfacs = {}
        II = range(nsz)
        JJ = rangeT
        VV = [1.] * nsz
        newfacs = {self: spmatrix(VV, II, JJ, (nsz, sz))}
        if not self.constant is None:
            newcons = self.constant[rangeT]
        else:
            newcons = None

        if indstr ==':' and self.size[1]==1:
            newstr = self.string
        else:
            newstr = glyphs.slice(self.string, indstr)
        # check size
        if newsize[0] == 0 or newsize[1] == 0:
            raise IndexError('slice of zero-dimension')
        return AffinExp(newfacs, newcons, newsize, newstr)


class Set:
    """
    Parent class for set expressions.
    """
    def __init__(self, typeStr, symbStr = None):
        self.typeStr = typeStr
        self.symbStr = symbStr

    def __repr__(self):
        if self.symbStr is not None:
            return glyphs.repr2(self.typeStr, self.symbStr)
        else:
            return glyphs.repr1(self.typeStr)

    def __str__(self):
        if self.symbStr is not None:
            return self.symbStr
        else:
            return glyphs.set(self.typeStr)

    string = property(__str__)


class Ball(Set):
    """
    Represents a ball of a given norm.

    ** Overloaded operators **

      :``>>``: membership of the right hand side in this set.
    """
    def __init__(self, p, radius):
        p = float(p) # Can be "inf".

        if p >= 1:
            typeStr = "L_{:g}-Ball of radius {:g}".format(p, radius)
            symbStr = None # TODO
        else:
            typeStr = "Generalized outer L_{:g}-Ball".format(p)
            symbStr = glyphs.set(glyphs.sep(
                glyphs.ge("x", 0), glyphs.ge(glyphs.pnorm("x", p), radius)))

        Set.__init__(self, typeStr, symbStr)

        self.p      = p
        self.radius = radius

    @_matrix_argument
    def __rshift__(self, exp):
        if isinstance(exp, AffinExp):
            if float(self.p) >= 1:
                return norm(exp, self.p) < self.radius
            else:
                return norm(exp, self.p) > self.radius
        else:
            return NotImplemented


class TruncatedSimplex(Set):
    """
    Represents a simplex, that can be intersected with the ball of radius 1 for
    the infinity-norm (truncation), and that can be symmetrized with respect to
    the origin.

    ** Overloaded operators **

      :``>>``: membership of the right hand side in this set.
    """
    def __init__(self, radius=1, truncated=False, nonneg=True):
        self.radius    = radius
        self.truncated = truncated
        self.nonneg    = nonneg

        if truncated:
            if nonneg:
                typeStr = "Truncated Simplex"
                symbStr = glyphs.set(glyphs.sep(glyphs.le(0, glyphs.le("x", 1)),
                    glyphs.le(glyphs.sum("x"), radius)))
            else:
                typeStr = "Symmetrized Truncated Simplex"
                symbStr = glyphs.set(glyphs.sep(glyphs.le(-1, glyphs.le("x", 1)),
                    glyphs.le(glyphs.sum(glyphs.abs("x")), radius)))
        else:
            if nonneg:
                if radius == 1:
                    typeStr = "Standard Simplex"
                else:
                    typeStr = "Simplex"
                symbStr = glyphs.set(glyphs.sep(glyphs.ge("x", 0),
                    glyphs.le(glyphs.sum("x"), radius)))
            else:
                typeStr = "L_1-Ball of radius {:g}".format(radius)
                symbStr = glyphs.set(glyphs.sep("x",
                    glyphs.le(glyphs.sum(glyphs.abs("x")), radius)))

        Set.__init__(self, typeStr, symbStr)

    @_matrix_argument
    def __rshift__(self, exp):
        if isinstance(exp, AffinExp):
            return SymTruncSimplexConstraint(self, exp)
        else:
            return NotImplemented


class ExponentialCone(Set):
    """
    Represents the cone
    :math:`\operatorname{closure}\\{(x,y,z): y \\exp(z/y) \\leq x, x,y > 0\\}`.

    ** Overloaded operators **

      :``>>``: membership of the right hand side in this set.
    """
    def __init__(self):
        typeStr = "Exponential Cone"
        symbStr = glyphs.closure(glyphs.set(glyphs.sep(
            glyphs.colVectorize("x", "y", "z"), ", ".join([
                glyphs.le(glyphs.mul("y",glyphs.exp(glyphs.div("z","y"))), "x"),
                glyphs.gt("x", 0),
                glyphs.gt("y", 0)
            ]))))

        Set.__init__(self, typeStr, symbStr)

    @_matrix_argument
    def __rshift__(self, exp):
        if isinstance(exp, AffinExp):
            if len(exp) != 3:
                raise TypeError("The member of an exponential cone must be "
                    "three-dimensional.")

            return ExpConeConstraint(exp)
        else:
            return NotImplemented
