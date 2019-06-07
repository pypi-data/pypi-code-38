#pylint: disable=too-many-lines,too-many-public-methods
"""
Steady-state system model of *hynet*.
"""

import logging

import numpy as np
from scipy.sparse import kron, coo_matrix

from hynet.types_ import hynet_int_, hynet_float_, hynet_complex_, hynet_sparse_
from hynet.utilities.base import (create_sparse_matrix,
                                  create_sparse_diag_matrix,
                                  create_sparse_zero_matrix,
                                  create_dense_vector,
                                  Timer)
from hynet.utilities.worker import workers
from hynet.utilities.graph import eliminate_parallel_edges
from hynet.qcqp.problem import QCQPPoint, ObjectiveFunction, Constraint, QCQP
from hynet.opf.result import OPFResult
from hynet.scenario.capability import ConverterCapRegion

_log = logging.getLogger(__name__)


def _call_and_concatenate(constraint_generator):
    """Calls the constraint generator and concatenates its result."""
    constraints = constraint_generator()
    if isinstance(constraints, tuple):
        constraints = np.concatenate(constraints)
    return constraints


class SystemModel:
    """
    System model for a steady-state scenario of a grid.

    Based on the specification of a scenario via a ``Scenario`` object, this
    class provides the methods to generate the corresponding system model
    equations and constraints as well as the associated optimal power flow
    (OPF) problem formulation. The state variables in this system model
    are the bus voltage vector ``v``, the converter state vector ``f``, the
    injector state vector ``s``, and the injector cost vector ``z``. The latter
    is actually not part of the system model but used for the reformulation of
    the piecewise linear active and reactive power cost functions of injectors.
    All state variables are considered in p.u., i.e., normalized.

    **Custom OPF Formulations:** The system model serves as a builder for the
    OPF problem. In order to customize the OPF formulation, one can define a
    corresponding system model by deriving from this class, implementing the
    additional constraint generators, registering them by overriding
    ``_get_constraint_generators``, and, if desired, overriding
    ``_get_opf_objective`` to customize the objective function. If additional
    variables are required, the auxiliary variable vector ``z`` may be expanded
    accordingly (override and increase ``dim_z`` and utilize the variables
    following the epigraph variables). If the customized OPF formulation
    necessitates a customized OPF result evaluation, implement the latter by
    deriving from ``OPFResult`` and associate this OPF result class with the
    system model by overriding ``create_opf_result``. To calculate a solution
    for the customized OPF, create an object of the specialized system model
    for the desired scenario and pass it to ``calc_opf``.

    See Also
    --------
    hynet.scenario.representation.Scenario:
        Specification of a steady-state grid scenario.
    hynet.opf.calc.calc_opf:
        Calculate an optimal power flow.
    """
    def __init__(self, scenario, verify_scenario=True):
        """
        Initialize the system model with the scenario data.

        Parameters
        ----------
        scenario : Scenario
            Steady-state scenario data for the model.
        verify_scenario : bool, optional
            If ``True`` (default), an integrity and validity check is performed
            on the provided scenario data (see ``Scenario.verify``). In case it
            is ensured beforehand that the provided data is consistent and
            valid, this check may be skipped to improve performance.
        """
        timer = Timer()
        if verify_scenario:
            scenario.verify()
        self._scr = scenario
        self._has_hybrid_architecture = self._scr.has_hybrid_architecture()
        self._islands = self._scr.get_islands()
        (self._Y, self._Y_src, self._Y_dst) = \
            SystemModel._get_admittance_matrices(self._scr)
        self._cost_scaling = self._select_cost_scaling(scenario)
        self._constraint_normalization = \
            self._select_constraint_normalization(scenario)
        _log.debug("Steady-state model creation ({:.3f} sec.)"
                   .format(timer.total()))

    @property
    def cost_function_scaling(self):
        """
        Return the cost function scaling used by ``get_cost_epigraph_constraints``.

        To improve the numerical conditioning of the OPF problem and,
        therewith, mitigate numerical issues with the solver, the cost
        functions are scaled. This scaling must be considered when including
        a loss term in the objective.
        """
        return self._cost_scaling

    @property
    def has_hybrid_architecture(self):
        """
        Return ``True`` if the system model features the *hybrid architecture*.

        **Remark:** This is determined at object construction and stored as a
        property for performance reasons.
        """
        return self._has_hybrid_architecture

    @property
    def islands(self):
        """
        Return a list with a pandas index of bus IDs for every islanded grid.

        **Remark:** This is determined at object construction and stored as a
        property for performance reasons.
        """
        return self._islands

    @staticmethod
    def _get_admittance_matrices(scenario):  # pylint: disable=too-many-locals
        """Return the bus, source, and destination admittance matrix."""
        N_E = scenario.num_branches
        N_V = scenario.num_buses

        e_src = scenario.e_src.values
        e_dst = scenario.e_dst.values

        rho_src = scenario.branch['rho_src'].values
        rho_dst = scenario.branch['rho_dst'].values
        rho = np.multiply(rho_src.conj(), rho_dst)

        y_tld = scenario.bus['y_tld'].values

        y_src = scenario.branch['y_src'].values
        y_dst = scenario.branch['y_dst'].values
        y_bar = 1 / scenario.branch['z_bar'].values

        alpha_src = np.multiply(np.square(np.abs(rho_src)), y_bar + y_src)
        alpha_dst = np.multiply(np.square(np.abs(rho_dst)), y_bar + y_dst)

        beta_src = -np.multiply(rho, y_bar)
        beta_dst = -np.multiply(rho.conj(), y_bar)

        alpha = y_tld + create_dense_vector(e_src, alpha_src, N_V) \
                      + create_dense_vector(e_dst, alpha_dst, N_V)

        Y_src = create_sparse_matrix(range(N_E), e_src, alpha_src, N_E, N_V) \
              + create_sparse_matrix(range(N_E), e_dst, beta_src, N_E, N_V)

        Y_dst = create_sparse_matrix(range(N_E), e_dst, alpha_dst, N_E, N_V) \
              + create_sparse_matrix(range(N_E), e_src, beta_dst, N_E, N_V)

        Y = create_sparse_diag_matrix(alpha) \
          + create_sparse_matrix(e_src, e_dst, beta_src, N_V, N_V) \
          + create_sparse_matrix(e_dst, e_src, beta_dst, N_V, N_V)

        # REMARK: The admittance matrices are primarily employed in row slicing
        # operations. For performance reasons, we thus use the CSR format here.
        return Y.tocsr(), Y_src.tocsr(), Y_dst.tocsr()

    @property
    def scenario(self):
        """Return the scenario data of the system model."""
        return self._scr

    @property
    def dim_v(self):
        """Return the dimension of the state variable ``v``."""
        return self._scr.num_buses

    @property
    def dim_f(self):
        """Return the dimension of the state variable ``f``."""
        return 4*self._scr.num_converters

    @property
    def dim_s(self):
        """Return the dimension of the state variable ``s``."""
        return 2*self._scr.num_injectors

    @property
    def dim_z(self):
        """Return the dimension of the state variable ``z``."""
        return 2*self._scr.num_injectors

    @property
    def Y(self):
        """Return the bus admittance matrix."""
        return self._Y

    @property
    def Y_src(self):
        """Return the source admittance matrix."""
        return self._Y_src

    @property
    def Y_dst(self):
        """Return the destination admittance matrix."""
        return self._Y_dst

    def get_normalization_factors(self):
        """
        Return the normalization factors of the state variables.

        Returns
        -------
        factors : QCQPPoint
            Contains the normalization factors of the state variables in the
            attributes ``v``, ``f``, ``s``, and ``z``.
        """
        return QCQPPoint(v=1.0,
                         f=1 / self._scr.base_mva,
                         s=1 / self._scr.base_mva,
                         z=self._cost_scaling)

    def _get_constraint_generators(self):
        """
        Return a list with all constraint generation functions.

        These constraint generation functions are used to generate the
        constraints of the OPF QCQP. Override this method in a derived class
        to **append** additional inequality constraints (The *first*
        constraint generator is assumed to return *equality constraints*,
        i.e., the power balance constraints, while all others are assumed to
        return *inequality constraints*, cf. ``get_opf_problem``).
        """
        return [self.get_balance_constraints,
                self.get_ampacity_constraints,
                self.get_real_part_constraints,
                self.get_angle_constraints,
                self.get_voltage_constraints,
                self.get_drop_constraints,
                self.get_converter_polyhedron_constraints,
                self.get_injector_polyhedron_constraints,
                self.get_cost_epigraph_constraints]

    def _get_opf_objective(self):
        """
        Return the objective function for the OPF problem formulation.

        Override this method in a derived class to customize the OPF objective.
        """
        N_I = self._scr.num_injectors

        if self._scr.loss_price != 0:
            (obj_C, obj_c) = self.get_dyn_loss_function()
            obj_C *= self._scr.loss_price * self._cost_scaling
            obj_c *= self._scr.loss_price * self._cost_scaling
        else:
            obj_C = create_sparse_zero_matrix(self.dim_v, self.dim_v)
            obj_c = create_sparse_zero_matrix(self.dim_f, 1)

        obj_r = np.zeros((self.dim_z, 1), dtype=hynet_float_)
        obj_r[:2*N_I, 0] = 1  # Cost function epigraph ordinate variables

        return ObjectiveFunction(C=obj_C,
                                 c=obj_c,
                                 a=create_sparse_zero_matrix(self.dim_s, 1),
                                 r=hynet_sparse_(obj_r),
                                 scaling=self._cost_scaling)

    def get_opf_problem(self):
        """
        Return the QCQP for the OPF problem of this system model.

        Returns
        -------
        qcqp : QCQP
            QCQP specification for the OPF problem associated with this
            system model.
        """
        timer = Timer()

        # Constraint generation (using parallel processing)
        constraints = workers.map(_call_and_concatenate,
                                  self._get_constraint_generators())

        # Variable bounds
        v_lb, v_ub = self.get_voltage_magnitude_bounds()
        f_lb, f_ub = self.get_converter_state_bounds()
        s_lb, s_ub = self.get_injector_state_bounds()
        z_lb, z_ub = self.get_cost_aux_var_bounds()

        qcqp = QCQP(obj_func=self._get_opf_objective(),
                    eq_crt=constraints[0],
                    ineq_crt=np.concatenate(constraints[1:]),
                    lb=QCQPPoint(v_lb, f_lb, s_lb, z_lb),
                    ub=QCQPPoint(v_ub, f_ub, s_ub, z_ub),
                    edges=eliminate_parallel_edges((self._scr.e_src.values,
                                                    self._scr.e_dst.values)),
                    roots=self._scr.get_ref_buses(),
                    normalization=self.get_normalization_factors())

        _log.debug("OPF QCQP creation ({:.3f} sec.)".format(timer.total()))
        return qcqp

    def create_opf_result(self, qcqp_result, total_time=np.nan):
        """
        Create and return an OPF result object.

        This method serves as a factory for an OPF result object using the OPF
        result class associated with this system model.

        Override this method in a derived class if the customized OPF
        formulation necessitates a customized result evaluation. The customized
        OPF class must be a specialization of ``OPFResult``.

        Parameters
        ----------
        qcqp_result : hynet.qcqp.result.QCQPResult
            Solution of the OPF QCQP.
        total_time : .hynet_float_, optional
            Total time for solving the OPF, cf. hynet.opf.calc.calc_opf.

        Returns
        -------
        result : hynet.opf.result.OPFResult
        """
        return OPFResult(self, qcqp_result, total_time=total_time)

    @staticmethod
    def _select_constraint_normalization(scenario):
        """
        Return the system constraint normalization factor.

        When applying a solver to the OPF problem, the achievable accuracy
        and/or the number of iterations usually depends on the conditioning of
        the optimization problem. Unfortunately, the OPF problem is a tough
        guy in that regard. In the description of the hybrid AC/DC power
        system model (cf. [1]_ and Appendix B in [2]_), it can be observed that
        the elements of the constraint matrices are either roughly close to 1,
        in the range of the series admittance of the branches (for the power
        balance constraints), or in the range of the series admittance squared
        (for the ampacity constraints). As the modulus of the smallest series
        admittance in a system is often rather large, this typically leads to
        several orders of magnitude of difference of the elements of the
        constraint matrices and, potentially, of the sensitivity of the
        constraint function values to changes in the bus voltage variables.
        This frequently leads to numerical issues in the employed solvers,
        especially for large-scale systems. To reduce the dynamic range in the
        constraint matrices, the power balance constraints are scaled by a
        normalization factor and the ampacity constraints by the square of the
        same normalization factor. This method returns an appropriately
        selected normalization factor.

        References
        ----------
        .. [1] M. Hotz and W. Utschick, "hynet: An optimal power flow framework
               for hybrid AC/DC power systems," arXiv:1811.10496, Nov. 2018.
               [Online]. Available: http://arxiv.org/abs/1811.10496
        .. [2] M. Hotz and W. Utschick, "A Hybrid Transmission Grid
               Architecture Enabling Efficient Optimal Power Flow," in IEEE
               Trans. Power Systems, vol. 31, no. 6, pp. 4504-4516, Nov. 2016.

        See Also
        --------
        hynet.model.steady_state.SystemModel.get_balance_constraints
        hynet.model.steady_state.SystemModel.get_ampacity_constraints
        """
        warning_threshold = 1e-4
        if scenario.num_branches == 0:
            return 1.0
        scaling = np.mean(np.abs(scenario.branch['z_bar'].values))
        if scaling < warning_threshold:
            _log.warning("The mean modulus of the series impedance is very "
                         "small ({:e} p.u.). This may cause numerical issues."
                         .format(scaling))
            scaling = warning_threshold
        return scaling

    def get_balance_constraints(self):  # pylint: disable=too-many-locals
        """Return the active and reactive power balance constraints."""
        timer = Timer()
        N_V = self._scr.num_buses
        N_C = self._scr.num_converters
        N_I = self._scr.num_injectors
        index = self._scr.bus.index
        c_src = self._scr.c_src.values
        c_dst = self._scr.c_dst.values
        n_src = self._scr.n_src.values
        scaling = self._constraint_normalization

        # CAVEAT: For better performance, the type conversion in the loop below
        # is made via .tocoo(). Update the code if the format has changed.
        assert hynet_sparse_ is coo_matrix

        load = self._scr.bus['load'].values / self._scr.base_mva

        loss_fix = self._scr.converter['loss_fix'].values / self._scr.base_mva
        loss_fwd = self._scr.converter['loss_fwd'].values / 100
        loss_bwd = self._scr.converter['loss_bwd'].values / 100

        # Accumulate static losses of converters at their respective source bus
        load += create_dense_vector(c_src, loss_fix, N_V)

        # Standard basis vectors in R^2 and R^4
        e1_R2 = create_sparse_matrix([0], [0], [1], 2, 1, dtype=hynet_float_)
        e2_R2 = create_sparse_matrix([1], [0], [1], 2, 1, dtype=hynet_float_)
        e1_R4 = create_sparse_matrix([0], [0], [1], 4, 1, dtype=hynet_float_)
        e2_R4 = create_sparse_matrix([1], [0], [1], 4, 1, dtype=hynet_float_)
        e3_R4 = create_sparse_matrix([2], [0], [1], 4, 1, dtype=hynet_float_)
        e4_R4 = create_sparse_matrix([3], [0], [1], 4, 1, dtype=hynet_float_)

        # Prepare calculation of vectors p_n and q_n
        A_src = create_sparse_matrix(range(N_C), c_src, np.ones(N_C), N_C, N_V,
                                     dtype=hynet_float_)
        A_dst = create_sparse_matrix(range(N_C), c_dst, np.ones(N_C), N_C, N_V,
                                     dtype=hynet_float_)
        B_src = create_sparse_matrix(range(N_C), c_src, 1 - loss_bwd, N_C, N_V,
                                     dtype=hynet_float_)
        B_dst = create_sparse_matrix(range(N_C), c_dst, 1 - loss_fwd, N_C, N_V,
                                     dtype=hynet_float_)

        # CSC format for efficient column slicing
        c_p = (kron(A_src, e1_R4) - kron(B_src, e2_R4) +
               kron(A_dst, e2_R4) - kron(B_dst, e1_R4)).tocsc()
        c_q = (-kron(A_src, e3_R4) - kron(A_dst, e4_R4)).tocsc()

        # Prepare calculation of vectors for injectors
        H = create_sparse_matrix(range(N_I), n_src, -np.ones(N_I), N_I, N_V,
                                 dtype=hynet_float_)

        # CSC format for efficient column slicing
        a_p = kron(H, e1_R2).tocsc()
        a_q = kron(H, e2_R2).tocsc()

        crt_p = np.ndarray(N_V, dtype=Constraint)
        crt_q = np.ndarray(N_V, dtype=Constraint)

        # Constraint scaling to improve conditioning
        # (See ``_select_constraint_normalization`` for more details)
        Y = self._Y * scaling
        c_p *= scaling
        c_q *= scaling
        a_p *= scaling
        a_q *= scaling
        load *= scaling

        for n in range(N_V):
            # REMARK to the construction of the matrices P_n and Q_n: To keep
            # the number of temporary matrices minimal, the construction of
            # P_n = (S_n + S_n^H) / 2 and Q_n = (S_n - S_n^H) / 2j utilizes the
            # fact that S_n consists of the conjugate transpose of the n-th row
            # of Y in its n-th column.
            y_n = Y[n, :].tocoo()
            idx_row = np.concatenate([y_n.col, y_n.row + n])
            idx_col = np.concatenate([y_n.row + n, y_n.col])
            P_n = create_sparse_matrix(idx_row, idx_col,
                                       np.concatenate([y_n.data.conj(),
                                                       y_n.data]) / 2,
                                       N_V, N_V, dtype=hynet_complex_)
            Q_n = create_sparse_matrix(idx_row, idx_col,
                                       np.concatenate([y_n.data.conj(),
                                                       -y_n.data]) / 2j,
                                       N_V, N_V, dtype=hynet_complex_)

            # Active power balance
            crt_p[n] = Constraint(name='bal_p',
                                  table='bus',
                                  id=index[n],
                                  C=P_n,
                                  c=c_p[:, n].tocoo(),
                                  a=a_p[:, n].tocoo(),
                                  r=None,
                                  b=-load[n].real,
                                  scaling=scaling / self._scr.base_mva)

            # Reactive power balance
            crt_q[n] = Constraint(name='bal_q',
                                  table='bus',
                                  id=index[n],
                                  C=Q_n,
                                  c=c_q[:, n].tocoo(),
                                  a=a_q[:, n].tocoo(),
                                  r=None,
                                  b=-load[n].imag,
                                  scaling=scaling / self._scr.base_mva)

        _log.debug("Power balance constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_p, crt_q

    def get_voltage_constraints(self):
        """Return the voltage magnitude lower and upper bound constraints."""
        timer = Timer()
        N_V = self._scr.num_buses
        index = self._scr.bus.index

        v_min_squared = np.square(self._scr.bus['v_min'].values)
        v_max_squared = np.square(self._scr.bus['v_max'].values)

        crt_v_min = np.ndarray(N_V, dtype=Constraint)
        crt_v_max = np.ndarray(N_V, dtype=Constraint)

        for n in range(N_V):
            M_n = create_sparse_matrix([n], [n], [1], N_V, N_V,
                                       dtype=hynet_float_)

            # Lower bound
            crt_v_min[n] = Constraint(name='v_min',
                                      table='bus',
                                      id=index[n],
                                      C=-M_n,
                                      c=None,
                                      a=None,
                                      r=None,
                                      b=-v_min_squared[n],
                                      scaling=1.0)

            # Upper bound
            crt_v_max[n] = Constraint(name='v_max',
                                      table='bus',
                                      id=index[n],
                                      C=M_n,
                                      c=None,
                                      a=None,
                                      r=None,
                                      b=v_max_squared[n],
                                      scaling=1.0)

        _log.debug("Voltage constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_v_min, crt_v_max

    def get_ampacity_constraints(self):
        """Return the source and destination ampacity constraints."""
        timer = Timer()
        N_E = self._scr.num_branches
        index = self._scr.branch.index
        scaling = self._constraint_normalization ** 2

        # CAVEAT: For better performance, the type conversion in the loop below
        # is made via .tocoo(). Update the code if the format has changed.
        assert hynet_sparse_ is coo_matrix

        # Maximum current is defined via apparent power flow rating at 1 p.u.
        rating = self._scr.branch['rating'].values
        I_max_squared = np.square(rating / self._scr.base_mva)

        # Allocate arrays for (non-omitted) constraint objects
        M = np.count_nonzero(~np.isnan(I_max_squared))
        crt_i_max_src = np.ndarray(M, dtype=Constraint)
        crt_i_max_dst = np.ndarray(M, dtype=Constraint)

        # Constraint scaling to improve conditioning
        # (See ``_select_constraint_normalization`` for more details)
        Y_src = self._Y_src * np.sqrt(scaling)
        Y_dst = self._Y_dst * np.sqrt(scaling)
        I_max_squared *= scaling

        m = 0
        for k in range(N_E):
            if np.isnan(I_max_squared[k]):
                continue

            # Flow limit at source bus
            Y_src_k = Y_src[k, :]
            I_src_k = Y_src_k.conj().transpose().dot(Y_src_k)
            crt_i_max_src[m] = Constraint(name='i_max_src',
                                          table='branch',
                                          id=index[k],
                                          C=I_src_k.tocoo(),
                                          c=None,
                                          a=None,
                                          r=None,
                                          b=I_max_squared[k],
                                          scaling=scaling)

            # Flow limit at destination bus
            Y_dst_k = Y_dst[k, :]
            I_dst_k = Y_dst_k.conj().transpose().dot(Y_dst_k)
            crt_i_max_dst[m] = Constraint(name='i_max_dst',
                                          table='branch',
                                          id=index[k],
                                          C=I_dst_k.tocoo(),
                                          c=None,
                                          a=None,
                                          r=None,
                                          b=I_max_squared[k],
                                          scaling=scaling)
            m += 1

        _log.debug("Ampacity constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_i_max_src, crt_i_max_dst

    def get_drop_constraints(self):
        """Return the voltage drop lower and upper bound constraints."""
        timer = Timer()
        N_V = self._scr.num_buses
        N_E = self._scr.num_branches
        index = self._scr.branch.index
        e_src = self._scr.e_src.values
        e_dst = self._scr.e_dst.values

        nu_min = self._scr.branch['drop_min'].values / 100
        nu_max = self._scr.branch['drop_max'].values / 100

        crt_drop_min = np.ndarray(np.count_nonzero(~np.isnan(nu_min)),
                                  dtype=Constraint)
        crt_drop_max = np.ndarray(np.count_nonzero(~np.isnan(nu_max)),
                                  dtype=Constraint)

        m_min = m_max = 0
        for k in range(N_E):
            src_dst = [e_src[k], e_dst[k]]

            # Lower bound on voltage drop
            if not np.isnan(nu_min[k]):
                M_min_k = create_sparse_matrix(src_dst, src_dst,
                                               [(1+nu_min[k]) ** 2, -1],
                                               N_V, N_V, dtype=hynet_float_)
                crt_drop_min[m_min] = Constraint(name='drop_min',
                                                 table='branch',
                                                 id=index[k],
                                                 C=M_min_k,
                                                 c=None,
                                                 a=None,
                                                 r=None,
                                                 b=0.0,
                                                 scaling=1.0)
                m_min += 1

            # Upper bound on voltage drop
            if not np.isnan(nu_max[k]):
                M_max_k = create_sparse_matrix(src_dst, src_dst,
                                               [-(1+nu_max[k]) ** 2, 1],
                                               N_V, N_V, dtype=hynet_float_)
                crt_drop_max[m_max] = Constraint(name='drop_max',
                                                 table='branch',
                                                 id=index[k],
                                                 C=M_max_k,
                                                 c=None,
                                                 a=None,
                                                 r=None,
                                                 b=0.0,
                                                 scaling=1.0)
                m_max += 1

        _log.debug("Voltage drop constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_drop_min, crt_drop_max

    def get_real_part_constraints(self):
        """
        Return the "real-part" constraints.

        These constraints ensure a precondition assumed by the voltage angle
        difference constraints, i.e., that the voltage angle difference is
        limited to +/- 90 degrees.
        """
        timer = Timer()
        N_V = self._scr.num_buses
        N_E = self._scr.num_branches
        index = self._scr.branch.index
        e_src = self._scr.e_src.values
        e_dst = self._scr.e_dst.values

        crt_real_part = np.ndarray(N_E, dtype=Constraint)

        for k in range(N_E):
            A_k = create_sparse_matrix([e_src[k], e_dst[k]],
                                       [e_dst[k], e_src[k]],
                                       [-1, -1], N_V, N_V, dtype=hynet_float_)
            crt_real_part[k] = Constraint(name='real_part',
                                          table='branch',
                                          id=index[k],
                                          C=A_k,
                                          c=None,
                                          a=None,
                                          r=None,
                                          b=0.0,
                                          scaling=1.0)

        _log.debug("Angle 'real-part' constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_real_part

    def get_angle_constraints(self):
        """
        Return the angle diff. lower and upper bound and "real-part" constraints.
        """
        timer = Timer()
        N_V = self._scr.num_buses
        N_E = self._scr.num_branches
        index = self._scr.branch.index
        e_src = self._scr.e_src.values
        e_dst = self._scr.e_dst.values

        tan_delta_min = np.tan(self._scr.branch['angle_min'].values * np.pi/180)
        tan_delta_max = np.tan(self._scr.branch['angle_max'].values * np.pi/180)

        crt_angle_min = np.ndarray(np.count_nonzero(~np.isnan(tan_delta_min)),
                                   dtype=Constraint)
        crt_angle_max = np.ndarray(np.count_nonzero(~np.isnan(tan_delta_max)),
                                   dtype=Constraint)

        m_min = m_max = 0
        for k in range(N_E):
            src_dst = [e_src[k], e_dst[k]]
            dst_src = src_dst[::-1]

            # Lower bound on angle difference
            if not np.isnan(tan_delta_min[k]):
                A_min_k = create_sparse_matrix(src_dst, dst_src,
                                               [tan_delta_min[k]+1j,
                                                tan_delta_min[k]-1j],
                                               N_V, N_V, dtype=hynet_complex_)
                crt_angle_min[m_min] = Constraint(name='angle_min',
                                                  table='branch',
                                                  id=index[k],
                                                  C=A_min_k,
                                                  c=None,
                                                  a=None,
                                                  r=None,
                                                  b=0.0,
                                                  scaling=1.0)
                m_min += 1

            # Upper bound on angle difference
            if not np.isnan(tan_delta_max[k]):
                A_max_k = create_sparse_matrix(src_dst, dst_src,
                                               [-tan_delta_max[k]-1j,
                                                -tan_delta_max[k]+1j],
                                               N_V, N_V, dtype=hynet_complex_)
                crt_angle_max[m_max] = Constraint(name='angle_max',
                                                  table='branch',
                                                  id=index[k],
                                                  C=A_max_k,
                                                  c=None,
                                                  a=None,
                                                  r=None,
                                                  b=0.0,
                                                  scaling=1.0)
                m_max += 1

        _log.debug("Angle difference constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_angle_min, crt_angle_max

    def get_converter_polyhedron_constraints(self):
        """Return the converter capability region polyhedron constraints."""
        timer = Timer()
        N_C = self._scr.num_converters
        index = self._scr.converter.index
        cap_src = self._scr.converter['cap_src'].values
        cap_dst = self._scr.converter['cap_dst'].values
        loss_fwd = self._scr.converter['loss_fwd'].values / 100
        loss_bwd = self._scr.converter['loss_bwd'].values / 100

        crt_conv_poly = np.ndarray((0,), dtype=Constraint)
        idx_col = np.zeros(4, dtype=hynet_int_)

        for l in range(N_C):
            A_src, b_src, name_src = cap_src[l].get_polyhedron('src', loss_bwd[l])
            A_dst, b_dst, name_dst = cap_dst[l].get_polyhedron('dst', loss_fwd[l])
            A = np.vstack((A_src, A_dst))
            b = np.concatenate((b_src, b_dst))
            name = ['src_' + x for x in name_src] + ['dst_' + x for x in name_dst]

            crt = np.ndarray(len(b), dtype=Constraint)
            idx_row = np.arange(4*l, 4*(l+1))

            # Create constraint objects for A*f_l <= b
            # (As f_l is normalized by base_mva, b is adjusted accordingly)
            for i in range(len(b)):
                crt[i] = Constraint(name='cap_' + name[i],
                                    table='converter',
                                    id=index[l],
                                    C=None,
                                    c=create_sparse_matrix(idx_row, idx_col,
                                                           A[i, :], 4*N_C, 1,
                                                           dtype=hynet_float_),
                                    a=None,
                                    r=None,
                                    b=b[i] / self._scr.base_mva,
                                    scaling=1 / self._scr.base_mva)

            crt_conv_poly = np.concatenate((crt_conv_poly, crt))

        _log.debug("Converter polyhedron constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_conv_poly

    def get_injector_polyhedron_constraints(self):
        """Return the injector capability region polyhedron constraints."""
        timer = Timer()
        N_I = self._scr.num_injectors
        index = self._scr.injector.index
        cap = self._scr.injector['cap'].values

        crt_inj_poly = np.ndarray((0,), dtype=Constraint)

        for j in range(N_I):
            A, b, name = cap[j].get_polyhedron()
            crt = np.ndarray(len(b), dtype=Constraint)

            # Create constraint objects for A*s_j <= b
            # (As s_j is normalized by base_mva, b is adjusted accordingly)
            for i in range(len(b)):
                crt[i] = Constraint(name='cap_' + name[i],
                                    table='injector',
                                    id=index[j],
                                    C=None,
                                    c=None,
                                    a=create_sparse_matrix([2*j, 2*j + 1],
                                                           [0, 0], A[i, :],
                                                           2*N_I, 1,
                                                           dtype=hynet_float_),
                                    r=None,
                                    b=b[i] / self._scr.base_mva,
                                    scaling=1 / self._scr.base_mva)

            crt_inj_poly = np.concatenate((crt_inj_poly, crt))

        _log.debug("Injector polyhedron constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_inj_poly

    def get_cost_epigraph_constraints(self):
        """Return the PWL cost function epigraph constraints."""
        timer = Timer()
        N_I = self._scr.num_injectors
        index = self._scr.injector.index
        cost_p = self._scr.injector['cost_p'].values
        cost_q = self._scr.injector['cost_q'].values

        crt_inj_epi = np.ndarray((0,), dtype=Constraint)
        a_scaling = self._scr.base_mva * self._cost_scaling

        for j in range(N_I):
            if cost_p[j] is not None:
                (A, b) = cost_p[j].get_epigraph_polyhedron()
                crt = np.ndarray(len(b), dtype=Constraint)

                # Create constraint objects for z_p_l*1 >= A*s_p_l + b
                for i in range(len(b)):
                    crt[i] = Constraint(name='inj_p_epi_' + str(i),
                                        table=None,
                                        id=index[j],
                                        C=None,
                                        c=None,
                                        a=create_sparse_matrix([2*j], [0],
                                                               [A[i] * a_scaling],
                                                               self.dim_s, 1,
                                                               dtype=hynet_float_),
                                        r=create_sparse_matrix([2*j], [0], [-1],
                                                               self.dim_z, 1,
                                                               dtype=hynet_float_),
                                        b=-b[i] * self._cost_scaling,
                                        scaling=self._cost_scaling)

                crt_inj_epi = np.concatenate((crt_inj_epi, crt))

            if cost_q[j] is not None:
                (A, b) = cost_q[j].get_epigraph_polyhedron()
                crt = np.ndarray(len(b), dtype=Constraint)

                # Create constraint objects for z_q_l*1 >= A*s_q_l + b
                for i in range(len(b)):
                    crt[i] = Constraint(name='inj_q_epi_' + str(i),
                                        table=None,
                                        id=index[j],
                                        C=None,
                                        c=None,
                                        a=create_sparse_matrix([2*j + 1], [0],
                                                               [A[i] * a_scaling],
                                                               self.dim_s, 1,
                                                               dtype=hynet_float_),
                                        r=create_sparse_matrix([2*j + 1], [0], [-1],
                                                               self.dim_z, 1,
                                                               dtype=hynet_float_),
                                        b=-b[i] * self._cost_scaling,
                                        scaling=self._cost_scaling)

                crt_inj_epi = np.concatenate((crt_inj_epi, crt))

        _log.debug("Cost function epigraph constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return crt_inj_epi

    def get_voltage_magnitude_bounds(self):
        """
        Return the voltage magnitude bounds ``v_lb <= |v| <= v_ub``.

        **Remark:** The voltage magnitude bounds are captured by
        ``get_voltage_constraints`` and, thus, this box constraint is actually
        redundant and only included to provide optimization variable bounds
        for the solver (which, for some solvers, can improve convergence).
        To avoid any impact on the dual variables of the voltage magnitude
        constraints (which e.g. was observed with MOSEK), these box constraints
        are loosened w.r.t. the limits employed in ``get_voltage_constraints``.
        """
        gap = 0.1 * self._scr.bus['v_max'].values  # Loosened by 10% of the UB
        v_lb = self._scr.bus['v_min'].values - gap
        v_ub = self._scr.bus['v_max'].values + gap
        return v_lb, v_ub

    def get_converter_state_bounds(self):
        """Return the converter state bounds ``f_lb <= f <= f_ub``."""
        N_C = self._scr.num_converters

        cap_src = self._scr.converter['cap_src'].values
        cap_dst = self._scr.converter['cap_dst'].values

        f_lb = np.zeros(4*N_C, dtype=hynet_float_)
        f_ub = np.zeros(4*N_C, dtype=hynet_float_)

        for l in range(N_C):
            (f_lb[4*l:4*(l+1)], f_ub[4*l:4*(l+1)]) = \
                ConverterCapRegion.get_box_constraint(cap_src[l], cap_dst[l])

        return f_lb / self._scr.base_mva, f_ub / self._scr.base_mva

    def get_injector_state_bounds(self):
        """Return the injector state bounds ``s_lb <= s <= s_ub``."""
        N_I = self._scr.num_injectors

        cap = self._scr.injector['cap'].values

        s_lb = np.zeros(2*N_I, dtype=hynet_float_)
        s_ub = np.zeros(2*N_I, dtype=hynet_float_)

        for j in range(N_I):
            s_lb[2*j:2*(j+1)] = (cap[j].p_min, cap[j].q_min)
            s_ub[2*j:2*(j+1)] = (cap[j].p_max, cap[j].q_max)

        return s_lb / self._scr.base_mva, s_ub / self._scr.base_mva

    def get_cost_aux_var_bounds(self):
        """
        Return the auxiliary cost variable bounds ``z_lb <= z <= z_ub``.

        The lower and upper bound is set to ``numpy.nan`` if the corresponding
        bound should be omitted.
        """
        N_I = self._scr.num_injectors

        cost_p = self._scr.injector['cost_p'].values
        cost_q = self._scr.injector['cost_q'].values

        z_lb = np.nan * np.ones(self.dim_z, dtype=hynet_float_)
        z_ub = np.nan * np.ones(self.dim_z, dtype=hynet_float_)

        for j in range(N_I):
            if cost_p[j] is None:
                z_lb[2*j] = z_ub[2*j] = 0
            if cost_q[j] is None:
                z_lb[2*j + 1] = z_ub[2*j + 1] = 0

        return z_lb, z_ub

    def get_dyn_loss_function(self):
        """
        Return ``(C, c)`` for the total dyn. loss ``L(v,f) = v^H C v + c^T f``.
        """
        e1_R4 = create_sparse_matrix([0], [0], [1], 4, 1, dtype=hynet_float_)
        e2_R4 = create_sparse_matrix([1], [0], [1], 4, 1, dtype=hynet_float_)

        loss_fwd = self._scr.converter['loss_fwd'].values / 100
        loss_bwd = self._scr.converter['loss_bwd'].values / 100

        C = (self._Y + self._Y.conj().transpose()) / 2
        c = kron(loss_fwd.reshape((-1, 1)), e1_R4) + \
            kron(loss_bwd.reshape((-1, 1)), e2_R4)
        return (hynet_sparse_(C * self._scr.base_mva),
                hynet_sparse_(c * self._scr.base_mva))

    @staticmethod
    def _select_cost_scaling(scenario):
        """
        Return a suitable scaling factor for the objective of the OPF problem.
        """
        cost_p = scenario.injector['cost_p'].values
        cost_q = scenario.injector['cost_q'].values
        cap = scenario.injector['cap'].values
        load = scenario.bus['load'].values

        max_cost = 0
        for (f_p, f_q, cr) in zip(cost_p, cost_q, cap):
            if f_p is not None:
                max_cost = np.max([max_cost,
                                   np.max(np.abs(
                                       f_p.evaluate([cr.p_min, cr.p_max])))])
            if f_q is not None:
                max_cost = np.max([max_cost,
                                   np.max(np.abs(
                                       f_q.evaluate([cr.q_min, cr.q_max])))])

        if max_cost == 0:
            # Looks like we are facing loss minimization...
            if scenario.loss_price > 0:
                return 1 / (scenario.loss_price * scenario.base_mva)
            else:
                return 1.0

        max_inj = np.max([1,
                          np.max([np.abs([x.p_min, x.p_max,
                                          x.q_min, x.q_max]).max()
                                  for x in cap]) / scenario.base_mva,
                          np.max([np.abs([x.real, x.imag]).max()
                                  for x in load]) / scenario.base_mva
                          ])

        if max_cost > max_inj:
            return max_inj / max_cost
        return 1

    def calc_dynamic_losses(self, operating_point):
        """
        Return the total dynamic losses in MW for the given operating point.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.
        """
        v = operating_point.v
        f = operating_point.f / self._scr.base_mva
        (C, c) = self.get_dyn_loss_function()
        return (v.conj().dot(C.dot(v)) + c.transpose().dot(f)).item().real

    def calc_shunt_apparent_power(self, operating_point):
        """
        Return the shunt apparent power in MVA for the given operating point.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.
        """
        v = operating_point.v
        y_tld = self._scr.bus['y_tld'].values
        s_shunt = np.multiply(y_tld.conj(), np.square(np.abs(v)))
        return s_shunt * self._scr.base_mva

    def calc_branch_flow(self, operating_point):
        """
        Return the flow on the branches for the given operating point.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.

        Returns
        -------
        i_src : numpy.ndarray[.hynet_float_]
            Branch current flow in p.u. at the source bus.
        i_dst : numpy.ndarray[.hynet_float_]
            Branch current flow in p.u. at the destination bus.
        s_src : numpy.ndarray[.hynet_complex_]
            Branch apparent power flow in MVA at the source bus.
        s_dst : numpy.ndarray[.hynet_complex_]
            Branch apparent power flow in MVA at the destination bus.
        """
        v = operating_point.v
        e_src = self._scr.e_src.values
        e_dst = self._scr.e_dst.values

        i_src = self._Y_src.dot(v)
        i_dst = self._Y_dst.dot(v)
        s_src = np.multiply(v[e_src], i_src.conj()) * self._scr.base_mva
        s_dst = np.multiply(v[e_dst], i_dst.conj()) * self._scr.base_mva
        return i_src, i_dst, s_src, s_dst

    def calc_branch_voltage_drop(self, operating_point):
        """
        Return the relative voltage magnitude drop along the branches.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.
        """
        v = operating_point.v
        e_src = self._scr.e_src.values
        e_dst = self._scr.e_dst.values
        v_drop = np.true_divide(np.abs(v[e_dst]), np.abs(v[e_src])) - 1
        return v_drop

    def calc_branch_angle_difference(self, operating_point):
        """
        Return the voltage angle difference along the branches in degrees.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.
        """
        v = operating_point.v
        e_src = self._scr.e_src.values
        e_dst = self._scr.e_dst.values
        angle_diff = np.angle(np.multiply(v[e_src].conj(), v[e_dst])) * 180/np.pi
        return angle_diff

    def calc_branch_effective_rating(self, operating_point):
        """
        Return the ampacity rating in MVA rating at the current bus voltages.

        In the scenario data, the branch flow is limited by an ampacity rating
        that is specified in terms of a long-term MVA rating at a bus voltage
        of 1 p.u.. Correspondingly, the ampacity rating translates to a
        different MVA rating if the bus voltages differ from 1 p.u.. This
        function returns the ampacity rating in MVA at the current bus
        voltages, i.e., the rating at 1 p.u. times the actual voltage.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.
        """
        v_abs = np.abs(operating_point.v)
        e_src = self._scr.e_src.values
        e_dst = self._scr.e_dst.values
        effective_rating = np.multiply(self._scr.branch['rating'].values,
                                       np.maximum(v_abs[e_src], v_abs[e_dst]))
        return effective_rating

    def calc_converter_flow(self, operating_point):
        """
        Return the apparent power flow into the converters.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.

        Returns
        -------
        s_src : numpy.ndarray[.hynet_complex_]
            Apparent power flow in MVA into the converter at the source bus.
        s_dst : numpy.ndarray[.hynet_complex_]
            Apparent power flow in MVA into the converter at the destination bus.
        """
        p_src = operating_point.f[0::4]
        p_dst = operating_point.f[1::4]
        q_src = operating_point.f[2::4]
        q_dst = operating_point.f[3::4]
        loss_fwd = self._scr.converter['loss_fwd'].values / 100
        loss_bwd = self._scr.converter['loss_bwd'].values / 100

        s_src = p_src - np.multiply(1 - loss_bwd, p_dst) - 1j*q_src
        s_dst = p_dst - np.multiply(1 - loss_fwd, p_src) - 1j*q_dst
        return s_src, s_dst

    def calc_injection_costs(self, operating_point):
        """
        Return the injector's active and reactive power injection costs in dollars.

        Parameters
        ----------
        operating_point : QCQPPoint
            Operating point of the system *without* the normalization of the
            state variables (except the voltage), i.e., as provided by an
            OPF result.

        Returns
        -------
        cost_p : numpy.ndarray[.hynet_complex_]
            Cost of the active power injection in dollars.
        cost_q : numpy.ndarray[.hynet_complex_]
            Cost of the reactive power injection in dollars.
        """
        s = operating_point.s[0::2] + 1j*operating_point.s[1::2]
        cost_p = np.nan * np.ones(self._scr.num_injectors, dtype=hynet_float_)
        cost_q = np.nan * np.ones(self._scr.num_injectors, dtype=hynet_float_)
        cost_iter = zip(s,
                        self._scr.injector['cost_p'].values,
                        self._scr.injector['cost_q'].values)

        for j, (s_j, f_p, f_q) in enumerate(cost_iter):
            if f_p is not None:
                cost_p[j] = f_p.evaluate(s_j.real)
            if f_q is not None:
                cost_q[j] = f_q.evaluate(s_j.imag)
        return cost_p, cost_q
