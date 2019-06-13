#pylint: disable=anomalous-backslash-in-string
"""
Representation of a *hynet*-specific QCQP.
"""

import logging
from collections import namedtuple
import copy

import numpy as np
import scipy.sparse

from hynet.types_ import hynet_int_, hynet_float_, hynet_sparse_
from hynet.utilities.worker import workers
from hynet.utilities.base import (create_sparse_matrix,
                                  create_sparse_diag_matrix,
                                  Timer)

_log = logging.getLogger(__name__)


class QCQPPoint:
    """
    Point in the space of the optimization variables of the QCQP problem.

    Parameters
    ----------
    v : numpy.ndarray[.hynet_complex_] or numpy.ndarray[.hynet_float_]
    f : numpy.ndarray[.hynet_float_]
    s : numpy.ndarray[.hynet_float_]
    z : numpy.ndarray[.hynet_float_]
    """
    def __init__(self, v, f, s, z):
        self.v = v
        self.f = f
        self.s = s
        self.z = z

    def scale(self, scaling):
        """
        Scale the point by ``scaling``.

        Parameters
        ----------
        scaling : QCQPPoint or .hynet_float_
            Scaling factor, which can either be a numeric value, to scale all
            variables equally, or a QCQP point, to scale the variables
            individually, where the attributes ``v``, ``f``, ``s``, and ``z``
            specify the scaling factor for the corresponding variable.
        """
        if isinstance(scaling, QCQPPoint):
            scaling_v = scaling.v
            scaling_f = scaling.f
            scaling_s = scaling.s
            scaling_z = scaling.z
        else:
            scaling_v = scaling_f = scaling_s = scaling_z = scaling
        if self.v is not None:
            self.v *= scaling_v
        if self.f is not None:
            self.f *= scaling_f
        if self.s is not None:
            self.s *= scaling_s
        if self.z is not None:
            self.z *= scaling_z
        return self

    def reciprocal(self):
        """Set the point to the element-wise reciprocal of the variables."""
        if self.v is not None:
            self.v = 1 / self.v
        if self.f is not None:
            self.f = 1 / self.f
        if self.s is not None:
            self.s = 1 / self.s
        if self.z is not None:
            self.z = 1 / self.z
        return self

    def copy(self):
        """Return a deep copy of this point."""
        return copy.deepcopy(self)

    def __repr__(self):
        return ("QCQPPoint("
                + "v=" + repr(self.v) + ", "
                + "f=" + repr(self.f) + ", "
                + "s=" + repr(self.s) + ", "
                + "z=" + repr(self.z) + ")")


class ObjectiveFunction:
    """
    Specifies an objective ``g(v,f,s,z) = v^H C v + c^T f + a^T s + r^T z``.

    Parameters
    ----------
    C : .hynet_sparse_
        Hermitian matrix ``C`` of the objective function.
    c : .hynet_sparse_
        Vector ``c`` of the objective function.
    a : .hynet_sparse_
        Vector ``a`` of the objective function.
    r : .hynet_sparse_
        Vector ``r`` of the objective function.
    scaling : .hynet_float_
        Scaling factor for the objective.
    """
    def __init__(self, C, c, a, r, scaling):
        self.C = C
        self.c = c
        self.a = a
        self.r = r
        self.scaling = scaling

    def evaluate(self, p):
        """
        Evaluate the function, i.e., return ``y = g(v, f, s, z)``.

        Parameters
        ----------
        p : QCQPPoint
            Point that specifies ``v``, ``f``, ``s``, and ``z``.

        Returns
        -------
        y : .hynet_float_
            Function value ``y`` at the given point ``p``.
        """
        return (p.v.conj().transpose().dot(self.C.dot(p.v)).real
                + self.c.transpose().dot(p.f)
                + self.a.transpose().dot(p.s)
                + self.r.transpose().dot(p.z)).item()

    def __repr__(self):
        return ("ObjectiveFunction("
                + "C=" + ("None" if self.C is None else "<mtx>") + ", "
                + "c=" + ("None" if self.c is None else "<vec>") + ", "
                + "a=" + ("None" if self.a is None else "<vec>") + ", "
                + "r=" + ("None" if self.r is None else "<vec>")
                + " | scaling={:.3e})".format(self.scaling))


class Constraint(namedtuple('ConstraintBase', ['name', 'table', 'id',
                                               'C', 'c', 'a', 'r', 'b',
                                               'scaling'])):
    """
    Specifies a constraint ``v^H C v + c^T f + a^T s + r^T z <=/== b``.

    Parameters
    ----------
    name : str
        Name of the constraint and column name for the result table generation
        in ``QCQPResult``.
    table : str or None
        Name of the table with which this constraint is associated. This is
        used to generate the result tables in ``QCQPResult``. Set to ``None``
        to ignore the associated values during the result table generation.
    id : .hynet_id_
        Identifier of the row with which this constraint is associated. This is
        used to generate the result tables in ``QCQPResult``.
    C : .hynet_sparse_ or None
        Hermitian matrix ``C`` of the constraint function or ``None`` if this
        term is omitted.
    c : .hynet_sparse_ or None
        Vector ``c`` of the constraint function or ``None`` if this term is
        omitted.
    a : .hynet_sparse_ or None
        Vector ``a`` of the constraint function or ``None`` if this term is
        omitted.
    r : .hynet_sparse_ or None
        Vector ``r`` of the constraint function or ``None`` if this term is
        omitted.
    b : .hynet_float_
        Right-hand side scalar ``b`` of the constraint.
    scaling : .hynet_float_
        Scaling factor of the constraint.
    """
    def evaluate(self, p):
        """
        Return ``y = v^H C v + c^T f + a^T s + r^T z - b``.

        Parameters
        ----------
        p : QCQPPoint
            Point that specifies ``v``, ``f``, ``s``, and ``z``.

        Returns
        -------
        y : .hynet_float_
            Constraint value ``y`` at the given point ``p``.
        """
        result = -self.b
        if self.C is not None:
            result += p.v.conj().transpose().dot(self.C.dot(p.v)).real.item()
        if self.c is not None:
            result += self.c.transpose().dot(p.f).item()
        if self.a is not None:
            result += self.a.transpose().dot(p.s).item()
        if self.r is not None:
            result += self.r.transpose().dot(p.z).item()
        return result

    def __repr__(self):
        return "{0.name}:{0.id}".format(self)


class QCQP:
    """
    Specification of a quadratically constrained quadratic program::

            min   v^H C v + c^T f + a^T s + r^T z
          v,f,s,z

            s.t.  v^H C'_i v + c'_i^T f + a'_i^T s + r'_i^T z == b'_i, i = 1,...,N
                  v^H C"_j v + c"_j^T f + a"_j^T s + r"_j^T z <= b"_j, j = 1,...,M
                  v_lb <= |v| <= v_ub
                  f_lb <=  f  <= f_ub
                  s_lb <=  s  <= s_ub
                  z_lb <=  z  <= z_ub

    The vector ``v`` is complex-valued, while ``f``, ``s``, and ``z`` are
    real-valued. The bounds on ``|v|`` are optional to implement by the solver.
    They are assumed to be captured by the inequality constraints, while
    ``v_lb`` and ``v_ub`` may be used to support convergence of the solver.
    In contrary, the bounds on ``f``, ``s``, and ``z`` are mandatory to
    implement. A bound is ignored if the respective element is set to
    ``numpy.nan``.

    The objective function, constraint functions, and optimization variables
    may be scaled to improve the numerical conditioning of the problem. All
    coefficient matrices, coefficient vectors, bounds as well as the initial
    point, if provided, must be specified for the *scaled* problem. The scaling
    factors for the objective and the constraints can be specified via their
    ``scaling`` attribute, while the scaling of the optimization variables is
    defined via ``normalization`` (see below). This scaling information is
    utilized in ``QCQPResult`` to adjust the optimizer, the optimal value, and
    the dual variables to represent the solution of the unscaled problem.

    **Caution:** If the QCQP object is used in repeated computations with
    modifications of the constraints, the constraint vectorization buffering
    must be deactivated, see ``use_buffered_vectorization``.

    Parameters
    ----------
    obj_func : ObjectiveFunction
        Specification of the objective function.
    eq_crt : numpy.ndarray[Constraint]
        Specification of the equality constraints.
    ineq_crt : numpy.ndarray[Constraint]
        Specification of the inequality constraints.
    lb : QCQPPoint
        Specification of the lower bounds on ``|v|``, ``f``, ``s``, and ``z``.
    ub : QCQPPoint
        Specification of the upper bounds on ``|v|``, ``f``, ``s``, and ``z``.
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Specification of the sparsity pattern of the lower-triangular part of
        the constraint matrices via the edges ``(edge_src, edge_dst)`` of an
        undirected graph. The constraint matrices may only have nonzero entries
        in row/column ``edge_src[i]`` and column/row ``edge_dst[i]``, with
        ``i in range(K)`` where ``K = len(edge_src) = len(edge_dst)``, as well
        as on the diagonal. The edges specified in ``edges`` must be *unique*,
        i.e., there must not exist any parallel or anti-parallel edges, and
        must refer to the *lower-triangular part*, i.e., ``edges[0] > edges[1]``.
        If case of any doubts, call ``hynet.utilities.graph.eliminate_parallel_edges``
        before assigning.
    roots : numpy.ndarray[.hynet_int_]
        Root nodes of the undirected graph defined by ``edges`` that specifies
        the sparsity pattern. At these root nodes the absolute angle of the
        optimal ``v`` is set to zero. (Note that, due to the quadratic form in
        ``v``, the optimal objective value is invariant w.r.t. an absolute phase
        shift within a connected component of the sparsity-defining graph.)
    normalization : QCQPPoint
        The attributes ``v``, ``f``, ``s``, and ``z`` specify the scaling of
        the corresponding optimization variable. This scaling is considered
        in the creation of the QCQP result, where the optimal value as well
        as the dual variables of the box constraints are adjusted accordingly.
    initial_point : QCQPPoint or None
        Initial point for the solver or None if omitted. (The initial point
        is typically only utilized in solvers for the nonconvex QCQP, but
        ignored in SDR and SOCR solvers.)
    use_buffered_vectorization : bool
        If True (default), the constraint vectorization is buffered to avoid
        its repeated computation. This QCQP object supports a vectorized
        representation, which is primarily intended for solver interfaces
        of relaxations, cf. ``get_vectorization``. As the vectorization of the
        constraints is computationally demanding, the result is buffered and
        reused if called repeatedly. If the *constraints are modified* between
        the calls, the buffering must be deactivated to update the
        vectorization.
    """

    def __init__(self, obj_func, eq_crt, ineq_crt, lb, ub, edges, roots,
                 normalization=None, initial_point=None,
                 use_buffered_vectorization=True):
        if not np.all(edges[0] > edges[1]):
            raise RuntimeError("The edges of the sparsity graph must specify "
                               "the pattern of the lower-triangular part.")
        self.obj_func = obj_func
        self.eq_crt = eq_crt
        self.ineq_crt = ineq_crt
        self.lb = lb
        self.ub = ub
        self.edges = edges
        self.roots = roots
        if normalization is not None:
            self.normalization = normalization
        else:
            self.normalization = QCQPPoint(v=1.0, f=1.0, s=1.0, z=1.0)
        self.initial_point = initial_point
        self.use_buffered_vectorization = use_buffered_vectorization
        self._vectorization_buffer = None

    @property
    def dim_v(self):
        """Return the dimension of the ambient space of ``v``."""
        return len(self.lb.v)

    @property
    def dim_f(self):
        """Return the dimension of the ambient space of ``f``."""
        return len(self.lb.f)

    @property
    def dim_s(self):
        """Return the dimension of the ambient space of ``s``."""
        return len(self.lb.s)

    @property
    def dim_z(self):
        """Return the dimension of the ambient space of ``z``."""
        return len(self.lb.z)

    @property
    def num_edges(self):
        """Return the number of edges in the sparsity-defining graph."""
        return len(self.edges[0])

    def __repr__(self):
        return ('QCQP(v:C^{0}, f:R^{1}, s:R^{2}, z:R^{3} | '
                '#EQ={4}, #INEQ={5}, #edges={6}, #roots={7})'
                ).format(self.dim_v, self.dim_f, self.dim_s, self.dim_z,
                         len(self.eq_crt), len(self.ineq_crt),
                         self.num_edges, len(self.roots))

    def _mtx2vec(self, A):
        """
        Return a vector "``a^T``" such that ``tr(A*V) = a^T v_tld``.

        Therein, ``v_tld`` is the vectorization of ``V`` as used in the
        vectorized problem. The matrix ``A`` is assumed to be Hermitian and
        to exhibit the sparsity pattern defined by the edges.

        **Remark:** For a Hermitian matrix ``A`` and ``V``, the inner product
        ``tr(A*V)`` is the sum of the product of their diagonal elements plus
        two times the sum of the product of the real and imaginary part of the
        off-diagonal elements. In this vectorization, the factor of two is
        included in the vectorization of the coefficient matrix ``A``, while
        the vectorization ``v_tld`` of the optimization variable ``V`` only
        comprises the stacking of the respective variables. (Note that, for
        symmetry reasons, the off-diagonal elements are typically scaled by
        ``sqrt(2)``, but we deviate from that due to implementation reasons.)
        """
        if self.num_edges:
            A = A.tocsr()  # Conversion to CSR for indexing
            A_offd = np.asarray(A[self.edges[0], self.edges[1]])[0]
            return hynet_sparse_(np.concatenate((A.diagonal().real,
                                                 2*A_offd.real,
                                                 2*A_offd.imag)))
        return hynet_sparse_(A.diagonal().real)

    def _vectorize_constraints(self, constraints):
        """
        Return ``(A, b)`` that represent the constraints in vectorized form.

        This method reformulates the given constraints of the form
        ::

            v^H C_i v + c_i^T f + a_i^T s + r_i^T z <=/== b_i

        into
        ::

            [ _mtx2vec(C_i), c_i^T, a_i^T, r_i^T ] x <=/== b_i

        with x as defined in the documentation of ``get_vectorization`` and
        _mtx2vec as defined in the member function of the same name of this
        class. Finally, the vectorized constraints are stacked, i.e.,
        ::

            [ _mtx2vec(C_1), c_1^T, a_1^T, r_1^T ]         [b_1]
            [                                    ]         [   ]
            [ ...                                ] x <=/== [...]
            [                                    ]         [   ]
            [ _mtx2vec(C_N), c_N^T, a_N^T, r_N^T ]         [b_N]

            \____________________________________/         \___/
                             A                     x <=/==   b

        Parameters
        ----------
        constraints : Iterable[Constraint]
            Constraint that shall be vectorized.

        Returns
        -------
        A : .hynet_sparse_
        b : numpy.ndarray[.hynet_float_]
        """
        timer = Timer()
        ofs_v_real = self.dim_v
        ofs_v_imag = ofs_v_real + self.num_edges
        ofs_c = ofs_v_imag + self.num_edges
        ofs_a = ofs_c + self.dim_f
        ofs_r = ofs_a + self.dim_s
        dim_x = ofs_r + self.dim_z

        aux = _AuxiliaryData(ofs_v_real=ofs_v_real,
                             ofs_v_imag=ofs_v_imag,
                             ofs_c=ofs_c,
                             ofs_a=ofs_a,
                             ofs_r=ofs_r,
                             dim_x=dim_x,
                             e_src=self.edges[0],
                             e_dst=self.edges[1])

        data = zip(range(len(constraints)),
                   constraints,
                   [aux] * len(constraints))

        result_list = workers.starmap(_vectorize_constraint, data)

        list_idx_row, list_idx_col, list_data = zip(*result_list)
        A = create_sparse_matrix(np.concatenate(list_idx_row),
                                 np.concatenate(list_idx_col),
                                 np.concatenate(list_data),
                                 len(constraints), dim_x, dtype=hynet_float_)
        b = np.array([crt.b for crt in constraints], dtype=hynet_float_)

        _log.debug("Constraint vectorization ({:.3f} sec.)"
                   .format(timer.total()))
        return A, b

    def get_constraint_vectorization(self):
        """
        Return a vectorized representation of the constraints.

        This class supports a vectorized representation of the QCQP, see
        ``get_vectorization`` for more details. This method returns the
        parameters for the vectorization of the equality and inequality
        constraints, i.e., ``Ax == b`` and ``Bx <= d``.

        See Also
        --------
        hynet.qcqp.problem.QCQP.get_vectorization

        Returns
        -------
        A, b, B, d : tuple
            Vectorization of the equality and inequality constraints.
        """
        if self.use_buffered_vectorization and \
                self._vectorization_buffer is not None:
            _log.debug("Constraint vectorization ~ Using buffered result.")
            return self._vectorization_buffer

        A, b = self._vectorize_constraints(self.eq_crt)
        B, d = self._vectorize_constraints(self.ineq_crt)
        self._vectorization_buffer = (A, b, B, d)  # Buffer the vectorization

        return A, b, B, d

    def get_vectorization(self):
        """
        Return a vectorized representation of this QCQP::

            min   c^T x   s.t.   Ax == b,  Bx <= d,  x_lb <= x <= x_ub
             x

        This representation is primarily intended for solver interfaces to
        *relaxations* of the QCQP and based on a reformulation in three steps,
        i.e.,

        1)  The complex-valued optimization variable ``v`` is replaced by a
            matrix ``V``::

                v^H C v = tr(v^H C v) = tr(Cvv^H) = tr(CV) with V = vv^H

            For equivalence to the original problem, ``V`` must be Hermitian
            (``V = V^H``), positive semidefinite (``V >= 0``) and have rank 1
            (``rank(V) = 1``). **Note that this vectorization does not take
            care of this, it only reformulates the problem in in terms of
            ``V``.** (For example, the semidefinite relaxation will include
            the psd constraint but omit the rank constraint.)

        2)  The sparsity of the constraint matrices is utilized to reduce the
            number of effective variables and vectorize the matrices, i.e.,
            ::

                tr(CV) = c_vec^T v_tld

            where ``c_vec = self._mtx2vec(C)`` and
            ::

                v_tld = [V_{1,1}                       ^
                         ...                           | N = self.dim_v
                         V_{N,N}                       v
                         real(V_{e_src(1),e_dst(1)}    ^
                         ...                           | K = self.num_edges
                         real(V_{e_src(K),e_dst(K)}    v
                         imag(V_{e_src(1),e_dst(1)}    ^
                         ...                           | K = self.num_edges
                         imag(V_{e_src(K),e_dst(K)}]   v

        3)  All optimization variables are stacked, i.e.,
            ::

                x = [v_tld^T, f^T, s^T, z^T]^T

            and the objective as well as the equality, inequality, and box
            constraints are adapted accordingly.

        **Caution:** This representation is **only reasonable with additional
        constraints** on the ``v_tld``-part of ``x``. For example, psd
        constraints on principal submatrices for the SOC relaxation or a psd
        constraint on the "reassembled" matrix ``V`` for the SDR.

        Returns
        -------
        (c, A, b, B, d, x_lb, x_ub) : tuple
            Parameters of the vectorized QCQP representation.
        """
        timer = Timer()

        c = hynet_sparse_(scipy.sparse.vstack(
            (
                self._mtx2vec(self.obj_func.C).transpose(),
                self.obj_func.c,
                self.obj_func.a,
                self.obj_func.r
            )))

        A, b, B, d = self.get_constraint_vectorization()

        v_bnd_od = np.multiply(self.ub.v[self.edges[0]],
                               self.ub.v[self.edges[1]])
        x_lb = np.concatenate((np.square(self.lb.v),
                               -v_bnd_od,
                               -v_bnd_od,
                               self.lb.f,
                               self.lb.s,
                               self.lb.z
                               ))
        x_ub = np.concatenate((np.square(self.ub.v),
                               v_bnd_od,
                               v_bnd_od,
                               self.ub.f,
                               self.ub.s,
                               self.ub.z
                               ))

        _log.debug("QCQP vectorization ({:.3f} sec.)".format(timer.total()))
        return c, A, b, B, d, x_lb, x_ub

    def split_vectorization_optimizer(self, x):
        """
        Return ``(V, f, s, z)`` for the optimizer ``x`` of the vectorized problem.

        The partitioning in ``x`` is assumed as defined in ``get_vectorization``.
        The vectorized representation ``v_tld`` of ``V`` is retracted, i.e.,
        ``V`` is populated with the diagonal and off-diagonal elements
        specified by ``v_tld``.
        """
        (e_src, e_dst) = self.edges
        N = self.dim_v
        K = self.num_edges
        ofs = 0

        V_diag = x[ofs:(ofs + N)]
        ofs += N
        V_offd = x[ofs:(ofs + K)] + 1j * x[(ofs + K):(ofs + 2*K)]
        ofs += 2*K

        f = x[ofs:(ofs + self.dim_f)]
        ofs += self.dim_f

        s = x[ofs:(ofs + self.dim_s)]
        ofs += self.dim_s

        z = x[ofs:(ofs + self.dim_z)]
        ofs += self.dim_z

        V = create_sparse_diag_matrix(V_diag) \
          + create_sparse_matrix(e_src, e_dst, V_offd, N, N) \
          + create_sparse_matrix(e_dst, e_src, V_offd.conj(), N, N)

        return hynet_sparse_(V), f, s, z

    def split_vectorization_bound_dual(self, dual_var):
        """
        Return the dual variable of a bound on ``x`` as a QCQP point.

        Splits the dual variable of a bound on the optimization variable ``x``
        of the vectorized problem (``x >= x_lb`` or ``x <= x_ub``) into the
        dual variables of the respective bound on ``f``, ``s``, and ``z`` and
        returns them as a QCQP point (with ``v`` set to ``None`` as the
        respective magnitude bounds are optional).

        Parameters
        ----------
        dual_var : numpy.ndarray[.hynet_float_]
            Dual variable of a bound on ``x`` of the vectorized problem.

        Returns
        -------
        point : QCQPPoint
            QCQP point with the dual variables of the respective bounds on
            ``|v|``, ``f``, ``s``, and ``z``.
        """
        (_, dv_f, dv_s, dv_z) = self.split_vectorization_optimizer(dual_var)
        return QCQPPoint(v=None, f=dv_f, s=dv_s, z=dv_z)


class _AuxiliaryData(namedtuple('_AuxiliaryData',
                                ['ofs_v_real', 'ofs_v_imag', 'ofs_c', 'ofs_a',
                                 'ofs_r', 'dim_x', 'e_src', 'e_dst'])):
    """
    Auxiliary data for the parallelization of constraint vectorization.
    """
    pass


def _vectorize_constraint(i, crt, aux):
    """
    Return the sparse data for the vectorized constraint at position ``i``.

    See Also
    --------
    hynet.qcqp.problem.QCQP._vectorize_constraints
    """
    # This vectorization was a bottleneck of the code and I had to sacrifice
    # readability for performance. I apologize for any inconvenience caused ;)
    list_idx_row = []
    list_idx_col = []
    list_data = []

    if crt.C is not None:
        # The following code corresponds to the operation of QCQP._mtx2vec
        C_diag = crt.C.diagonal().real
        idx_col = C_diag.nonzero()[0]
        if idx_col.size:
            list_idx_row.append(i + np.zeros(len(idx_col), dtype=hynet_int_))
            list_idx_col.append(idx_col)
            list_data.append(C_diag[idx_col])
        if aux.e_src.size:
            C_offd = np.asarray(crt.C.tocsr()[aux.e_src, aux.e_dst])[0]
            idx_col = C_offd.nonzero()[0]
            if idx_col.size:
                idx_row = i + np.zeros(len(idx_col), dtype=hynet_int_)
                data = C_offd[idx_col]
                list_idx_row.append(idx_row)
                list_idx_col.append(idx_col + aux.ofs_v_real)
                list_data.append(2*data.real)
                list_idx_row.append(idx_row)
                list_idx_col.append(idx_col + aux.ofs_v_imag)
                list_data.append(2*data.imag)
    if crt.c is not None:
        # REMARK: This code includes the transposition by exchanging
        # the row and column index and it utilizes the fact that the
        # column indices are always zero to avoid an additional vector
        # allocation. The same applies to crt.a and crt.r.
        if crt.c.row.size:
            list_idx_row.append(crt.c.col + i)
            list_idx_col.append(crt.c.row + aux.ofs_c)
            list_data.append(crt.c.data)
    if crt.a is not None:
        if crt.a.row.size:
            list_idx_row.append(crt.a.col + i)
            list_idx_col.append(crt.a.row + aux.ofs_a)
            list_data.append(crt.a.data)
    if crt.r is not None:
        if crt.r.row.size:
            list_idx_row.append(crt.r.col + i)
            list_idx_col.append(crt.r.row + aux.ofs_r)
            list_data.append(crt.r.data)

    if list_idx_row:
        row = np.concatenate(list_idx_row)
        col = np.concatenate(list_idx_col)
        data = np.concatenate(list_data)
    else:
        row = col = np.ndarray(0, dtype=hynet_int_)
        data = np.ndarray(0, dtype=hynet_float_)

    return row, col, data
