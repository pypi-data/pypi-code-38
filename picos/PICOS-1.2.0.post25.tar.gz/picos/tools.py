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
# This file implements miscellaneous tools for both users and developers.
# TODO: Split this file by topic. Topics include:
#       - Algebraic functions. Should be lifted to the picos namespace via e.g.
#         "from algebra import *" inside __init__.py.
#       - Helper functions that the user does not need to know about. These
#         seem to be the functions starting with "_", and maybe a few others.
#-------------------------------------------------------------------------------

from __future__ import print_function, division
from warnings import warn
import re

try: # Python 3
    import builtins
except ImportError: # Python 2
    import __builtin__ as builtins

import cvxopt as cvx
import numpy as np

from . import glyphs

INTEGER_TYPES = tuple([int] + ([long] if hasattr(builtins, "long") else []))

builtin_sum = builtins.sum

def sum(lst, it=None, indices=None):
    """
    This is a replacement for Python's :func:`sum` that produces sensible string
    representations when summing PICOS expressions.

    :param lst: A list of :class:`expressions <picos.expressions.Expression>`,
        or a single affine expression whose elements shall be summed.
    :type lst: list or tuple or AffinExp
    :param it: DEPRECATED
    :param indices: DEPRECATED

    **Example:**

    >>> import picos
    >>> P = picos.Problem()
    >>> x = P.add_variable("x", 5)
    >>> e = [x[i]*x[i+1] for i in range(len(x) - 1)]
    >>> sum(e)
    <Quadratic Expression: x[0]·x[1] + x[1]·x[2] + x[2]·x[3] + x[3]·x[4]>
    >>> picos.sum(e)
    <Quadratic Expression: ∑(x[i]·x[i+1] : i ∈ [0…3])>
    >>> picos.sum(x) # The same as (x|1).
    <1×1 Affine Expression: ∑(x)>
    """
    from .expressions import Expression, AffinExp

    if it is not None or indices is not None:
        warn("Arguments 'it' and 'indices' to picos.sum are ignored.",
            DeprecationWarning)

    if isinstance(lst, Expression):
        if isinstance(lst, AffinExp):
            theSum = (lst|1)
            theSum.string = glyphs.sum(lst.string)
            return theSum
        else:
            raise TypeError("PICOS doesn't know how to sum over a single {}."
                .format(type(lst).__name__))

    if not all(isinstance(expression, Expression) for expression in lst):
        return builtin_sum(lst)

    if len(lst) == 0:
        return AffinExp.fromScalar(0)
    elif len(lst) == 1:
        return lst[0]
    elif len(lst) == 2:
        return lst[0] + lst[1]

    theSum = lst[0].copy()
    for expression in lst[1:]:
        theSum += expression

    try:
        template, data = parameterized_string([exp.string for exp in lst])
    except ValueError:
        theSum.string = glyphs.sum(
            glyphs.fromto(lst[0].string + ", ", ", " + lst[-1].string))
    else:
        theSum.string = glyphs.sum(glyphs.sep(template, data))

    return theSum


def break_cols(mat, sizes):
    n = len(sizes)
    I, J, V = [], [], []
    for i in range(n):
        I.append([])
        J.append([])
        V.append([])
    cumsz = np.cumsum(sizes)
    import bisect
    for i, j, v in zip(mat.I, mat.J, mat.V):
        block = bisect.bisect(cumsz, j)
        I[block].append(i)
        V[block].append(v)
        if block == 0:
            J[block].append(j)
        else:
            J[block].append(j - cumsz[block - 1])
    return [spmatrix(V[k], I[k], J[k], (mat.size[0], sz))
            for k, sz in enumerate(sizes)]


def break_rows(mat, sizes):
    n = len(sizes)
    I, J, V = [], [], []
    for i in range(n):
        I.append([])
        J.append([])
        V.append([])
    cumsz = np.cumsum(sizes)
    import bisect
    for i, j, v in zip(mat.I, mat.J, mat.V):
        block = bisect.bisect(cumsz, i)
        J[block].append(j)
        V[block].append(v)
        if block == 0:
            I[block].append(i)
        else:
            I[block].append(i - cumsz[block - 1])
    return [spmatrix(V[k], I[k], J[k], (sz, mat.size[1]))
            for k, sz in enumerate(sizes)]


def block_idx(i, sizes):
    # if there are blocks of sizes n1,...,nk and i is
    # the index of an element of the big vectorized variable,
    # returns the block of i and its index inside the sub-block.
    cumsz = np.cumsum(sizes)
    import bisect
    block = bisect.bisect(cumsz, i)
    return block, (i if block == 0 else i - cumsz[block - 1])


def geomean(exp):
    """returns a :class:`GeoMeanExp <picos.expressions.GeoMeanExp>` object representing the geometric mean of the entries of ``exp[:]``.
    This can be used to enter inequalities of the form ``t <= geomean(x)``.
    Note that geometric mean inequalities are internally reformulated as a
    set of SOC inequalities.

    **Example:**

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> x = prob.add_variable('x',1)
    >>> y = prob.add_variable('y',3)
    >>> # Add the constraint x <= (y0*y1*y2)**(1./3) to the problem:
    >>> prob.add_constraint(x<pic.geomean(y))
    <Geometric Mean Constraint: x ≤ geomean(y)>
    """
    from .expressions import AffinExp, GeoMeanExp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    return GeoMeanExp(exp)


def norm(exp, num=2, denom=1):
    """returns a :class:`NormP_Exp <picos.expressions.NormP_Exp>` object representing the (generalized-) p-norm of the entries of ``exp[:]``.
    This can be used to enter constraints of the form :math:`\Vert x \Vert_p \leq t` with :math:`p\geq1`.
    Generalized norms are also defined for :math:`p<1`, by using the usual formula
    :math:`\operatorname{norm}(x,p) := \Big(\sum_i x_i^p\Big)^{1/p}`. Note that this function
    is concave (for :math:`p<1`) over the set of vectors with nonnegative coordinates.
    When a constraint of the form :math:`\operatorname{norm}(x,p) > t` with :math:`p\leq1` is entered, PICOS implicitely assumes that :math:`x` is a nonnegative vector.

    This function can also be used to represent the Lp,q- norm of a matrix (for :math:`p,q \geq 1`):
    :math:`\operatorname{norm}(X,(p,q)) := \Big(\sum_i (\sum_j x_{ij}^q )^{p/q}\Big)^{1/p}`,
    that is, the p-norm of the vector formed with the q-norms of the rows of :math:`X`.

    The exponent :math:`p` of the norm must be specified either by
    a couple numerator (2d argument) / denominator (3d arguments),
    or directly by a float ``p`` given as second argument. In the latter case a rational
    approximation of ``p`` will be used. It is also possible to pass ``'inf'``  as
    second argument for the infinity-norm (aka max-norm).

    For the case of :math:`(p,q)`-norms, ``p`` and ``q`` must be specified by a tuple of floats
    in the second argument (rational approximations will be used), and the third argument will
    be ignored.

    **Example:**

    >>> import picos as pic
    >>> P = pic.Problem()
    >>> x = P.add_variable('x',1)
    >>> y = P.add_variable('y',3)
    >>> pic.norm(y,7,3) < x
    <p-Norm Constraint: ‖y‖_(7/3) ≤ x>
    >>> pic.norm(y,-0.4) > x
    <Generalized p-Norm Constraint: ‖y‖_(-2/5) ≥ x>
    >>> X = P.add_variable('X',(3,2))
    >>> pic.norm(X,(1,2)) < 1
    <(p,q)-Norm Constraint: ‖X‖_1,2 ≤ 1>
    >>> pic.norm(X,('inf',1)) < 1
    <(p,q)-Norm Constraint: ‖X‖_inf,1 ≤ 1>
    """
    from .expressions import AffinExp, NormP_Exp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    if num == 2 and denom == 1:
        return abs(exp)

    if isinstance(num, tuple) and len(num) == 2:
        if denom != 1:
            raise ValueError(
                'tuple as 2d argument for L(p,q)-norm and 3d argument is !=1')

        return NormP_Exp(exp, num[0], 1, num[1], 1)

    p = float(num) / float(denom)

    if p == 0:
        raise Exception('undefined for p=0')
    elif p == float('inf'):
        return NormP_Exp(exp, float('inf'), 1)
    elif p == float('-inf'):
        return NormP_Exp(exp, float('-inf'), 1)
    else:
        from fractions import Fraction
        frac = Fraction(p).limit_denominator(1000)
        return NormP_Exp(exp, frac.numerator, frac.denominator)


def tracepow(exp, num=1, denom=1, coef=None):
    """Returns a :class:`TracePow_Exp <picos.expressions.TracePow_Exp>` object representing the trace of the pth-power of the symmetric matrix ``exp``, where ``exp`` is an :class:`AffinExp <picos.expressions.AffinExp>` which we denote by :math:`X`.
    This can be used to enter constraints of the form :math:`\operatorname{trace} X^p \leq t` with :math:`p\geq1` or :math:`p < 0`, or :math:`\operatorname{trace} X^p \geq t` with :math:`0 \leq p \leq 1`.
    Note that :math:`X` is forced to be positive semidefinite when a constraint of this form is entered in PICOS.

    It is also possible to specify a ``coef`` matrix (:math:`M`) of the same size as ``exp``, in order to represent the expression  :math:`\operatorname{trace} (M X^p)`.
    The constraint :math:`\operatorname{trace} (M X^p)\geq t` can be reformulated with SDP constraints if :math:`M` is positive
    semidefinite and :math:`0<p<1`.

    Trace of power inequalities are internally reformulated as a set of Linear Matrix Inequalities (SDP),
    or second order cone inequalities if ``exp`` is a scalar.

    The exponent :math:`p` of the norm must be specified either by
    a couple numerator (2d argument) / denominator (3d arguments),
    or directly by a float ``p`` given as second argument. In the latter case a rational
    approximation of ``p`` will be used.

    **Example:**

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> X = prob.add_variable('X',(3,3),'symmetric')
    >>> t = prob.add_variable('t',1)
    >>> pic.tracepow(X,7,3) < t
    <Trace of Power Constraint: trace(X^(7/3)) ≤ t>
    >>> pic.tracepow(X,0.6) > t
    <Trace of Power Constraint: trace(X^(3/5)) ≥ t>
    >>> import cvxopt as cvx
    >>> A = cvx.normal(3,3);A=A*A.T # A random semidefinite positive matrix
    >>> A = pic.new_param('A',A)
    >>> pic.tracepow(X,0.25,coef=A) > t
    <Trace of Power Constraint: trace(A·X^(1/4)) ≥ t>
    """
    from .expressions import AffinExp, TracePow_Exp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    if coef is not None and not isinstance(coef, AffinExp):
        coef = AffinExp.fromMatrix(coef)

    if num == denom:
        # Note that AffinExp.__or__ choses the correct string for this case.
        return (exp | 'I')

    p = float(num) / float(denom)

    if p == 0:
        raise Exception('undefined for p=0')

    from fractions import Fraction
    frac = Fraction(p).limit_denominator(1000)
    return TracePow_Exp(exp, frac.numerator, frac.denominator, coef)


def trace(exp):
    """
    trace of a square AffinExp
    """
    return tracepow(exp)


def sum_k_largest(exp, k):
    """returns a :class:`Sum_k_Largest_Exp <picos.expressions.Sum_k_Largest_Exp>` object representing the sum
    of the ``k`` largest elements of an affine expression ``exp``.
    This can be used to enter constraints of the form :math:`\sum_{i=1}^k x_{i}^{\downarrow} \leq t`.
    This kind of constraints is reformulated internally as a set of linear inequalities.

    **Example:**

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> x = prob.add_variable('x',3)
    >>> t = prob.add_variable('t',1)
    >>> pic.sum_k_largest(x,2) < 1
    <Sum of Largest Elements Constraint: sum_2_largest(x) ≤ 1>
    >>> pic.sum_k_largest(x,1) < t
    <Sum of Largest Elements Constraint: max(x) ≤ t>
    """
    from .expressions import AffinExp, Sum_k_Largest_Exp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    return Sum_k_Largest_Exp(exp, k, False)


def sum_k_largest_lambda(exp, k):
    """returns a :class:`Sum_k_Largest_Exp <picos.expressions.Sum_k_Largest_Exp>` object representing the sum
    of the ``k`` largest eigenvalues of a square matrix affine expression ``exp``.
    This can be used to enter constraints of the form :math:`\sum_{i=1}^k \lambda_{i}^{\downarrow}(X) \leq t`.
    This kind of constraints is reformulated internally as a set of linear matrix inequalities (SDP).
    Note that ``exp`` is assumed to be symmetric (picos does not check).

    **Example:**

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> X = prob.add_variable('X',(3,3),'symmetric')
    >>> t = prob.add_variable('t',1)
    >>> pic.sum_k_largest_lambda(X,3) < 1
    <Sum of Largest Eigenvalues Constraint: trace(X) ≤ 1>
    >>> pic.sum_k_largest_lambda(X,2) < t
    <Sum of Largest Eigenvalues Constraint: sum_2_largest_λ(X) ≤ t>
    """
    from .expressions import AffinExp, Sum_k_Largest_Exp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    return Sum_k_Largest_Exp(exp, k, True)


def lambda_max(exp):
    """
    largest eigenvalue of a square matrix expression (cf. :func:`pic.sum_k_largest(exp,1) <picos.tools.sum_k_largest_lambda>`)

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> X = prob.add_variable('X',(3,3),'symmetric')
    >>> pic.lambda_max(X) < 2
    <Sum of Largest Eigenvalues Constraint: λ_max(X) ≤ 2>
    """
    return sum_k_largest_lambda(exp, 1)


def sum_k_smallest(exp, k):
    """returns a :class:`Sum_k_Smallest_Exp <picos.expressions.Sum_k_Smallest_Exp>` object representing the sum
    of the ``k`` smallest elements of an affine expression ``exp``.
    This can be used to enter constraints of the form :math:`\sum_{i=1}^k x_{i}^{\\uparrow} \geq t`.
    This kind of constraints is reformulated internally as a set of linear inequalities.

    **Example:**

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> x = prob.add_variable('x',3)
    >>> t = prob.add_variable('t',1)
    >>> pic.sum_k_smallest(x,2) > t
    <Sum of Smallest Elements Constraint: sum_2_smallest(x) ≥ t>
    >>> pic.sum_k_smallest(x,1) > 3
    <Sum of Smallest Elements Constraint: min(x) ≥ 3>
    """
    from .expressions import AffinExp, Sum_k_Smallest_Exp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    return Sum_k_Smallest_Exp(exp, k, False)


def sum_k_smallest_lambda(exp, k):
    """returns a :class:`Sum_k_Smallest_Exp <picos.expressions.Sum_k_Smallest_Exp>` object representing the sum
    of the ``k`` smallest eigenvalues of a square matrix affine expression ``exp``.
    This can be used to enter constraints of the form :math:`\sum_{i=1}^k \lambda_{i}^{\\uparrow}(X) \geq t`.
    This kind of constraints is reformulated internally as a set of linear matrix inequalities (SDP).
    Note that ``exp`` is assumed to be symmetric (picos does not check).

    **Example:**

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> X = prob.add_variable('X',(3,3),'symmetric')
    >>> t = prob.add_variable('t',1)
    >>> pic.sum_k_smallest_lambda(X,1) > 1
    <Sum of Smallest Eigenvalues Constraint: λ_min(X) ≥ 1>
    >>> pic.sum_k_smallest_lambda(X,2) > t
    <Sum of Smallest Eigenvalues Constraint: sum_2_smallest_λ(X) ≥ t>
    """
    from .expressions import AffinExp, Sum_k_Smallest_Exp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    return Sum_k_Smallest_Exp(exp, k, True)


def lambda_min(exp):
    """
    smallest eigenvalue of a square matrix expression (cf. :func:`pic.sum_k_smallest(exp,1) <picos.tools.sum_k_smallest_lambda>`)

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> X = prob.add_variable('X',(3,3),'symmetric')
    >>> pic.lambda_min(X) > -1
    <Sum of Smallest Eigenvalues Constraint: λ_min(X) ≥ -1>
    """
    return sum_k_smallest_lambda(exp, 1)


def partial_transpose(exp, dims_1=None, subsystems = None, dims_2=None):
    r"""Partial transpose of an Affine Expression, with respect to
    given subsystems. If ``X`` is a matrix
    :class:`AffinExp <picos.expressions.AffinExp>`
    that can be written as :math:`X = A_0 \otimes \cdots \otimes A_{n-1}`
    for some matrices :math:`A_0,\ldots,A_{n-1}`
    of respective sizes ``dims_1[0] x dims_2[0]``, ... , ``dims_1[n-1] x dims_2[n-1]``,
    this function returns the matrix
    :math:`Y = B_0 \otimes \cdots \otimes B_{n-1}`,
    where :math:`B_i=A_i^T` if ``i in subsystems``, and  :math:`B_i=A_i` otherwise.

    The optional parameters ``dims_1`` and ``dims_2`` are tuples specifying the dimension
    of each subsystem :math:`A_i`. The argument ``subsystems`` must be a ``tuple`` (or an ``int``) with the
    index of all subsystems to be transposed.

    The default value ``dims_1=None`` automatically computes the size of the subblocks,
    assuming that ``exp`` is a :math:`n^k \times n^k`-square matrix,
    for the *smallest* appropriate value of :math:`k \in [2,6]`, that is ``dims_1=(n,)*k``.

    If ``dims_2`` is not specified, it is assumed that the subsystems :math:`A_i` are square,
    i.e., ``dims_2=dims_1``. If ``subsystems`` is not specified, the default assumes that
    only the last system must be transposed, i.e., ``subsystems = (len(dims_1)-1,)``

    **Example:**

    >>> import picos as pic
    >>> import cvxopt as cvx
    >>> P = pic.Problem()
    >>> X = P.add_variable('X',(4,4))
    >>> X.value = cvx.matrix(range(16),(4,4))
    >>> print(X) #doctest: +NORMALIZE_WHITESPACE
    [ 0.00e+00  4.00e+00  8.00e+00  1.20e+01]
    [ 1.00e+00  5.00e+00  9.00e+00  1.30e+01]
    [ 2.00e+00  6.00e+00  1.00e+01  1.40e+01]
    [ 3.00e+00  7.00e+00  1.10e+01  1.50e+01]
    >>> # Standard partial transpose with respect to the 2x2 blocks and 2nd subsystem:
    >>> print(X.Tx) #doctest: +NORMALIZE_WHITESPACE
    [ 0.00e+00  1.00e+00  8.00e+00  9.00e+00]
    [ 4.00e+00  5.00e+00  1.20e+01  1.30e+01]
    [ 2.00e+00  3.00e+00  1.00e+01  1.10e+01]
    [ 6.00e+00  7.00e+00  1.40e+01  1.50e+01]
    >>> # Now with respect to the first subsystem:
    >>> print(pic.partial_transpose(X,(2,2),0)) #doctest: +NORMALIZE_WHITESPACE
    [ 0.00e+00  4.00e+00  2.00e+00  6.00e+00]
    [ 1.00e+00  5.00e+00  3.00e+00  7.00e+00]
    [ 8.00e+00  1.20e+01  1.00e+01  1.40e+01]
    [ 9.00e+00  1.30e+01  1.10e+01  1.50e+01]
    """
    return exp.partial_transpose(dims_1,subsystems,dims_2)


def partial_trace(X, k=1, dim=None):
    r"""Partial trace of an Affine Expression, with respect to the ``k``th subsystem or to every subsystems in ``k`` for a tensor product of dimensions ``dim``.
    If ``X`` is a matrix
    :class:`AffinExp <picos.expressions.AffinExp>`
    that can be written as :math:`X = A_0 \otimes \cdots \otimes A_{n-1}`
    for some matrices :math:`A_0,\ldots,A_{n-1}`
    of respective sizes ``dim[0] x dim[0]``, ... , ``dim[n-1] x dim[n-1]`` (``dim`` is a list of ints if all matrices are square),
    or ``dim[0][0] x dim[0][1]``, ...,``dim[n-1][0] x dim[n-1][1]`` (``dim`` is a list of 2-tuples if any of them except the ``k`` th one is rectangular),
    this function returns the matrix
    :math:`Y = \operatorname{trace}(A_k)\quad A_0 \otimes \cdots A_{k-1} \otimes A_{k+1} \otimes \cdots \otimes A_{n-1}` if ``k`` is an ``int`` or a ``list`` of one element, :math:`Y = \operatorname{trace}(A_{k_0,k_1,\ldots,k_m}) \quad A_0 \otimes \cdots A_{k_0-1} \otimes A_{k_0+1} \otimes \cdots \otimes A_{k_m-1} \otimes A_{k_m+1} \otimes \cdots \otimes A_{n-1}` if ``k`` is a list of subsystems.

    The default value ``dim=None`` automatically computes the size of the subblocks,
    assuming that ``X`` is a :math:`n^2 \times n^2`-square matrix
    with blocks of size :math:`n \times n`, in this case only bipartite subsystem is assume, hence ``k`` as to be either ``0`` or ``1``.

    **Example:**

    >>> import picos as pic
    >>> import cvxopt as cvx
    >>> P = pic.Problem()
    >>> X = P.add_variable('X',(4,4))
    >>> Y = P.add_variable('Y',(8,8))
    >>> X.value = cvx.matrix(range(16),(4,4))
    >>> Y.value = cvx.matrix(range(64),(8,8))
    >>> print(X) #doctest: +NORMALIZE_WHITESPACE
    [ 0.00e+00  4.00e+00  8.00e+00  1.20e+01]
    [ 1.00e+00  5.00e+00  9.00e+00  1.30e+01]
    [ 2.00e+00  6.00e+00  1.00e+01  1.40e+01]
    [ 3.00e+00  7.00e+00  1.10e+01  1.50e+01]
    >>> # Partial trace with respect to second subsystem (k=1):
    >>> print(pic.partial_trace(X)) #doctest: +NORMALIZE_WHITESPACE
    [ 5.00e+00  2.10e+01]
    [ 9.00e+00  2.50e+01]
    >>> # And with respect to first subsystem (k=0):
    >>> print(pic.partial_trace(X,0)) #doctest: +NORMALIZE_WHITESPACE
    [ 1.00e+01  1.80e+01]
    [ 1.20e+01  2.00e+01]
    >>> #Partial trace in a multiple subsystem scenario:
    >>> print(pic.partial_trace(Y,k=[0,2],dim=[2,2,2])) #doctest: +NORMALIZE_WHITESPACE
    [ 9.00e+01  1.54e+02]
    [ 9.80e+01  1.62e+02]
    """
    return X.partial_trace(k, dim)


def detrootn(exp):
    """returns a :class:`DetRootN_Exp <picos.expressions.DetRootN_Exp>` object representing the determinant of the
    :math:`n` th-root of the symmetric matrix ``exp``, where :math:`n` is the dimension of the matrix.
    This can be used to enter constraints of the form :math:`(\operatorname{det} X)^{1/n} \geq t`.
    Note that :math:`X` is forced to be positive semidefinite when a constraint of this form is entered in PICOS.
    Determinant inequalities are internally reformulated as a set of Linear Matrix Inequalities (SDP).

    **Example:**

    >>> import picos as pic
    >>> prob = pic.Problem()
    >>> X = prob.add_variable('X',(3,3),'symmetric')
    >>> t = prob.add_variable('t',1)
    >>> t < pic.detrootn(X)
    <n-th Root of a Determinant Constraint: det(X)^(1/3) ≥ t>
    """
    from .expressions import AffinExp, DetRootN_Exp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    return DetRootN_Exp(exp)


def ball(r, p=2):
    """returns a :class:`Ball <picos.expressions.Ball>` object representing:

      * a L_p Ball of radius ``r`` (:math:`\{x: \Vert x \Vert_p \geq r \}`) if :math:`p \geq 1`
      * the convex set :math:`\{x\geq 0: \Vert x \Vert_p \geq r \}` :math:`p < 1`.

    **Example**

    >>> import picos as pic
    >>> P = pic.Problem()
    >>> x = P.add_variable('x', 3)
    >>> x << pic.ball(2,3)  #doctest: +NORMALIZE_WHITESPACE
    <p-Norm Constraint: ‖x‖_3 ≤ 2>
    >>> x << pic.ball(1,0.5)
    <Generalized p-Norm Constraint: ‖x‖_(1/2) ≥ 1>
    """
    from .expressions import Ball
    return Ball(p, r)


def simplex(gamma=1):
    """returns a :class:`TruncatedSimplex <picos.expressions.TruncatedSimplex>` object representing the set :math:`\{x\geq 0: ||x||_1 \leq \gamma \}`.

    **Example**

    >>> import picos as pic
    >>> P = pic.Problem()
    >>> x = P.add_variable('x', 3)
    >>> x << pic.simplex()
    <Standard Simplex Constraint: x ∈ {x ≥ 0 : ∑(x) ≤ 1}>
    >>> x << pic.simplex(2)
    <Simplex Constraint: x ∈ {x ≥ 0 : ∑(x) ≤ 2}>
    """
    from .expressions import TruncatedSimplex
    return TruncatedSimplex(radius=gamma, truncated=False, nonneg=True)


def truncated_simplex(gamma=1, sym=False):
    """returns a :class:`TruncatedSimplex <picos.expressions.TruncatedSimplex>` object representing the set:

      * :math:`\{x \geq  0: ||x||_\infty \leq 1,\ ||x||_1 \leq \gamma \}` if ``sym=False`` (default)
      * :math:`\{x: ||x||_\infty \leq 1,\ ||x||_1 \leq \gamma \}` if ``sym=True``.

    **Example**

    >>> import picos as pic
    >>> P = pic.Problem()
    >>> x = P.add_variable('x', 3)
    >>> x << pic.truncated_simplex(2)
    <Truncated Simplex Constraint: x ∈ {0 ≤ x ≤ 1 : ∑(x) ≤ 2}>
    >>> x << pic.truncated_simplex(2,sym=True)
    <Symmetrized Truncated Simplex Constraint: x ∈ {-1 ≤ x ≤ 1 : ∑(|x|) ≤ 2}>
    """
    from .expressions import TruncatedSimplex
    return TruncatedSimplex(radius=gamma, truncated=True, nonneg=not(sym))


def expcone():
    """returns a :class:`ExponentialCone <picos.expressions.ExponentialCone>` object representing the set :math:`\operatorname{closure}\ \{(x,y,z): y>0, y\exp(x/y)\leq z \}`

    **Example**

    >>> import picos as pic
    >>> P = pic.Problem()
    >>> x = P.add_variable('x', 3)
    >>> pic.expcone()
    <Exponential Cone: cl{[x; y; z] : y·exp(z/y) ≤ x, x > 0, y > 0}>
    >>> x << pic.expcone()
    <Exponential Cone Constraint: x[0] ≥ x[1]·exp(x[2]/x[1])>
    """
    from .expressions import ExponentialCone
    return ExponentialCone()


def _allIdent(lst):
    if len(lst) <= 1:
        return True

    return (np.array([lst[i] == lst[i + 1] for i in range(len(lst) - 1)]).all())


def detect_range(sequence, asQuadruple = False, asStringTemplate = False,
        shortString = False):
    """
    Detects a Python range object yielding the same sequence as the given
    integer sequence.

    By default, returns a range object mirroring the input sequence.

    :param sequence: An integer sequence that can be mirrored by a Python range.
    :param bool asQuadruple: Whether to return a quadruple with factor, inner
        shift, outer shift, and length, formally ``(a, i, o, n)`` such that
        ``[a*(x+i)+o for x in range(n)]`` mirrors the input sequence.
    :param bool asStringTemplate: Whether to return a format string that, if
        instanciated with numbers from ``0`` to ``len(sequence) - 1``, yields
        math expression strings that describe the input sequence members.
    :param bool shortString: Whether to return condensed string templates that
        are designed to be instanciated with an index character string. Requires
        asStringTemplate to be ``True``.
    :raises TypeError: If the input is not an integer sequence.
    :raises ValueError: If the input cannot be mirrored by a Python range.
    :returns: A range object, a quadruple of numbers, or a format string.

    **Example**

    >>> from picos.tools import detect_range as dr
    >>> R = range(7,30,5)
    >>> S = list(R)
    >>> S
    [7, 12, 17, 22, 27]
    >>> # By default, returns a matching range object:
    >>> dr(S)
    range(7, 28, 5)
    >>> dr(S) == R
    True
    >>> # Sequence elements can also be decomposed w.r.t. range(len(S)):
    >>> a, i, o, n = dr(S, asQuadruple=True)
    >>> [a*(x+i)+o for x in range(n)] == S
    True
    >>> # The same decomposition can be returned in a string representation:
    >>> dr(S, asStringTemplate=True)
    '5·({} + 1) + 2'
    >>> # Short string representations are designed to accept index names:
    >>> dr(S, asStringTemplate=True, shortString=True).format("i")
    '5(i+1)+2'
    >>> dr(range(0,100,5), asStringTemplate=True, shortString=True).format("i")
    '5i'
    >>> dr(range(10,100), asStringTemplate=True, shortString=True).format("i")
    'i+10'

    **Example**

    >>> # This works with decreasing ranges as well.
    >>> R2 = range(10,4,-2)
    >>> S2 = list(R2)
    >>> S2
    [10, 8, 6]
    >>> dr(S2)
    range(10, 5, -2)
    >>> dr(S2) == R2
    True
    >>> a, i, o, n = dr(S2, asQuadruple=True)
    >>> [a*(x+i)+o for x in range(n)] == S2
    True
    >>> T = dr(S2, asStringTemplate=True, shortString=True)
    >>> [T.format(i) for i in range(len(S2))]
    ['-2(0-5)', '-2(1-5)', '-2(2-5)']
    """
    if asQuadruple and asStringTemplate:
        raise ValueError(
            "Can only return a quadruple or a string template, not both.")

    if shortString and not asStringTemplate:
        raise ValueError("Enabling 'shortString' requires 'asStringTemplate'.")

    if len(sequence) is 0:
        if asQuadruple:
            return 0, 0, 0, 0
        elif asStringTemplate:
            return ""
        else:
            return range(0)

    first  = sequence[0]
    last   = sequence[-1]
    next   = last + (1 if first <= last else -1)
    length = len(sequence)

    if not isinstance(first, int) or not isinstance(last, int):
        raise TypeError("Not an integer container.")

    # Determine potential integer step size.
    if length > 1:
        step = (last - first) / (length - 1)
    else:
        step = 1
    if int(step) != step:
        raise ValueError("Cannot be mirrored by a Python range.")
    step = int(step)

    # Determine potential range.
    range_ = range(first, next, step)
    for position, number in enumerate(range_):
        if sequence[position] != number:
            raise ValueError("Cannot be mirrored by a Python range.")

    if asQuadruple or asStringTemplate:
        # Compute inner and outer shift.
        innerShift = first // step
        outerShift = first  % step

        # Verify our finding.
        assert last // step + 1 - innerShift                 == length
        assert step*(0 + innerShift) + outerShift            == first
        assert step*((length - 1) + innerShift) + outerShift == last

        if asQuadruple:
            return step, innerShift, outerShift, length
        elif shortString:
            string = "{{}}{:+d}".format(innerShift) if innerShift else "{}"
            if step != 1 and innerShift:
                string = "{}({})".format("-" if step == -1 else step, string)
            elif step != 1:
                string = "{}{}".format("-" if step == -1 else step, string)
            string = "{}{:+d}".format(string, outerShift) \
                if outerShift else string

            return string
        else:
            glyph = glyphs.add("{}", innerShift) if innerShift else "{}"
            glyph = glyphs.mul(step, glyph) if step != 1 else glyph
            glyph = glyphs.add(glyph, outerShift) if outerShift else glyph

            return glyph
    else:
        return range_


def parameterized_string(
        strings, replace = "\d+", placeholders = "ijklpqr", fallback = "?"):
    """
    Given a list of strings with similar structure, finds a single string with
    placeholders and an expression that denotes how to instantiate the
    placeholders in order to obtain each string in the list.

    The function is designed to take a number of symbolic string representations
    of math expressions that differ only with respect to indices.

    :param list strings: The list of strings to compare.
    :param str replace: A regular expression describing the bits to replace with
        placeholders.
    :param placeholders: An iterable of placeholder strings. Usually a string,
        so that each of its characters becomes a placeholder.
    :param str fallback: A fallback placeholder string, if the given
        placeholders are not sufficient.
    :returns: A tuple of two strings, the first being the template string and
        the second being a description of the placeholders used.

    **Example**

    >>> from picos.tools import parameterized_string as ps
    >>> ps(["A[{}]".format(i) for i in range(5, 31)])
    ('A[i+5]', 'i ∈ [0…25]')
    >>> ps(["A[{}]".format(i) for i in range(5, 31, 5)])
    ('A[5(i+1)]', 'i ∈ [0…5]')
    >>> S=["A[0]·B[2]·C[3]·D[5]·F[0]",
    ...    "A[1]·B[1]·C[6]·D[6]·F[0]",
    ...    "A[2]·B[0]·C[9]·D[9]·F[0]"]
    >>> ps(S)
    ('A[i]·B[-(i-2)]·C[3(i+1)]·D[j]·F[0]', '(i,j) ∈ zip([0…2],[5,6,9])')
    """
    if len(strings) is 0:
        return "", ""
    elif len(strings) is 1:
        return strings[0], ""

    for string in strings:
        if not isinstance(string, str):
            raise TypeError("First argument must be a list of strings.")

    # The skeleton of a string is the part not matched by 'replace', and it must
    # be the same for all strings.
    skeleton = re.split(replace, strings[0])
    for string in strings[1:]:
        if skeleton != re.split(replace, string):
            raise ValueError("Strings do not have a common skeleton.")

    # The slots are the parts that are matched by 'replace' and should be filled
    # with the placeholders.
    slotToValues = []
    for string in strings:
        slotToValues.append(re.findall(replace, string))
    slotToValues = list(zip(*slotToValues))

    # Verify that slots are always surrounded by (empty) skeleton strings.
    assert len(skeleton) is len(slotToValues) + 1

    # Find slots with the same value in each string; add them to the skeleton.
    for slot in range(len(slotToValues)):
        if len(set(slotToValues[slot])) is 1:
            skeleton[slot + 1] =\
                skeleton[slot] + slotToValues[slot][0] + skeleton[slot + 1]
            skeleton[slot] = None
            slotToValues[slot] = None
    skeleton     = [s for s in skeleton     if s is not None]
    slotToValues = [v for v in slotToValues if v is not None]

    # We next build a mapping from slots to (few) placeholder indices.
    slotToIndex = {}
    nextIndex = 0

    # Find slots whose values form a range, and build string templates that lift
    # a placeholder to a formula denoting sequence elements (e.g. "i" → "2i+1").
    # All such slots share the first placeholder (with index 0).
    slotToTemplate = {}
    for slot, values in enumerate(slotToValues):
        try:
            slotToTemplate[slot] = detect_range([int(v) for v in values],
                asStringTemplate = True, shortString = True)
        except ValueError:
            pass
        else:
            slotToIndex[slot] = 0
            nextIndex = 1

    # Find slots with identical value in each string and assign them the same
    # placeholder.
    valsToIndex = {}
    for slot, values in enumerate(slotToValues):
        if slot in slotToIndex:
            # The slot holds a range.
            continue

        if values in valsToIndex:
            slotToIndex[slot] = valsToIndex[values]
        else:
            slotToIndex[slot]   = nextIndex
            valsToIndex[values] = nextIndex
            nextIndex += 1

    # Define a function that maps slots to their placeholder symbols.
    def placeholder(slot):
        index = slotToIndex[slot]
        return placeholders[index] if index < len(placeholders) else fallback

    # Assemble the string template (with values replaced by placeholders).
    template = ""
    for slot in range(len(slotToIndex)):
        if slot in slotToTemplate:
            ph = slotToTemplate[slot].format(placeholder(slot))
        else:
            ph = placeholder(slot)

        template += skeleton[slot] + ph
    template += skeleton[-1]

    # Collect the placeholdes that were used, and their domains.
    usedPHs, domains = [], []
    indices = set()
    for slot, index in slotToIndex.items():
        values = slotToValues[slot]

        if index in indices:
            continue
        else:
            indices.add(index)

        usedPHs.append(placeholder(slot))

        if slot in slotToTemplate:
            domains.append(glyphs.intrange(0, len(values) - 1))
        elif len(values) > 4:
            domains.append(glyphs.intrange(
                ",".join(values[:2]) + ",", "," + ",".join(values[-2:])))
        else:
            domains.append(glyphs.interval(",".join(values)))

    # Make sure used placeholders and their domains match in number.
    assert len(usedPHs) == len(domains)

    # Assemble occuring placeholders and ther joint domain (the data).
    if len(domains) is 0:
        data = ""
    else:
        if len(domains) is 1:
            usedPHs = usedPHs[0]
            domain  = domains[0]
        else:
            usedPHs = "({})".format(",".join(usedPHs))
            domain  = "zip({})".format(",".join(domains))

        data = glyphs.element(usedPHs, domain)

    return template, data


def eval_dict(dict_of_variables):
    """
    if ``dict_of_variables`` is a dictionary
    mapping variable names (strings) to :class:`variables <picos.expressions.Variable>`,
    this function returns the dictionary ``names -> variable values``.
    """
    valued_dict = {}

    for k in dict_of_variables:
        valued_dict[k] = dict_of_variables[k].eval()
        if valued_dict[k].size == (1, 1):
            valued_dict[k] = valued_dict[k][0]
    return valued_dict


def blocdiag(X, n):
    """
    makes diagonal blocs of X, for indices in [sub1,sub2[
    n indicates the total number of blocks (horizontally)
    """
    if not isinstance(X, cvx.base.spmatrix):
        X = cvx.sparse(X)
    if n==1:
        return X
    else:
        Z = spmatrix([],[],[],X.size)
        mat = []
        for i in range(n):
            col = [Z]*(n-1)
            col.insert(i,X)
            mat.append(col)
        return cvx.sparse(mat)


def exp(x):
    """
    Exponentiation of a PICOS, CVXOPT, NumPy, or numeric expression.
    """
    from .expressions import Expression, AffinExp, SumExponential

    if isinstance(x, AffinExp):
        if len(x) != 1:
            raise TypeError("PICOS does not support element-wise exponentiation"
                " of a multidimensional affine expression. "
                "Use picos.sumexp if you mean the sum over that.")

        if x.isconstant():
            return AffinExp.fromScalar(
                exp(x.constant[0]) if x.constant else 1.0)
        else:
            return SumExponential(x)
    elif isinstance(x, Expression):
        raise NotImplementedError(
            "Exponentiation of a {} expression is not supported."
            .format(x.__class__.__name__))

    moduleName = type(x).__module__.split(".", 1)

    if moduleName == "cvxopt":
        return cvx.exp(x)
    elif moduleName == "numpy":
        return np.exp(x)
    elif is_numeric(x):
        return np.exp(x)
    else:
        raise TypeError("PICOS doesn't know how to apply the exponential "
            "function to an object of type '{}'.".format(type(x).__name__))


def log(x):
    """
    The logarithm of a PICOS, CVXOPT, NumPy, or numeric expression.
    """
    from .expressions import Expression, AffinExp, SumExponential, \
        Logarithm, KullbackLeibler, LogSumExp

    if isinstance(x, AffinExp):
        if len(x) != 1:
            raise TypeError("PICOS does not support taking the element-wise "
                "logarithm of a multidimensional affine expression.")

        if x.isconstant():
            return AffinExp.fromScalar(
                log(x.constant[0]) if x.constant else log(0))
        else:
            return Logarithm(x)
    elif isinstance(x, SumExponential):
        if not x.Exp2.is1():
            raise NotImplementedError(
                "Taking the logarithm of a sum of perspectives of exponentials "
                "is not supported.")

        return LogSumExp(x.Exp)
    elif isinstance(x, Expression):
        raise NotImplementedError(
            "Taking the logarithm of a {} expression is not supported."
            .format(x.__class__.__name__))

    moduleName = type(x).__module__.split(".", 1)

    if moduleName == "cvxopt":
        return cvx.log(x)
    elif moduleName == "numpy":
        return np.log(x)
    elif is_numeric(x):
        if x < 0:
            x = complex(x)
        elif x == 0:
            raise ValueError("Cannot take the logarithm of 0.")

        return np.log(x)
    else:
        raise TypeError("PICOS doesn't know how to take the logarithm of an "
            "object of type '{}'.".format(type(x).__name__))


def sumexp(x, y = None):
    """
    A shorthand for :class:`SumExponential <picos.expressions.SumExponential>`.

    If the second optional argument is passed, the resulting expression is the
    sum of perspectives of exponentials :math:`\sum_i y_i \exp(x_i / y_i)`,
    otherwise it is a sum of exponentials :math:`\sum_i \exp(x_i)`.
    """
    from .expressions import SumExponential
    return SumExponential(x, y)


def kullback_leibler(x, y = None):
    """
    A shorthand for :class:`KullbackLeibler <picos.expressions.KullbackLeibler>`.

    If the second optional argument is passed, the resulting expression is the
    Kullback-Leibler divergence :math:`\sum_i x_i \log(x_i / y_i)`, otherwise
    it is the (negative) entropy :math:`\sum_i x_i \log(x_i)`.
    """
    from .expressions import KullbackLeibler
    return KullbackLeibler(x, y)


def logsumexp(exp):
    """
    A shorthand for :class:`LogSumExp <picos.expressions.LogSumExp>`.

    **Example**

    >>> import picos as pic
    >>> import cvxopt as cvx
    >>> prob=pic.Problem()
    >>> x=prob.add_variable('x',3)
    >>> A=pic.new_param('A',cvx.matrix([[1,2],[3,4],[5,6]]))
    >>> pic.lse(A*x)<0
    <LSE Constraint: log∘sum∘exp(A·x) ≤ 0>
    """
    from .expressions import LogSumExp
    return LogSumExp(exp)

lse = logsumexp


def diag(exp, dim=1):
    r"""
    if ``exp`` is an affine expression of size (n,m),
    ``diag(exp,dim)`` returns a diagonal matrix of size ``dim*n*m`` :math:`\times` ``dim*n*m``,
    with ``dim`` copies of the vectorized expression ``exp[:]`` on the diagonal.

    In particular:

      * when ``exp`` is scalar, ``diag(exp,n)`` returns a diagonal
        matrix of size :math:`n \times n`, with all diagonal elements equal to ``exp``.

      * when ``exp`` is a vector of size :math:`n`, ``diag(exp)`` returns the diagonal
        matrix of size :math:`n \times n` with the vector ``exp`` on the diagonal

    **Example**

    >>> import picos as pic
    >>> prob=pic.Problem()
    >>> x=prob.add_variable('x',1)
    >>> y=prob.add_variable('y',1)
    >>> pic.diag(x-y,4)
    <4×4 Affine Expression: Diag(x - y)>
    >>> pic.diag(x//y)
    <2×2 Affine Expression: Diag([x; y])>
    """
    from .expressions import AffinExp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    (n, m) = exp.size

    # TODO: Use copy function of AffinExp.
    expcopy = AffinExp(exp.factors.copy(), exp.constant, exp.size, exp.string)

    idx = cvx.spdiag([1.] * dim * n * m)[:].I
    for k in exp.factors.keys():
        # ensure it's sparse
        mat = cvx.sparse(expcopy.factors[k])
        I, J, V = list(mat.I), list(mat.J), list(mat.V)
        newI = []
        for d in range(dim):
            for i in I:
                newI.append(idx[i + n * m * d])
        expcopy.factors[k] = spmatrix(
            V * dim, newI, J * dim, ((dim * n * m)**2, exp.factors[k].size[1]))

    expcopy.constant = cvx.matrix(0., ((dim * n * m)**2, 1))
    if not exp.constant is None:
        for k, i in enumerate(idx):
            expcopy.constant[i] = exp.constant[k % (n * m)]

    expcopy._size = (dim * n * m, dim * n * m)
    expcopy.string = glyphs.Diag(exp.string)

    return expcopy


def diag_vect(exp):
    """
    Returns the vector with the diagonal elements of the matrix expression ``exp``

    **Example**

    >>> import picos as pic
    >>> prob=pic.Problem()
    >>> X=prob.add_variable('X',(3,3))
    >>> pic.diag_vect(X)
    <3×1 Affine Expression: diag(X)>
    """
    from .expressions import AffinExp

    if not isinstance(exp, AffinExp):
        exp = AffinExp.fromMatrix(exp)

    (n, m) = exp.size
    n = min(n, m)

    idx = cvx.spdiag([1.] * n)[:].I
    expcopy = AffinExp(exp.factors.copy(), exp.constant, exp.size,  exp.string)
    proj = spmatrix([1.] * n, range(n), idx, (n, exp.size[0] * exp.size[1]))

    for k in exp.factors.keys():
        expcopy.factors[k] = proj * expcopy.factors[k]

    if not exp.constant is None:
        expcopy.constant = proj * expcopy.constant

    expcopy._size = (n, 1)

    expcopy.string = glyphs.diag(exp.string)

    return expcopy


def retrieve_matrix(mat, exSize=None):
    """
    parses the variable *mat* and convert it to a :func:`cvxopt sparse matrix <cvxopt:cvxopt.spmatrix>`.
    If the variable **exSize** is provided, the function tries
    to return a matrix that matches this expected size, or raise an
    error.

    .. WARNING:: If there is a conflit between the size of **mat** and
                 the expected size **exsize**, the function might still
                 return something without raising an error !

    :param mat: The value to be converted into a cvx.spmatrix.
                The function will try to parse this variable and
                format it to a vector/matrix. *mat* can be of one
                of the following types:

                    * ``list`` [creates a vecor of dimension len(list)]
                    * :func:`cvxopt matrix <cvxopt:cvxopt.matrix>`
                    * :func:`cvxopt sparse matrix <cvxopt:cvxopt.spmatrix>`
                    * :func:`numpy array <numpy:numpy.array>`
                    * ``int`` or ``real`` [creates a vector/matrix of the size exSize *(or of size (1,1) if exSize is None)*,
                      whith all entries equal to **mat**.
                    * following strings:

                            * '``|a|``' for a matrix with all terms equal to a
                            * '``|a|(n,m)``' for a matrix forced to be of size n x m, with all terms equal to a
                            * '``e_i(n,m)``' matrix of size (n,m), with a 1 on the ith coordinate (and 0 elsewhere)
                            * '``e_i,j(n,m)``' matrix  of size (n,m), with a 1 on the (i,j)-entry (and 0 elsewhere)
                            * '``I``' for the identity matrix
                            * '``I(n)``' for the identity matrix, forced to be of size n x n.
                            * '``a%s``', where ``%s`` is one of the above string: the matrix that
                              should be returned when **mat** == ``%s``, multiplied by the scalar a.
    :returns: A tuple of the form (**M**, **s**), where **M** is the conversion of **mat** into a
              :func:`cvxopt sparse matrix <cvxopt:cvxopt.spmatrix>`, and **s**
              is a string representation of **mat**

    **Example:**

    >>> import picos as pic
    >>> pic.tools.retrieve_matrix([1,2,3])
    (<3x1 sparse matrix, tc='d', nnz=3>, '[3×1]')
    >>> pic.tools.retrieve_matrix('e_5(7,1)')
    (<7x1 sparse matrix, tc='d', nnz=1>, 'e_5')
    >>> print(pic.tools.retrieve_matrix('e_11(7,2)')[0]) #doctest: +NORMALIZE_WHITESPACE
    [   0        0       ]
    [   0        0       ]
    [   0        0       ]
    [   0        0       ]
    [   0        1.00e+00]
    [   0        0       ]
    [   0        0       ]
    >>> print(pic.tools.retrieve_matrix('5.3I',(2,2)))
    (<2x2 sparse matrix, tc='d', nnz=2>, '5.3·I')
    """
    from .expressions import Expression

    if exSize is not None and not is_integer(exSize) \
    and not isinstance(exSize, tuple):
        raise TypeError("Argument 'exSize' must be None, an integer, or an "
            "integer tuple.")

    retstr = None

    if isinstance(mat, Expression) and mat.is_valued():
        # TODO: This seems dangerous as it could unexpectedly translate
        #       non-constant expressions.
        retmat = mat.valueAsMatrix
        retstr = mat.string
    elif isinstance(mat, np.ndarray):
        if np.iscomplex(mat).any():
            retmat = cvx.matrix(mat, tc='z')
        else:
            retmat = cvx.matrix(mat.real, tc='d')
    elif isinstance(mat, cvx.base.matrix):
        if mat.typecode in "dz":
            retmat = mat
        elif mat.typecode is "i":
            retmat = cvx.matrix(mat, tc='d')
        else:
            raise TypeError(
                "PICOS does not know how to handle CVXOPT dense matrices with "
                "type code '{}'.".format(mat.typecode))
    elif isinstance(mat, cvx.base.spmatrix):
        retmat = mat
    elif isinstance(mat, list):
        if any([isinstance(v, complex) for v in mat]):
            tc = 'z'
        else:
            tc = 'd'
        if (isinstance(exSize, tuple)  # it matches the expected size
                and len(exSize) == 2
                and not(exSize[0] is None)
                and not(exSize[1] is None)
                and len(mat) == exSize[0] * exSize[1]):
            retmat = cvx.matrix(np.array(mat), exSize, tc=tc)
        else:  # no possible match
            retmat = cvx.matrix(np.array(mat), tc=tc)
    elif is_numeric(mat):
        if 'complex' in str(type(mat)):
            mat = complex(mat)

            if mat.imag:
                tc = 'z'
            else:
                mat = mat.real
                tc = 'd'
        else:
            mat = float(mat)
            tc = 'd'

        if not mat: # == 0
            retstr = glyphs.scalar(0)

            if exSize is None:
                retmat = cvx.matrix(0.0, (1, 1))
            elif is_integer(exSize):
                retmat = spmatrix([], [], [], (exSize, exSize))
            else:
                retmat = spmatrix([], [], [], exSize)
        else:
            retstr = glyphs.scalar(mat)

            if exSize is None:
                retmat = cvx.matrix(mat, (1, 1), tc=tc)
            elif is_integer(exSize):
                retmat = cvx.spdiag([mat] * exSize)

                if exSize > 1:
                    retstr = glyphs.mul(retstr, glyphs.idmatrix())
            else:
                retmat = cvx.matrix(mat, exSize)

                if exSize != (1, 1):
                    retstr = glyphs.matrix(retstr)
    elif isinstance(mat, str):
        regex = \
            "^([\-0-9.+j]+)?" + "(" +\
                "e_[0-9]+(?:,[0-9]+)?" + "|" +\
                "\|[\-0-9.+j]+\|" + "|" +\
                "I" + ")" +\
            "(\([0-9]+(?:,[0-9]+)?\))?" +\
            "(.T)?$"

        tokens = re.findall(regex, mat)[0]

        if len(tokens) != 4:
            raise ValueError("The string '{}' could not be parsed as a matrix.'"
                .format(mat))

        factor, base, forcedSize, transpose = tokens

        # Convert the factor.
        if "j" in factor:
            factor = complex(factor)
        elif factor:
            factor = float(factor)
        else:
            factor = 1.0

        # Convert the size.
        if forcedSize:
            forcedSize = forcedSize[1:-1].split(",")
            if len(forcedSize) == 1:
                forcedSize *= 2
            forcedSize = int(forcedSize[0]), int(forcedSize[1])
            size = forcedSize
        else:
            if is_integer(exSize):
                size = (exSize, exSize)
            else:
                size = exSize

        if size is None:
            raise ValueError("The size of the target matrix was not specified.")

        # Convert the transposition.
        transpose = bool(transpose)

        # Create the base matrix.
        # TODO: In the case of forced size, consider adding the size to the
        #       matrix description.
        if base.startswith("e_"):
            position = base[2:].split(",")
            if len(position) == 1:
                index = int(position[0])
                i,j = index % size[0], index // size[0]
            else:
                i,j = int(position[0]), int(position[1])

            retmat = spmatrix([1.0], [i], [j], size)
            retstr = base if 1 in size else base.upper()
        elif base.startswith("|"):
            element = base[1:-1]
            if "j" in element:
                element = complex(element)
            else:
                element = float(element)

            # Pull the factor inside the matrix.
            element *= factor
            factor = 1.0

            retmat = cvx.matrix(element, size)
            retstr = glyphs.matrix(element)
        elif base == "I":
            if size[0] != size[1]:
                raise ValueError("Cannot create a non-square identy matrix.")

            retmat = cvx.spdiag([1.0] * size[0])
            retstr = glyphs.idmatrix()
        else:
            assert False, "Unexpected matrix base string"

        if factor != 1.0:
            retmat *= factor
            retstr = glyphs.mul(factor, retstr)

        if transpose:
            retmat = retmat.T
            retstr = glyphs.transp(retstr)
    else:
        raise TypeError("PICOS does not know how to convert an object of type "
            "'{}' to a matrix.".format(type(mat)))

    # Make sure the matrix returned is sparse.
    # TODO: Is this really necessary for dense matrices?
    if not isinstance(mat, cvx.base.spmatrix):
        retmat = cvx.sparse(retmat)

    # Broadcast a 1×1 matrix to a differing expected size.
    if retmat.size == (1, 1) and exSize not in [(1, 1), 1, None]:
        return retrieve_matrix(retmat[0], exSize)

    # Fallback to a generic matrix string if no better string was found.
    if retstr is None:
        retstr = glyphs.matrix(glyphs.size(*retmat.size))

    return retmat, retstr


def svec(mat, ignore_sym=False):
    """
    returns the svec representation of the cvx matrix ``mat``.
    (see `Dattorro, ch.2.2.2.1 <http://meboo.convexoptimization.com/Meboo.html>`_)

    If ``ignore_sym = False`` (default), the function raises an Exception if ``mat`` is not symmetric.
    Otherwise, elements in the lower triangle of ``mat`` are simply ignored.
    """
    if not isinstance(mat, cvx.spmatrix):
        mat = cvx.sparse(mat)

    s0 = mat.size[0]
    if s0 != mat.size[1]:
        raise ValueError('mat must be square')

    I = []
    J = []
    V = []
    for (i, j, v) in zip((mat.I), (mat.J), (mat.V)):
        if not ignore_sym:
            if abs(mat[j, i] - v) > 1e-6:
                raise ValueError('mat must be symmetric')
        if i <= j:
            isvec = j * (j + 1) // 2 + i
            J.append(0)
            I.append(isvec)
            if i == j:
                V.append(v)
            else:
                V.append(np.sqrt(2) * v)

    return spmatrix(V, I, J, (s0 * (s0 + 1) // 2, 1))


def svecm1(vec, triu=False):
    if vec.size[1] > 1:
        raise ValueError('should be a column vector')
    v = vec.size[0]
    n = int(np.sqrt(1 + 8 * v) - 1) // 2
    if n * (n + 1) // 2 != v:
        raise ValueError('vec should be of dimension n(n+1)/2')
    if not isinstance(vec, cvx.spmatrix):
        vec = cvx.sparse(vec)
    I = []
    J = []
    V = []
    for i, v in zip(vec.I, vec.V):
        c = int(np.sqrt(1 + 8 * i) - 1) // 2
        r = i - c * (c + 1) // 2
        I.append(r)
        J.append(c)
        if r == c:
            V.append(v)
        else:
            if triu:
                V.append(v / np.sqrt(2))
            else:
                I.append(c)
                J.append(r)
                V.extend([v / np.sqrt(2)] * 2)
    return spmatrix(V, I, J, (n, n))


def ltrim1(vec, uptri=True,offdiag_fact=1.):
    """
    If ``vec`` is a vector or an affine expression of size n(n+1)/2, ltrim1(vec) returns a (n,n) matrix with
    the elements of vec in the lower triangle.
    If ``uptri == False``, the upper triangle is 0, otherwise the upper triangle is the symmetric of the lower one.
    """
    if vec.size[1] > 1:
        raise ValueError('should be a column vector')
    from .expressions import AffinExp
    v = vec.size[0]
    n = int(np.sqrt(1 + 8 * v) - 1) // 2
    if n * (n + 1) // 2 != v:
        raise ValueError('vec should be of dimension n(n+1)/2')
    if isinstance(vec, cvx.matrix) or isinstance(vec, cvx.spmatrix):
        if not isinstance(vec, cvx.matrix):
            vec = cvx.matrix(vec)
        M = cvx.matrix(0., (n, n))
        r = 0
        c = 0
        for v in vec:
            if r == n:
                c += 1
                r = c
            if r!=c:
                v *= offdiag_fact
            M[r, c] = v
            if r > c and uptri:
                M[c, r] = v
            r += 1

        return M
    elif isinstance(vec, AffinExp):
        I, J, V = [], [], []
        r = 0
        c = 0
        for i in range(v):
            if r == n:
                c += 1
                r = c
            I.append(r + n * c)
            J.append(i)
            V.append(1)
            if r > c and uptri:
                I.append(c + n * r)
                J.append(i)
                V.append(1)
            r += 1
        H = spmatrix(V, I, J, (n**2, v))
        Hvec = H * vec
        newfacs = Hvec.factors
        newcons = Hvec.constant
        if uptri:
            return AffinExp(newfacs, newcons, (n, n),
                glyphs.makeFunction("ltrim1_sym")(vec.string))
        else:
            return AffinExp(newfacs, newcons, (n, n),
                glyphs.makeFunction("ltrim1")(vec.string))
    else:
        raise Exception('expected a cvx vector or an affine expression')


def lowtri(exp):
    r"""
    if ``exp`` is a square affine expression of size (n,n),
    ``lowtri(exp)`` returns the (n(n+1)/2)-vector of the lower triangular elements of ``exp``.

    **Example**

    >>> import picos as pic
    >>> import cvxopt as cvx
    >>> prob=pic.Problem()
    >>> X=prob.add_variable('X',(4,4),'symmetric')
    >>> pic.tools.lowtri(X)
    <10×1 Affine Expression: lowtri(X)>
    >>> X0 = cvx.matrix(range(16),(4,4))
    >>> X.value = X0 * X0.T
    >>> print(X) #doctest: +NORMALIZE_WHITESPACE
    [ 2.24e+02  2.48e+02  2.72e+02  2.96e+02]
    [ 2.48e+02  2.76e+02  3.04e+02  3.32e+02]
    [ 2.72e+02  3.04e+02  3.36e+02  3.68e+02]
    [ 2.96e+02  3.32e+02  3.68e+02  4.04e+02]
    >>> print(pic.tools.lowtri(X)) #doctest: +NORMALIZE_WHITESPACE
    [ 2.24e+02]
    [ 2.48e+02]
    [ 2.72e+02]
    [ 2.96e+02]
    [ 2.76e+02]
    [ 3.04e+02]
    [ 3.32e+02]
    [ 3.36e+02]
    [ 3.68e+02]
    [ 4.04e+02]
    """
    if exp.size[0] != exp.size[1]:
        raise ValueError('exp must be square')
    from .expressions import AffinExp
    if not isinstance(exp, AffinExp):
        mat, name = retrieve_matrix(exp)
        exp = AffinExp({}, constant=mat[:], size=mat.size, string=name)
    (n, m) = exp.size
    newfacs = {}
    newrow = {}  # dict of new row indices
    nr = 0
    for i in range(n**2):
        col = i // n
        row = i % n
        if row >= col:
            newrow[i] = nr
            nr += 1
    nsz = nr  # this should be (n*(n+1))/2
    for var, mat in exp.factors.items():
        I, J, V = [], [], []
        for i, j, v in zip(mat.I, mat.J, mat.V):
            col = i // n
            row = i % n
            if row >= col:
                I.append(newrow[i])
                J.append(j)
                V.append(v)
        newfacs[var] = spmatrix(V, I, J, (nr, mat.size[1]))
    if exp.constant is None:
        newcons = None

    else:
        ncs = []
        for i, v in enumerate(cvx.matrix(exp.constant)):
            col = i // n
            row = i % n
            if row >= col:
                ncs.append(v)
        newcons = cvx.matrix(ncs, (nr, 1))

    return AffinExp(newfacs, newcons, (nr, 1),
        glyphs.makeFunction("lowtri")(exp.string))


def utri(mat):
    """
    return elements of the (strict) upper triangular part of a cvxopt matrix
    """
    m, n = mat.size
    if m != n:
        raise ValueError('mat must be square')
    v = []
    for j in range(1, n):
        for i in range(j):
            v.append(mat[i, j])
    return cvx.sparse(v)


def svecm1_identity(vtype, size):
    """
    row wise svec-1 transformation of the
    identity matrix of size size[0]*size[1]
    """
    if vtype in ('symmetric',):
        s0 = size[0]
        if size[1] != s0:
            raise ValueError('should be square')
        I = range(s0 * s0)
        J = []
        V = []
        for i in I:
            rc = (i % s0, i // s0)
            (r, c) = (min(rc), max(rc))
            j = c * (c + 1) // 2 + r
            J.append(j)
            if r == c:
                V.append(1)
            else:
                V.append(1 / np.sqrt(2))
        idmat = spmatrix(V, I, J, (s0 * s0, s0 * (s0 + 1) // 2))
    elif vtype == 'antisym':
        s0 = size[0]
        if size[1] != s0:
            raise ValueError('should be square')
        I = []
        J = []
        V = []
        k = 0
        for j in range(1, s0):
            for i in range(j):
                I.append(s0 * j + i)
                J.append(k)
                V.append(1)
                I.append(s0 * i + j)
                J.append(k)
                V.append(-1)
                k += 1
        idmat = spmatrix(V, I, J, (s0 * s0, s0 * (s0 - 1) // 2))
    else:
        sp = size[0] * size[1]
        idmat = spmatrix([1] * sp, range(sp), range(sp), (sp, sp))

    return idmat

def svecm1_identity_factor(factors, variable):
    """
    :returns: Whether the variable coefficients are the svec-1 transformation of
        the identity.
    """
    if variable not in factors:
        raise ValueError("There are no coefficients for the given variable.")

    factor   = factors[variable]
    identity = svecm1_identity(variable.vtype, variable.size)

    return list(factor.I) == list(identity.I) \
        and list(factor.J) == list(identity.J) \
        and list(factor.V) == list(identity.V)

def new_param(name, value):
    """
    Declare a parameter for the problem, that will be stored
    as a :func:`cvxopt sparse matrix <cvxopt:cvxopt.spmatrix>`.
    It is possible to give a list or a dictionary of parameters.
    The function returns a constant :class:`AffinExp <picos.expressions.AffinExp>`
    (or a ``list`` or a ``dict`` of :class:`AffinExp <picos.expressions.AffinExp>`) representing this parameter.

    .. note :: Declaring parameters is optional, since the expression can
                    as well be given by using normal variables. (see Example below).
                    However, if you use this function to declare your parameters,
                    the names of the parameters will be displayed when you **print**
                    an :class:`Expression <picos.expressions.Expression>` or a :class:`Constraint <picos.constraints.Constraint>`

    :param str name: The name given to this parameter.
    :param value: The value (resp ``list`` of values, ``dict`` of values) of the parameter.
                    The type of **value** (resp. the elements of the ``list`` **value**,
                    the values of the ``dict`` **value**) should be understandable by
                    the function :func:`retrieve_matrix() <picos.tools.retrieve_matrix>`.
    :returns: A constant affine expression (:class:`AffinExp <picos.expressions.AffinExp>`)
                    (resp. a ``list`` of :class:`AffinExp <picos.expressions.AffinExp>` of the same length as **value**,
                    a ``dict`` of :class:`AffinExp <picos.expressions.AffinExp>` indexed by the keys of **value**)

    **Example:**

    >>> import picos as pic
    >>> import cvxopt as cvx
    >>> prob=pic.Problem()
    >>> x=prob.add_variable('x',3)
    >>> B={'foo':17.4,'matrix':cvx.matrix([[1,2],[3,4],[5,6]]),'ones':'|1|(4,1)'}
    >>> B['matrix']*x+B['foo']
    <2×1 Affine Expression: [2×3]·x + [17.4]>
    >>> #(in the string above, |17.4| represents the 2-dim vector [17.4,17.4])
    >>> B=pic.new_param('B',B)
    >>> #now that B is a param, we have a nicer display:
    >>> B['matrix']*x+B['foo']
    <2×1 Affine Expression: B[matrix]·x + [B[foo]]>
    """
    from .expressions import AffinExp

    if isinstance(value, list):
        if all([is_numeric(x) for x in value]):
            # list with numeric data
            exp = AffinExp.fromMatrix(value)
            exp.string = name
        elif all([isinstance(x, list) for x in value]) \
        and  all([len(x) == len(value[0]) for x in value]) \
        and  all([is_realvalued(xi) for x in value for xi in x]):
            # list of numeric lists of the same length
            exp = AffinExp.fromMatrix(value, size = (len(value), len(value[0])))
            exp.string = name
        else:
            return [new_param(glyphs.slice(name, i), l)
                for i, l in enumerate(value)]
    elif isinstance(value, tuple):
        # Like with lists, but ignore numeric lists/tables.
        # TODO: Isn't this inconsistent?
        return [new_param(glyphs.slice(name, i), l) for i,l in enumerate(value)]
    elif isinstance(value, dict):
        return {k: new_param(glyphs.slice(name, k), l) for k,l in value.items()}
    else:
        exp = AffinExp.fromMatrix(value)
        exp.string = name

    return exp


def offset_in_lil(lil, offset, lower):
    """
    substract the ``offset`` from all elements of the
    (recursive) list of lists ``lil``
    which are larger than ``lower``.
    """
    for i, l in enumerate(lil):
        if is_integer(l):
            if l > lower:
                lil[i] -= offset
        elif isinstance(l, list):
            lil[i] = offset_in_lil(l, offset, lower)
        else:
            raise Exception('elements of lil must be int or list')
    return lil


def import_cbf(filename):
    """
    Imports the data from a CBF file, and creates a :class:`Problem
    <picos.Problem>` object.

    The created problem contains one (multidimmensional) variable
    for each cone specified in the section ``VAR`` of the .cbf file,
    and one (multidimmensional) constraint for each cone
    specified in the sections ``CON`` and ``PSDCON``.

    Semidefinite variables defined in the section ``PSDVAR`` of the .cbf file
    are represented by a matrix picos variable ``X`` with
    ``X.vtype = 'symmetric'``.

    This function returns a tuple ``(P,x,X,data)``,
    where:

     * ``P`` is the imported picos :class:`Problem <picos.Problem>` object.
     * ``x`` is a list of :class:`Variable <picos.expressions.Variable>`
       objects, representing the (multidimmensional) scalar variables.
     * ``X`` is a list of :class:`Variable <picos.expressions.Variable>`
       objects, representing the symmetric semidefinite positive variables.
     * ``data`` is a dictionary containing picos parameters (:class:`AffinExp
       <picos.expressions.AffinExp>` objects) used to define the problem.
       Indexing is with respect to the blocks of variables as defined in the
       sections ``VAR`` and  ``CON`` of the .cbf file.
    """
    from .problem import Problem
    P = Problem()
    x, X, data = P._read_cbf(filename)
    return (P, x, X, data)


def flatten(l):
    """ flatten a (recursive) list of list """
    for el in l:
        if hasattr(el, "__iter__") \
        and not (isinstance(el, str) or isinstance(el, bytes)):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def remove_in_lil(lil, elem):
    """ remove the element ``elem`` from a (recursive) list of list ``lil``.
        empty lists are removed if any"""
    if elem in lil:
        lil.remove(elem)
    for el in lil:
        if isinstance(el, list):
            remove_in_lil(el, elem)
            remove_in_lil(el, [])
    if [] in lil:
        lil.remove([])


def quad2norm(qd):
    """
    transform the list of bilinear terms qd
    in an equivalent squared norm
    (x.T Q x) -> ||Q**0.5 x||**2
    """
    # find all variables
    qdvars = []
    for xy in qd:
        p1 = (xy[0].startIndex, xy[0])
        p2 = (xy[1].startIndex, xy[1])
        if p1 not in qdvars:
            qdvars.append(p1)
        if p2 not in qdvars:
            qdvars.append(p2)
    # sort by start indices
    qdvars = sorted(qdvars)
    qdvars = [v for (i, v) in qdvars]
    offsets = {}
    ofs = 0
    for v in qdvars:
        offsets[v] = ofs
        ofs += v.size[0] * v.size[1]

    # construct quadratic matrix
    Q = spmatrix([], [], [], (ofs, ofs))
    I, J, V = [], [], []
    for (xi, xj), Qij in qd.items():
        oi = offsets[xi]
        oj = offsets[xj]
        Qtmp = spmatrix(Qij.V, Qij.I + oi, Qij.J + oj, (ofs, ofs))
        Q += 0.5 * (Qtmp + Qtmp.T)
    # cholesky factorization V.T*V=Q
    # remove zero rows and cols
    nz = set(Q.I)
    P = spmatrix(1., range(len(nz)), list(nz), (len(nz), ofs))
    Qp = P * Q * P.T
    try:
        import cvxopt.cholmod
        F = cvxopt.cholmod.symbolic(Qp)
        cvxopt.cholmod.numeric(Qp, F)
        Z = cvxopt.cholmod.spsolve(F, Qp, 7)
        V = cvxopt.cholmod.spsolve(F, Z, 4)
        V = V * P
    except ArithmeticError:  # Singular or Non-convex, we must work on the dense matrix
        import cvxopt.lapack
        sig = cvx.matrix(0., (len(nz), 1), tc='z')
        U = cvx.matrix(0., (len(nz), len(nz)))
        cvxopt.lapack.gees(cvx.matrix(Qp), sig, U)
        sig = sig.real()
        if min(sig) < -1e-7:
            raise NonConvexError('I cannot convert non-convex quads to socp')
        for i in range(len(sig)):
            sig[i] = max(sig[i], 0)
        V = cvx.spdiag(sig**0.5) * U.T
        V = cvx.sparse(V) * P
    allvars = qdvars[0]
    for v in qdvars[1:]:
        if v.size[1] == 1:
            allvars = allvars // v
        else:
            allvars = allvars // v[:]
    return abs(V * allvars)**2


def _copy_dictexp_to_new_vars(dct, cvars, complex=None):
    # cf function copy_exp_to_new_vars for an explanation of the 'complex'
    # argument
    D = {}
    import copy
    for var, value in dct.items():
        if isinstance(var, tuple):  # quad
            if var[0].vtype == 'hermitian' or var[1].vtype == 'hermitian':
                raise Exception('quadratic form involving hermitian variable')
            D[cvars[var[0].name], cvars[var[1].name]] = copy.copy(value)
        else:
            if complex is None:
                D[cvars[var.name]] = copy.copy(value)
                continue

            if var.vtype == 'hermitian' and (var.name + '_RE') in cvars:

                n = int(value.size[1]**(0.5))
                idasym = svecm1_identity('antisym', (n, n))

                if value.typecode == 'z':
                    vr = value.real()
                    D[cvars[var.name + '_IM_utri']] = -value.imag() * idasym
                    #!BUG corrected, in previous version (1.0.1)
                    #"no minus because value.imag()=-value.H.imag()" ???
                    # But maybe an other error was cancelling this bug...
                else:
                    vr = value
                    if complex:
                        D[cvars[var.name + '_IM_utri']] = spmatrix(
                            [], [], [],
                            (vr.size[0], cvars[var.name + '_IM_utri'].size[0]))

                vv = []
                for i in range(vr.size[0]):
                    v = vr[i, :]
                    AA = cvx.matrix(v, (n, n))
                    AA = (AA + AA.T) * 0.5  # symmetrize
                    vv.append(svec(AA).T)
                D[cvars[var.name + '_RE']] = cvx.sparse(vv)
                if complex:
                    # compute the imaginary part and append it.
                    if value.typecode == 'z':
                        Him = value.real()
                        vi = value.imag()
                    else:
                        Him = copy.copy(value)
                        vi = spmatrix([], [], [], Him.size)

                    n = int(vi.size[1]**(0.5))
                    vv = []
                    for i in range(vi.size[0]):
                        v = vi[i, :]
                        BB = cvx.matrix(v, (n, n))
                        BB = (BB + BB.T) * 0.5  # symmetrize
                        vv.append(svec(BB).T)
                    Hre = cvx.sparse(vv)

                    D[cvars[var.name + '_RE']
                      ] = cvx.sparse([D[cvars[var.name + '_RE']], Hre])
                    D[cvars[var.name + '_IM_utri']
                      ] = cvx.sparse([D[cvars[var.name + '_IM_utri']], Him * idasym])

            else:
                if value.typecode == 'z':
                    vr = value.real()
                    vi = value.imag()
                else:
                    vr = copy.copy(value)
                    vi = spmatrix([], [], [], vr.size)
                if complex:
                    D[cvars[var.name]] = cvx.sparse([vr, vi])
                else:
                    D[cvars[var.name]] = vr
    return D

# TODO: Give expressions a proper copy interface (yielding what affine
#       expressions they store).
def copy_exp_to_new_vars(exp, cvars, complex=None):
    # if complex=None (default), the expression is copied "as is"
    # if complex=False, the exp is assumed to be real_valued and
    #                  only the real part is copied to the new expression)
    # otherwise (complex=True), a new expression is created, which concatenates horizontally
    #           the real and the imaginary part
    from .expressions import Variable, AffinExp, Norm, LogSumExp, QuadExp, \
        GeneralFun, GeoMeanExp, NormP_Exp, TracePow_Exp, DetRootN_Exp, \
        SumExponential, KullbackLeibler
    import copy
    if isinstance(exp, Variable):
        if exp.vtype == 'hermitian':  # handle as AffinExp
            return copy_exp_to_new_vars('I' * exp, cvars, complex=complex)
        return cvars[exp.name]
    elif isinstance(exp, AffinExp):
        newfacs = _copy_dictexp_to_new_vars(
            exp.factors, cvars, complex=complex)
        if exp.constant is None:
            v = spmatrix([], [], [], (exp.size[0] * exp.size[1], 1))
        else:
            v = exp.constant
        if complex is None:
            newcons = copy.copy(v)
            newsize = exp.size
        elif complex:
            if v.typecode == 'z':
                vi = v.imag()
            else:
                vi = spmatrix([], [], [], v.size)
            newcons = cvx.sparse([v.real(), vi])
            newsize = (exp.size[0], 2 * exp.size[1])
        else:
            newcons = v.real()
            newsize = exp.size
        return AffinExp(newfacs, newcons, newsize, exp.string)
    elif isinstance(exp, Norm):
        newexp = copy_exp_to_new_vars(exp.exp, cvars, complex=complex)
        return Norm(newexp)
    elif isinstance(exp, LogSumExp):
        newexp = copy_exp_to_new_vars(exp.Exp, cvars, complex=complex)
        return LogSumExp(newexp)
    elif isinstance(exp, SumExponential):
        newexp = copy_exp_to_new_vars(exp.Exp, cvars, complex=complex)
        newexp2 = copy_exp_to_new_vars(exp.Exp2, cvars, complex=complex)
        return LogSumExp(newexp, newexp2)
    elif isinstance(exp, KullbackLeibler):
        newexp = copy_exp_to_new_vars(exp.Exp, cvars, complex=complex)
        newexp2 = copy_exp_to_new_vars(exp.Exp2, cvars, complex=complex)
        return KullbackLeibler(newexp, newexp2)
    elif isinstance(exp, QuadExp):
        newaff = copy_exp_to_new_vars(exp.aff, cvars, complex=complex)
        newqds = _copy_dictexp_to_new_vars(exp.quad, cvars, complex=complex)
        if exp.LR is None:
            return QuadExp(newqds, newaff, exp.string, None)
        else:
            LR0 = copy_exp_to_new_vars(exp.LR[0], cvars, complex=complex)
            LR1 = copy_exp_to_new_vars(exp.LR[1], cvars, complex=complex)
            return QuadExp(newqds, newaff, exp.string, (LR0, LR1))
    elif isinstance(exp, GeneralFun):
        newexp = copy_exp_to_new_vars(exp.Exp, cvars, complex=complex)
        return LogSumExp(exp.fun, newexp, exp.funstring)
    elif isinstance(exp, GeoMeanExp):
        newexp = copy_exp_to_new_vars(exp.exp, cvars, complex=complex)
        return GeoMeanExp(newexp)
    elif isinstance(exp, NormP_Exp):
        newexp = copy_exp_to_new_vars(exp.exp, cvars, complex=complex)
        return NormP_Exp(newexp, exp.numerator, exp.denominator)
    elif isinstance(exp, TracePow_Exp):
        newexp = copy_exp_to_new_vars(exp.exp, cvars, complex=complex)
        return TracePow_Exp(newexp, exp.numerator, exp.denominator)
    elif isinstance(exp, DetRootN_Exp):
        newexp = copy_exp_to_new_vars(exp.exp, cvars, complex=complex)
        return DetRootN_Exp(newexp)
    elif exp is None:
        return None
    else:
        raise Exception('unknown type of expression')


def _cplx_mat_to_real_mat(M):
    """
    if M = A +iB,
    return the block matrix [A,-B;B,A]
    """
    if not(isinstance(M, cvx.base.spmatrix) or isinstance(M, cvx.base.matrix)):
        raise NameError('unexpected matrix type')
    if M.typecode == 'z':
        A = M.real()
        B = M.imag()
    else:
        A = M
        B = spmatrix([], [], [], A.size)
    return cvx.sparse([[A, B], [-B, A]])


def cplx_vecmat_to_real_vecmat(M, sym=True, times_i=False):
    """
    If the columns of M are vectorizations of matrices of the form A +iB:
      * If times_i is False (default), return vectorizations of the block matrix
        [A, -B; B, A] otherwise, return vectorizations of the block matrix
        [-B, -A; A, -B].
      * If sym=True, returns the columns with respect to the sym-vectorization
        of the variables of the LMI.
    """
    if not(isinstance(M, cvx.base.spmatrix) or isinstance(M, cvx.base.matrix)):
        raise NameError('unexpected matrix type')

    if times_i:
        M = M * 1j

    mm = M.size[0]
    m = mm**0.5
    if int(m) != m:
        raise NameError('first dimension must be a perfect square')
    m = int(m)

    vv = []
    if sym:
        nn = M.size[1]
        n = nn**0.5
        if int(n) != n:
            raise NameError('2d dimension must be a perfect square')
        n = int(n)

        for k in range(n * (n + 1) // 2):
            j = int(np.sqrt(1 + 8 * k) - 1) // 2
            i = k - j * (j + 1) // 2
            if i == j:
                v = M[:, n * i + i]
            else:
                i1 = n * i + j
                i2 = n * j + i
                v = (M[:, i1] + M[:, i2]) * (1. / (2**0.5))
            vvv = _cplx_mat_to_real_mat(cvx.matrix(v, (m, m)))[:]
            vv.append([vvv])

    else:
        for i in range(M.size[1]):
            v = M[:, i]
            A = cvx.matrix(v, (m, m))
            vvv = _cplx_mat_to_real_mat(A)[:]  # TODO 0.5*(A+A.H) instead ?
            vv.append([vvv])

    return cvx.sparse(vv)


def is_idty(mat, vtype='continuous'):
    if vtype == 'continuous':
        if (mat.size[0] == mat.size[1]):
            n = mat.size[0]
            if (list(mat.I) == list(range(n)) and
                    list(mat.J) == list(range(n)) and
                    list(mat.V) == [1.] * n):
                return True
    elif vtype == 'antisym':
        n = int((mat.size[0])**0.5)
        if n != int(n) or n * (n - 1) // 2 != mat.size[1]:
            return False
        if not (svecm1_identity('antisym', (n, n)) - mat):
            return True
    return False


def is_integer(x):
    return (isinstance(x, INTEGER_TYPES) or
            isinstance(x, np.int64) or
            isinstance(x, np.int32))

def is_numeric(x):
    return (isinstance(x, float) or
            isinstance(x, INTEGER_TYPES) or
            isinstance(x, np.float64) or
            isinstance(x, np.int64) or
            isinstance(x, np.int32) or
            isinstance(x, np.complex128) or
            isinstance(x, complex))

def is_realvalued(x):
    return (isinstance(x, float) or
            isinstance(x, INTEGER_TYPES) or
            isinstance(x, np.float64) or
            isinstance(x, np.int64) or
            isinstance(x, np.int32))


def spmatrix(*args, **kwargs):
    """
    A wrapper around :func:`cvxopt.spmatrix` that converts indices to
    :class:`int`, if necessary.

    It works around PICOS sometimes passing indices as `numpy.int64`.
    """
    try:
        return cvx.spmatrix(*args, **kwargs)
    except TypeError as error:
        # CVXOPT does not like NumPy's int64 scalar type for indices, so attempt
        # to convert all indices to Python's int.
        if str(error) == "non-numeric type in list":
            newargs = list(args)

            for argNum, arg in enumerate(args):
                if argNum in (1, 2): # Positional I, J.
                    newargs[argNum] = [int(x) for x in args[argNum]]

            for kw in "IJ":
                if kw in kwargs:
                    kwargs[kw] = [int(x) for x in kwargs[kw]]

            return cvx.spmatrix(*newargs, **kwargs)
        else:
            raise


def kron(A,B):
    """
    Kronecker product of 2 expression, at least one of which must be constant

    **Example:**

    >>> import picos as pic
    >>> import cvxopt as cvx
    >>> import numpy as np
    >>> P = pic.Problem()
    >>> X = P.add_variable('X',(4,3))
    >>> X.value = cvx.matrix(range(12),(4,3))
    >>> I = pic.new_param('I',np.eye(2))
    >>> print(pic.kron(I,X)) #doctest: +NORMALIZE_WHITESPACE
    [ 0.00e+00  4.00e+00  8.00e+00  0.00e+00  0.00e+00  0.00e+00]
    [ 1.00e+00  5.00e+00  9.00e+00  0.00e+00  0.00e+00  0.00e+00]
    [ 2.00e+00  6.00e+00  1.00e+01  0.00e+00  0.00e+00  0.00e+00]
    [ 3.00e+00  7.00e+00  1.10e+01  0.00e+00  0.00e+00  0.00e+00]
    [ 0.00e+00  0.00e+00  0.00e+00  0.00e+00  4.00e+00  8.00e+00]
    [ 0.00e+00  0.00e+00  0.00e+00  1.00e+00  5.00e+00  9.00e+00]
    [ 0.00e+00  0.00e+00  0.00e+00  2.00e+00  6.00e+00  1.00e+01]
    [ 0.00e+00  0.00e+00  0.00e+00  3.00e+00  7.00e+00  1.10e+01]
    """

    from .expressions import AffinExp

    if not isinstance(A,AffinExp):
        expA, nameA = retrieve_matrix(A)
    else:
        expA, nameA = A,A.string

    if not isinstance(B,AffinExp):
        expB, nameB = retrieve_matrix(B)
    else:
        expB, nameB = B,B.string

    if expA.isconstant():
        AA = np.array(expA.valueAsMatrix)
        kron_fact = {}
        for x, Bx in expB.factors.items():
            #Blst contains matrix such that B=\sum x_i B_i (+constant)
            Blst = []
            AkronB = []
            for k in range(Bx.size[1]):
                Blst.append(np.reshape(cvx.matrix(Bx[:,k]),expB.size[::-1]).T)
                AkronB.append(np.kron(AA,Blst[-1]))
            kron_fact[x] = cvx.sparse([list(AkronB[k].T.ravel()) for k in range(Bx.size[1])])
        kron_cons = None
        if expB.constant:
            Bcons = np.reshape(cvx.matrix(expB.constant),expB.size[::-1]).T
            AkronB = np.kron(AA,Bcons)
            kron_cons = cvx.sparse(list(AkronB.T.ravel()))

        kron_size = (expA.size[0] * expB.size[0], expA.size[1] * expB.size[1])
    elif expB.isconstant():
        BB = np.array(expB.valueAsMatrix)
        kron_fact = {}
        for x, Ax in expA.factors.items():
            #Blst contains matrix such that B=\sum x_i B_i (+constant)
            Alst = []
            AkronB = []
            for k in range(Ax.size[1]):
                Alst.append(np.reshape(cvx.matrix(Ax[:,k]),expA.size[::-1]).T)
                AkronB.append(np.kron(Alst[-1],BB))
            kron_fact[x] = cvx.sparse([list(AkronB[k].T.ravel()) for k in range(Ax.size[1])])
        kron_cons = None
        if expA.constant:
            Acons = np.reshape(cvx.matrix(expA.constant),expA.size[::-1]).T
            AkronB = np.kron(Acons,BB)
            kron_cons = cvx.sparse(list(AkronB.T.ravel()))

        kron_size = (expA.size[0] * expB.size[0], expA.size[1] * expB.size[1])
    else:
        raise NotImplementedError('kron product with quadratic terms')

    kron_string = glyphs.kron(nameA, nameB)
    return AffinExp(
        kron_fact, constant=kron_cons, size=kron_size, string=kron_string)


def flow_Constraint(
        G, f, source, sink, flow_value, capacity=None, graphName=''):
    """
    Constructs a network flow constraint.

    :param G: A directed graph.
    :type G: `networkx DiGraph <http://networkx.lanl.gov/index.html>`_.

    :param dict f: A dictionary of variables indexed by the edges of ``G``.

    :param source: Either a node of ``G`` or a list of nodes in case of a
        multi-source flow.

    :param sink: Either a node of ``G`` or a list of nodes in case of a
        multi-sink flow.

    :param flow_value: The value of the flow, or a list of values in case of a
        single-source/multi-sink flow. In the latter case, the values represent
        the demands of each sink (resp. of each source for a
        multi-source/single-sink flow). The values can be either constants or
        :class:`affine expressions <picos.expressions.AffinExp>`.

    :param capacity: Either ``None`` or a string. If this is a string, it
        indicates the key of the edge dictionaries of ``G`` that is used for the
        capacity of the links. Otherwise, edges have an unbounded capacity.

    :param str graphName: Name of the graph as used in the string representation
        of the constraint.
    """
    from .constraints.meta_flow import FlowConstraint
    return FlowConstraint(
        G, f, source, sink, flow_value, capacity, graphName)


def drawGraph(G, capacity='capacity'):
    """"Draw a given Graph"""
    pos = nx.spring_layout(G)
    edge_labels = dict([((u, v,), d[capacity])
                        for u, v, d in G.edges(data=True)])
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw(G, pos)
    plt.show()


class NonWritableDict(dict):
    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        raise Exception('Cannot modify a non-writable dictionary.')

    def __delitem__(self, key):
        raise Exception('Cannot modify a non-writable dictionary.')

    def __copy__(self):
        new = self.__class__()
        for key, val in self.items():
            new._set(key, val)
        return new

    def __deepcopy__(self, memo):
        from copy import deepcopy
        new = self.__class__()
        for key, val in self.items():
            new._set(deepcopy(key), deepcopy(val))
        return new

    def _set(self, key, value):
        dict.__setitem__(self, key, value)

    def _del(self, key):
        dict.__delitem__(self, key)

    def _reset(self):
        for key in self.keys():
            self._del(key)


class QuadAsSocpError(Exception):
    """
    Exception raised when the problem can not be solved
    in the current form, because quad constraints are not handled.
    User should try to convert the quads as socp.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self): return self.msg

    def __repr__(self): return "QuadAsSocpError('" + self.msg + "')"


class NotAppropriateSolverError(Exception):
    """
    Exception raised when trying to solve a problem with
    a solver which cannot handle it
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self): return self.msg

    def __repr__(self): return "NotAppropriateSolverError('" + self.msg + "')"


class NonConvexError(Exception):
    """
    Exception raised when non-convex quadratic constraints
    are passed to a solver which cannot handle them.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self): return self.msg

    def __repr__(self): return "NonConvexError('" + self.msg + "')"


class DualizationError(Exception):
    """
    Exception raised when a non-standard conic problem is being dualized.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self): return self.msg

    def __repr__(self): return "DualizationError('" + self.msg + "')"
