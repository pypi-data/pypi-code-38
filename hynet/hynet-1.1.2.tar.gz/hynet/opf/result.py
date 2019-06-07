#pylint: disable=line-too-long,too-many-lines,too-many-statements,anomalous-backslash-in-string
"""
Representation of an optimal power flow result.
"""

import logging
import os.path
from collections import OrderedDict

import numpy as np
import pandas as pd

from hynet import __version__ as hynet_version
from hynet.types_ import hynet_float_, BusType, BranchType, SolverType, SolverStatus
from hynet.utilities.base import Timer, truncate_with_ellipsis
import hynet.config as config

_log = logging.getLogger(__name__)


class OPFResult:
    """
    Result of an optimal power flow calculation.

    **Remark:** In the data frames below, the respective column for the dual
    variables of a type of constraint (e.g., voltage drop) is only present if
    at least one constraint of this constraint type appears in the problem
    formulation.

    Parameters
    ----------
    model : SystemModel
        Steady-state model for which the optimal power flow was calculated.
    empty : bool
        ``True`` if the object does not contain any result data and ``False``
        otherwise.
    solver : SolverInterface
        Solver object by which the result was obtained.
    solver_status : SolverStatus
        Status reported by the solver.
    solver_time : float
        Duration of the call to the solver in seconds.
    optimal_value : float
        Optimal objective value or ``numpy.nan`` if the solver failed.
    total_time : float or numpy.nan
        Total time for the OPF calculation, including loading of the data (if
        applicable), modeling, solving, and result assembly. If not provided,
        this time is set to ``numpy.nan``.
    is_physical : bool
        Unavailable if the result is empty and, otherwise, ``True`` if the
        power balance equations hold with reasonable accuracy.
    reconstruction_mse : float
        Unavailable if the result is empty and, otherwise, the mean squared
        error of the reconstructed bus voltages in case of a relaxation and
        ``numpy.nan`` otherwise.
    total_injection_cost : float
        Unavailable if the result is empty and, otherwise, the total injection
        cost in $/h.
    dynamic_losses : float
        Unavailable if the result is empty and, otherwise, the dynamic losses
        in MW.
    total_losses : float
        Unavailable if the result is empty and, otherwise, the total losses in
        MW (dynamic losses plus the static losses of the converters).

    bus : pandas.DataFrame, optional
        Unavailable if the result is empty and, otherwise, a data frame with
        the bus result data, indexed by the *bus ID*, which comprises the
        following columns:

        ``v``: (``hynet_complex_``)
            Bus voltage rms phasor (AC) or bus voltage magnitude (DC).
        ``s_shunt``: (``hynet_complex_``)
            Shunt apparent power in MVA. The real part constitutes the shunt
            losses in MW and the *negated* imaginary part constitutes the
            reactive power *injection*.
        ``dv_v_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage lower bound in $/p.u..
        ``dv_v_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage upper bound in $/p.u..
        ``dv_bal_p``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power balance
            constraint in $/MW. In case of exactness of the relaxation (or
            zero duality gap in the QCQP), these dual variables equal the
            locational marginal prices (LMPs) for active power, cf. [1]_.
        ``dv_bal_q``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power balance
            constraint in $/Mvar. In case of exactness of the relaxation (or
            zero duality gap in the QCQP), these dual variables equal the
            locational marginal prices (LMPs) for reactive power, cf. [1]_.
        ``bal_err``: (``hynet_complex_``)
            Power balance residual in MVA, i.e., the evaluation of the
            complex-valued power balance equation at the system state.
            Theoretically, this should be identical to zero, but due to a
            limited solver accuracy and/or inexactness of the relaxation it is
            only approximately zero. This residual supports the assessment of
            solution accuracy and validity.

    branch : pandas.DataFrame, optional
        Unavailable if the result is empty and, otherwise, a data frame with
        the branch result data, indexed by the *branch ID*, which comprises the
        following columns:

        ``s_src``: (``hynet_complex_``)
            Apparent power flow in MVA at the source bus (measured as a flow
            *into* the branch).
        ``s_dst``: (``hynet_complex_``)
            Apparent power flow in MVA at the destination bus (measured as a
            flow *into* the branch).
        ``i_src``: (``hynet_complex_``)
            Current flow in p.u. at the source bus (measured as a flow
            *into* the branch).
        ``i_dst``: (``hynet_complex_``)
            Current flow in p.u. at the destination bus (measured as a flow
            *into* the branch).
        ``v_drop``: (``hynet_float_``)
            Relative voltage magnitude drop from the source bus to the
            destination bus.
        ``angle_diff``: (``hynet_float_``)
            Bus voltage angle difference in degrees between the source and
            destination bus.
        ``effective_rating``: (``hynet_float_``)
            Ampacity in terms of a long-term MVA rating at the *actual* bus
            voltage. If no rating is available, it is set to ``numpy.nan``.
        ``rel_err``: (``hynet_float_``)
            Branch-related relative reconstruction error
            :math:`\kappa_k(V^\star)` as defined in equation (24) in [1]_ in
            case of a relaxed OPF or ``numpy.nan`` otherwise.
        ``dv_i_max_src``: (``hynet_float_``)
            Dual variable or KKT multiplier of the ampacity constraint at the
            source bus in $/p.u. or ``numpy.nan`` if unavailable.
        ``dv_i_max_dst``: (``hynet_float_``)
            Dual variable or KKT multiplier of the ampacity constraint at the
            destination bus in $/p.u. or ``numpy.nan`` if unavailable.
        ``dv_angle_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the angle difference lower bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_angle_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the angle difference upper bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_real_part``: (``hynet_float_``)
            Dual variable or KKT multiplier of the +/-90 degrees constraint
            on the angle difference (cf. equation (27) in [2]_) or
            ``numpy.nan`` if unavailable.
        ``dv_drop_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage drop lower bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_drop_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage drop upper bound
            constraint or ``numpy.nan`` if unavailable.

    converter : pandas.DataFrame
        Unavailable if the result is empty and, otherwise, a data frame with
        the converter result data, indexed by the *converter ID*, which
        comprises the following columns:

        ``p_src``: (``hynet_complex_``)
            Active power flow in MW at the source bus *into the converter*.
        ``p_dst``: (``hynet_complex_``)
            Active power flow in MW at the destination bus *into the
            converter*.
        ``q_src``: (``hynet_complex_``)
            Reactive power injection in Mvar at the source bus *into the grid*.
        ``q_dst``: (``hynet_complex_``)
            Reactive power injection in Mvar at the destination bus *into the
            grid*.
        ``dv_cap_src_p_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power lower bound
            of the capability region at the source bus in $/MW or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region at the source bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_p_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power upper bound
            of the capability region at the source bus in $/MW or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region at the source bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_p_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power lower bound
            of the capability region at the destination bus in $/MW or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region at the destination bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_p_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power upper bound
            of the capability region at the destination bus in $/MW or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region at the destination bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.

    injector : pandas.DataFrame
        Unavailable if the result is empty and, otherwise, a data frame with
        the injector result data, indexed by the *injector ID*, which comprises
        the following columns:

        ``s``: (``hynet_complex_``)
            Apparent power injection in MVA.
        ``cost_p``: (``hynet_float_``)
            Cost of the active power injection in dollars or ``numpy.nan`` if
            no cost function was provided.
        ``cost_q``: (``hynet_float_``)
            Cost of the reactive power injection in dollars or ``numpy.nan`` if
            no cost function was provided.
        ``dv_cap_p_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power lower bound
            of the capability region in $/MW or ``numpy.nan`` if unavailable.
        ``dv_cap_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region in $/Mvar or ``numpy.nan`` if unavailable.
        ``dv_cap_p_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power upper bound
            of the capability region in $/MW or ``numpy.nan`` if unavailable.
        ``dv_cap_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region in $/Mvar or ``numpy.nan`` if unavailable.
        ``dv_cap_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.
        ``dv_cap_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.
        ``dv_cap_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.
        ``dv_cap_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.

    References
    ----------
    .. [1] M. Hotz and W. Utschick, "The Hybrid Transmission Grid Architecture:
           Benefits in Nodal Pricing," in IEEE Trans. Power Systems, vol. 33,
           no. 2, pp. 1431-1442, Mar. 2018.
    .. [2] M. Hotz and W. Utschick, "A Hybrid Transmission Grid Architecture
           Enabling Efficient Optimal Power Flow," in IEEE Trans. Power
           Systems, vol. 31, no. 6, pp. 4504-4516, Nov. 2016.
    """

    # Result printing: Threshold on zero values to be replaced by a dash
    _zero_thres = 1e-8

    # Result printing: Tolerance factor for activity indicator w.r.t.
    # constraint interval
    _tol_active = 0.005

    # Result printing: Ratio w.r.t. to rating for indication of high loading
    _high_loading = 0.9

    # Physical solution: A sufficiently accurate power balance.
    #
    # 1) Maximum nodal error limit: Threshold on the ratio of the maximum nodal
    #    apparent power balance error to the largest load or injection.
    _bal_err_nodal_thres = 1e-3
    #
    # 2) Maximum total error limit: Threshold on the ratio of the total active
    #    power balance error to the total active power load.
    _bal_err_total_thres = 1e-3

    def __init__(self, model, qcqp_result, total_time=np.nan):
        """
        Create an OPF result object.

        Parameters
        ----------
        model : hynet.model.steady_state.SystemModel
            System model for which the OPF was performed.
        qcqp_result : hynet.qcqp.result.QCQPResult
            Solution of the OPF QCQP.
        total_time : .hynet_float_, optional
            Total time for solving the OPF, cf. hynet.opf.calc.calc_opf.
        """
        timer = Timer()
        self.model = model
        self.total_time = total_time

        # REMARK: Only relevant data of the QCQP result object is extracted
        # here as storing it in its entirety would bloat the OPF result object
        # due to the constraint objects in the contained QCQP object, which
        # exhibit a significant memory consumption.
        self.empty = qcqp_result.empty
        self.solver = qcqp_result.solver
        self.solver_status = qcqp_result.solver_status
        self.solver_time = qcqp_result.solver_time
        self.optimal_value = qcqp_result.optimal_value
        self._optimizer = qcqp_result.optimizer

        if qcqp_result.empty:
            return

        # Bus-related state data
        s_shunt = self.model.calc_shunt_apparent_power(self._optimizer)

        self.bus = pd.DataFrame(OrderedDict(
            [('v', self._optimizer.v),
             ('s_shunt', s_shunt)
             ]))
        self.bus.index = self.model.scenario.bus.index

        # Branch-related state data
        i_src, i_dst, s_src, s_dst = self.model.calc_branch_flow(self._optimizer)
        v_drop = self.model.calc_branch_voltage_drop(self._optimizer)
        angle_diff = self.model.calc_branch_angle_difference(self._optimizer)
        effective_rating = self.model.calc_branch_effective_rating(self._optimizer)

        self.branch = pd.DataFrame(OrderedDict(
            [('s_src', s_src),
             ('s_dst', s_dst),
             ('i_src', i_src),
             ('i_dst', i_dst),
             ('v_drop', v_drop),
             ('angle_diff', angle_diff),
             ('effective_rating', effective_rating)
             ]))
        self.branch.index = self.model.scenario.branch.index

        # Converter-related state data
        s_src, s_dst = self.model.calc_converter_flow(self._optimizer)

        self.converter = pd.DataFrame(OrderedDict(
            [('p_src', s_src.real),
             ('p_dst', s_dst.real),
             ('q_src', -s_src.imag),
             ('q_dst', -s_dst.imag)
             ]))
        self.converter.index = self.model.scenario.converter.index

        # Injector-related state data
        cost_p, cost_q = self.model.calc_injection_costs(self._optimizer)

        self.injector = pd.DataFrame(OrderedDict(
            [('s', self._optimizer.s[0::2] + 1j*self._optimizer.s[1::2]),
             ('cost_p', cost_p),
             ('cost_q', cost_q)
             ]))
        self.injector.index = self.model.scenario.injector.index

        # Mean squared and branch-related reconstruction error
        self.reconstruction_mse = qcqp_result.reconstruction_mse
        if qcqp_result.V is not None:
            edges = (self.model.scenario.e_src.values,
                     self.model.scenario.e_dst.values)
            rel_err = self.solver.rank1approx.calc_rel_err(qcqp_result.V,
                                                           self._optimizer.v,
                                                           edges)
        else:
            rel_err = np.nan * np.ones(self.model.scenario.num_branches,
                                       dtype=hynet_float_)

        self.branch.loc[:, 'rel_err'] = pd.Series(rel_err,
                                                  index=self.branch.index)

        # Dual variables of the box constraints
        #
        # REMARK 1: As the QCQP considers the variables in p.u., the dual
        # variables must be scaled accordingly to capture the sensitivity in
        # $/MW and $/Mvar, respectively.
        #
        # REMARK 2: The active power limits of the converter capability regions
        # are implemented via inequalities, see also ``ConverterCapRegion``,
        # and thus their dual variables are not extracted here.
        self.injector['dv_cap_p_min'] = qcqp_result.dv_lb.s[0::2]
        self.injector['dv_cap_q_min'] = qcqp_result.dv_lb.s[1::2]

        self.injector['dv_cap_p_max'] = qcqp_result.dv_ub.s[0::2]
        self.injector['dv_cap_q_max'] = qcqp_result.dv_ub.s[1::2]

        self.converter['dv_cap_src_q_min'] = qcqp_result.dv_lb.f[2::4]
        self.converter['dv_cap_dst_q_min'] = qcqp_result.dv_lb.f[3::4]

        self.converter['dv_cap_src_q_max'] = qcqp_result.dv_ub.f[2::4]
        self.converter['dv_cap_dst_q_max'] = qcqp_result.dv_ub.f[3::4]

        # Dual variables and constraint function values
        timer.interval()
        qcqp_result.get_result_tables(tables={'bus': self.bus,
                                              'branch': self.branch,
                                              'converter': self.converter,
                                              'injector': self.injector},
                                      dual_prefix='dv_',
                                      value_prefix='cv_')
        _log.debug("Result table creation ({:.3f} sec.)"
                   .format(timer.interval()))

        self.bus.loc[:, 'bal_err'] = self.bus['cv_bal_p'] + 1j*self.bus['cv_bal_q']
        self.bus.drop(['cv_bal_p', 'cv_bal_q'], axis='columns', inplace=True)

        # Total injection cost
        self.total_injection_cost = 0
        if not self.injector['cost_p'].isnull().all():
            self.total_injection_cost += self.injector['cost_p'].sum()
        if not self.injector['cost_q'].isnull().all():
            self.total_injection_cost += self.injector['cost_q'].sum()

        # Total losses
        self.dynamic_losses = \
            self.model.calc_dynamic_losses(self._optimizer)
        self.total_losses = self.dynamic_losses
        if not self.model.scenario.converter.empty:
            self.total_losses += self.model.scenario.converter['loss_fix'].sum()

        # Physically valid solution: Do the state variables satisfy the power
        # balance equations up to a sufficient accuracy?
        max_bal_err = self.bus.loc[:, 'bal_err'].abs().max()
        max_inj = np.max([self.model.scenario.bus['load'].abs().max(),
                          self.injector['s'].abs().max()])
        total_bal_err = np.sum(np.abs(self.bus.loc[:, 'bal_err'].real))
        total_load = np.sum(np.abs(self.model.scenario.bus['load'].real))
        if max_bal_err / max_inj <= self._bal_err_nodal_thres and \
                total_bal_err / total_load <= self._bal_err_total_thres:
            self.is_physical = True
        else:
            self.is_physical = False

        # Update the total time with the duration of the OPF result creation
        self.total_time += timer.total()

        _log.debug("OPF result creation (total) ({:.3f} sec.)"
                   .format(timer.total()))

    @property
    def num_buses(self):
        """Return the number of buses."""
        return 0 if self.empty else len(self.bus.index)

    @property
    def num_branches(self):
        """Return the number of branches."""
        return 0 if self.empty else len(self.branch.index)

    @property
    def num_converters(self):
        """Return the number of converters."""
        return 0 if self.empty else len(self.converter.index)

    @property
    def num_injectors(self):
        """Return the number of injectors."""
        return 0 if self.empty else len(self.injector.index)

    @property
    def scenario(self):
        """Return the scenario data of the system model."""
        return self.model.scenario

    def __repr__(self):
        """Return a summary of the OPF result."""
        t = ""
        t += self._get_header()
        if self.empty:
            t += self._get_termination_summary()
        else:
            t += "|> Grid Information " + "-"*58 + "<|\n"
            t += "|" + " "*78 + "|\n"
            t += self._get_grid_summary()
            t += "|" + " "*78 + "|\n"
            t += "|> Results " + "-"*67 + "<|\n"
            t += "|" + " "*78 + "|\n"
            t += self._get_result_summary()
            t += "|" + " "*78 + "|\n"
            t += "|> Solver Information " + "-"*56 + "<|\n"
            t += "|" + " "*78 + "|\n"
            t += self._get_solver_info()
            t += "|" + " "*78 + "|\n"
            t += self._get_pathological_price_profile_info()
            t += "+" + "-"*78 + "+\n"
        return t

    @property
    def details(self):
        """
        Return a formatted string with details of the OPF result.

        The returned string contains a formatted table for all major entity
        types, which is hopefully mostly self-explaining. In the very left or
        right of a column, there may be an indicator:

        +-----------+-------------------------------------------------------+
        | Indicator | Meaning                                               |
        +===========+=======================================================+
        |   ``R``   | Reference bus in the respective subgrid.              |
        +-----------+-------------------------------------------------------+
        |   ``=``   | The bus is a DC bus. If there is no indicator, the    |
        |           | bus is an AC bus.                                     |
        +-----------+-------------------------------------------------------+
        |   ``*``   | A limit on the respective quantity is active.         |
        +-----------+-------------------------------------------------------+
        |   ``>``   | The branch is highly loaded, i.e., the flow is 90% or |
        |           | more of the effective rating.                         |
        +-----------+-------------------------------------------------------+
        |   ``T``   | The branch is a transformer. If there is no           |
        |           | indicator, the branch is a line/cable.                |
        +-----------+-------------------------------------------------------+
        """
        if self.empty:
            return self._get_termination_summary()
        if self.bus.index.max() > 99999 or self.bus.index.min() < -9999:
            raise RuntimeError("This formatted output only supports bus IDs "
                               "comprising 5 characters or less.")
        t = ""
        t += self._get_bus_details()
        t += self._get_branch_details()
        t += self._get_converter_details()
        t += self._get_injector_details()
        return t

    #==========================================================================
    #
    # CAUTION: Below is only some ugly string formatting code.
    #
    #                         You have been warned! ;P
    #
    #==========================================================================

    def _get_header(self):
        scenario = self.scenario
        t = ""
        t += "\n+" + "-"*78 + "+\n"
        t += "| OPTIMAL POWER FLOW {:>57s} |\n"\
            .format("hynet ~ version " + hynet_version)
        t += "|" + " "*78 + "|\n"
        t += "|> Data Source " + "-"*63 + "<|\n"
        t += "|" + " "*78 + "|\n"
        t += "| Grid:       {:<64s} |\n"\
            .format(truncate_with_ellipsis(scenario.grid_name + " ("
                + os.path.basename(scenario.database_uri) + ")", 64))
        t += "| Scenario:   {:<64s} |\n"\
            .format(truncate_with_ellipsis("{0:s} @ {1:s} (id={2:s})"
                                           .format(scenario.name,
                                                   scenario.get_time_string(),
                                                   str(scenario.id)),
                                           64))
        t += "|" + " "*78 + "|\n"
        return t

    def _get_termination_summary(self):
        t = ""
        t += "+" + "-"*78 + "+\n"
        t += "| Solver terminated with status {:<46s} |\n"\
            .format("'" + self.solver_status.name + "'")
        t += "+" + "-"*78 + "+\n"
        return t

    def _get_grid_summary(self):
        bus = self.scenario.bus
        branch = self.scenario.branch
        converter = self.scenario.converter
        injector = self.scenario.injector

        line_bus_type = \
            bus.loc[branch.loc[branch['type'] == BranchType.LINE, 'src'], 'type'].values

        conv_src_bus_type = bus.loc[converter['src'], 'type'].values
        conv_dst_bus_type = bus.loc[converter['dst'], 'type'].values
        conv_b2b_bus_type = conv_src_bus_type[conv_src_bus_type == conv_dst_bus_type]

        num_conventional = sum(x.is_conventional() for x in injector['type'])
        num_renewable = sum(x.is_renewable() for x in injector['type'])
        num_prosumer = sum(x.is_prosumer() for x in injector['type'])
        num_load = sum(x.is_load() for x in injector['type'])
        num_compensation = sum(x.is_compensation() for x in injector['type'])

        p_capacity = sum(x.p_max for x in injector['cap'])
        p_tot_load = bus['load'].real.sum()

        t = ""
        t += "| Topology: {:>9s} |{:7d} AC subgrids|{:6d} DC subgrids|{:5d} islands    |\n"\
            .format("acyclic" if self.scenario.has_acyclic_subgrids() else "meshed",
                    len(self.scenario.get_ac_subgrids()),
                    len(self.scenario.get_dc_subgrids()),
                    len(self.model.islands) - 1)
        t += "| Buses:     {:8d} |{:7d} AC buses   |{:6d} DC buses   |{:5d} with shunt |\n"\
            .format(len(bus.index),
                    (bus['type'] == BusType.AC).sum(),
                    (bus['type'] == BusType.DC).sum(),
                    (bus['y_tld'].abs() > 0).sum())
        t += "| Branches:  {:8d} |{:7d} AC lines   |{:6d} DC lines   |{:5d} transform. |\n"\
            .format(len(branch.index),
                    (line_bus_type == BusType.AC).sum(),
                    (line_bus_type == BusType.DC).sum(),
                    (branch['type'].values == BranchType.TRANSFORMER).sum())
        t += "| Converters:{:8d} |{:7d} AC/DC      |{:6d} AC/AC      |{:5d} DC/DC      |\n"\
            .format(len(converter.index),
                    (conv_src_bus_type != conv_dst_bus_type).sum(),
                    (conv_b2b_bus_type == BusType.AC).sum(),
                    (conv_b2b_bus_type == BusType.DC).sum())
        t += "| Injectors: {:8d} |{:7d} convent.   |{:6d} disp. load |{:5d} compensat. |\n"\
            .format(len(injector.index),
                    num_conventional,
                    num_load,
                    num_compensation)
        t += "|" + " "*21 + "|{:7d} renewable  |{:6d} prosumer   |                 |\n"\
            .format(num_renewable,
                    num_prosumer)
        t += "|" + " "*78 + "|\n"
        t += "| Injection:{:11.1f} MW /{:8.1f} Mvar | Min.: {:9.1f} MW /{:9.1f} Mvar |\n"\
            .format(p_capacity,
                    sum(x.q_max for x in injector['cap']),
                    sum(x.p_min for x in injector['cap']),
                    sum(x.q_min for x in injector['cap']))
        t += "| Total load:{:10.1f} MW /{:8.1f} Mvar | Loading:{:9.2%} of P-capacity    |\n"\
            .format(p_tot_load,
                    bus['load'].imag.sum(),
                    p_tot_load/p_capacity)
        return t

    def _get_result_summary(self):
        converter_p_sum = 0
        converter_q_sum = 0
        if not self.scenario.converter.empty:
            converter_p_sum += self.scenario.converter['loss_fix'].sum()
            converter_p_sum += self.converter['p_src'].sum()
            converter_p_sum += self.converter['p_dst'].sum()
            converter_q_sum += self.converter['q_src'].sum()
            converter_q_sum += self.converter['q_dst'].sum()

        v_abs = np.abs(self.bus['v'])
        v_angle = np.angle(self.bus['v']) * 180/np.pi

        dv_bal_p_min = self.bus['dv_bal_p'].min()
        dv_bal_p_max = self.bus['dv_bal_p'].max()
        dv_bal_q_min = self.bus['dv_bal_q'].min()
        dv_bal_q_max = self.bus['dv_bal_q'].max()

        branch_flow = self.branch[['s_src', 's_dst']].abs().max(axis=1)
        branch_utilization = branch_flow / self.branch['effective_rating']

        idx_dc_line = self.scenario.get_dc_branches()
        idx_ac = self.scenario.get_ac_branches()
        idx_ac_line = idx_ac[
            self.scenario.branch.loc[idx_ac, 'type'] == BranchType.LINE]
        idx_tf = idx_ac[
            self.scenario.branch.loc[idx_ac, 'type'] == BranchType.TRANSFORMER]

        util_dc_line = branch_utilization[idx_dc_line].mean()
        util_ac_line = branch_utilization[idx_ac_line].mean()
        util_tf = branch_utilization[idx_tf].mean()

        t = ""
        t += "| Injection:{:11.1f} MW /{:8.1f} Mvar | Inj. cost:{:17.3f} k$/h   |\n"\
            .format(self.injector['s'].real.sum(),
                    self.injector['s'].imag.sum(),
                    self.total_injection_cost/1e3)
        t += "| Total loss:{:10.1f} MW /{:6.2%} P-load | Shunt loss:{:14.1f} MW       |\n"\
            .format(self.total_losses,
                    self.total_losses/np.sum(self.scenario.bus['load'].real),
                    self.bus['s_shunt'].real.sum())
        t += "| Branch loss:{:9.1f} MW                | Shunt Q-sum:{:13.1f} Mvar     |\n"\
            .format(self.branch['s_src'].real.sum() + self.branch['s_dst'].real.sum(),
                    -self.bus['s_shunt'].imag.sum())
        t += "| Conv. loss:{:10.1f} MW                | Converter Q-sum:{:9.1f} Mvar     |\n"\
            .format(converter_p_sum, converter_q_sum)
        t += "|" + " "*40 + "-+---+-" + " "*31 + "|\n"
        t += "| Voltage mag.:{:10.3f} to{:10.3f} p.u.   | Average branch utilization:    |\n"\
            .format(v_abs.min(), v_abs.max())
        t += "| Voltage angle:{:8.2f}  to{:9.2f} deg.    |  AC lines:    {:<17s}|\n"\
            .format(v_angle.min(), v_angle.max(),
                    "{:9.2%}".format(util_ac_line) if not np.isnan(util_ac_line) else "     -")
        t += "| P-bal. dual:{:>10s}  to{:>9s} $/MWh   |  DC lines:    {:<17s}|\n"\
            .format("{:10.2f}".format(dv_bal_p_min) if not np.isnan(dv_bal_p_min) else "-  ",
                    "{:9.2f}".format(dv_bal_p_max) if not np.isnan(dv_bal_p_max) else "-  ",
                    "{:9.2%}".format(util_dc_line) if not np.isnan(util_dc_line) else "     -")
        t += "| Q-bal. dual:{:>10s}  to{:>9s} $/Mvarh |  Transformers:{:<17s}|\n"\
            .format("{:10.2f}".format(dv_bal_q_min) if not np.isnan(dv_bal_q_min) else "-  ",
                    "{:9.2f}".format(dv_bal_q_max) if not np.isnan(dv_bal_q_max) else "-  ",
                    "{:9.2%}".format(util_tf) if not np.isnan(util_tf) else "     -")
        return t

    def _get_solver_info(self):
        solver_string = str(self.solver)
        if self.solver.param:
            solver_string += ' / '
            solver_string += ', '.join([key + '=' + str(value)
                                        for key, value
                                        in self.solver.param.items()])

        bal_err = self.bus['bal_err'].abs()

        if np.isnan(self.reconstruction_mse):
            rec_mse = "-"
        else:
            rec_mse = "{:9.3e} mean squared error".format(self.reconstruction_mse)
            if self.model.has_hybrid_architecture:
                rec_mse += "  <-  HYBRID ARCHITECTURE"

        t = ""
        t += "| Solver:             {:<56s} |\n"\
            .format(truncate_with_ellipsis(solver_string, 56))
        t += "| Status:             {:<56s} |\n"\
            .format(self.solver_status.name.lower())
        t += "| Time:               {:<56s} |\n"\
            .format('{:.2f} sec. in the solver'.format(self.solver_time)
                    + ('' if np.isnan(self.total_time) else
                       ' / {:.2f} sec. in total'.format(self.total_time)))
        t += "| Objective value:   {:10.3e} $/h"\
            .format(self.optimal_value) + " "*44 + "|\n"
        t += "| Loss penalty:      {:10.3e} $/h {:<42s} |\n"\
            .format(self.dynamic_losses * self.scenario.loss_price,
                    "({:.2f} MW * {:.3f} $/MWh)"\
                        .format(self.dynamic_losses, self.scenario.loss_price))
        t += "| Power balance:      {:9.3e} ({:9.3e}) mean (max.) absolute " \
             "error in MVA".format(bal_err.mean(), bal_err.max()) + "  |\n"
        t += "| Reconstruction:     {:<56s} |\n".format(rec_mse)
        if not self.is_physical:
            t += "|" + " "*78 + "|\n"
            t += "|{:^78s}|\n".format("WARNING: THE POWER BALANCE EQUATION IS VIOLATED!")
        return t

    def _get_pathological_price_profile_info(self):
        t = ""
        if not (self.model.has_hybrid_architecture and
                self.solver_status == SolverStatus.SOLVED and
                self.solver.type != SolverType.QCQP and
                not self.is_physical and
                self.reconstruction_mse >= 1e-8 and
                config.OPF['pathological_price_profile_info']):
            return t
        t += "| This scenario exhibits a pathological price profile. Prominent causes are:   |\n"
        t += "|  (a) Zero marginal cost injectors: This can induce near-zero LMPs for        |\n"
        t += "|      active power. To add loss minimization, see Scenario.loss_price.        |\n"
        t += "|  (b) Shortage of inductive reactive power: This can induce negative LMPs     |\n"
        t += "|      for reactive power. To add compensation, see Scenario.add_compensation. |\n"
        t += "| To analyze the cause of inexactness, see hynet.show_power_balance_error.     |\n"
        t += "| In some cases, Scenario.set_minimum_series_resistance may be supportive.     |\n"
        return t

    def _check_activity(self, value, min_, max_):
        if min_ is None and max_ is not None:
            min_ = np.nan * max_
        elif max_ is None and min_ is not None:
            max_ = np.nan * min_
        tolerance = pd.Series(False, index=max_.index)
        for id_ in tolerance.index:
            val = value.at[id_]
            lb = min_.at[id_]
            ub = max_.at[id_]
            lb_present = ~np.isnan(lb)
            ub_present = ~np.isnan(ub)
            if lb_present and ub_present:
                tol = self._tol_active * (ub - lb) + self._zero_thres
                tolerance.at[id_] = (val <= lb + tol) | (val >= ub - tol)
            elif lb_present:
                tol = abs(self._tol_active * lb) + self._zero_thres
                tolerance.at[id_] = (val <= lb + tol)
            elif ub_present:
                tol = abs(self._tol_active * ub) + self._zero_thres
                tolerance.at[id_] = (val >= ub - tol)
        return tolerance

    def _check_cap_region_box_active(self, value, cap):
        p = pd.Series(value.real, index=value.index)
        p_min = pd.Series([x.p_min for x in cap], index=cap.index)
        p_max = pd.Series([x.p_max for x in cap], index=cap.index)
        p_active = self._check_activity(p, p_min, p_max)

        q = pd.Series(value.imag, index=value.index)
        q_min = pd.Series([x.q_min for x in cap], index=cap.index)
        q_max = pd.Series([x.q_max for x in cap], index=cap.index)
        q_active = self._check_activity(q, q_min, q_max)
        return p_active, q_active

    def _get_bus_details(self):
        t = ""
        t += "\n+" + "-"*78 + "+\n"
        t += "| BUS RESULT" + " "*67 + "|\n"
        t += "+-------+---------------+-------------------+--------------+-------------------+\n"
        t += "|       |    Voltage    |       Load        |    Shunt     |  Dual Variables   |\n"
        t += "|       +-------+-------+---------+---------+------+-------+---------+---------+\n"
        t += "|       |  Mag. | Phase |    P    |    Q    | Loss | Q-Inj.|  P-bal. |  Q-bal. |\n"
        t += "|  ID   |  (pu) | (deg) |   (MW)  |  (Mvar) | (MW) | (Mvar)| ($/MWh) |($/Mvarh)|\n"
        t += "+-------+-------+-------+---------+---------+------+-------+---------+---------+\n"
        t = [t]
        scr_bus = self.scenario.bus
        res_bus = self.bus
        dc_bus = scr_bus['type'] == BusType.DC
        v_abs = res_bus['v'].abs()
        v_abs_active = self._check_activity(v_abs, scr_bus['v_min'], scr_bus['v_max'])
        v_angle = pd.Series(np.angle(res_bus['v']) * 180/np.pi, index=res_bus.index)
        load_p = pd.Series(scr_bus['load'].real, index=scr_bus.index)
        load_q = pd.Series(scr_bus['load'].imag, index=scr_bus.index)
        shunt_p = pd.Series(res_bus['s_shunt'].real, index=res_bus.index)
        shunt_q = pd.Series(res_bus['s_shunt'].imag, index=res_bus.index)
        dv_bal_p = res_bus['dv_bal_p']
        dv_bal_q = res_bus['dv_bal_q']
        for id_ in res_bus.index:
            r = "|"
            r += "R" if scr_bus.at[id_, 'ref'] else " "
            r += "{:5d}".format(id_)
            r += "=" if dc_bus.at[id_] else " "
            r += "|"
            r += "*" if v_abs_active.at[id_] else " "
            r += "{:6.3f}".format(v_abs.at[id_])
            r += "|"
            if dc_bus.at[id_] and np.abs(v_angle.at[id_]) < self._zero_thres:
                r += "   -   "
            else:
                r += "{:7.3f}".format(v_angle.at[id_])
            r += "|"
            if load_p.at[id_] == 0:
                r += "      -  "
            else:
                r += "{:9.2f}".format(load_p.at[id_])
            r += "|"
            if load_q.at[id_] == 0:
                r += "      -  "
            else:
                r += "{:9.2f}".format(load_q.at[id_])
            r += "|"
            if shunt_p.at[id_] == 0:
                r += "  -   "
            else:
                r += "{:6.3f}".format(shunt_p.at[id_])
            r += "|"
            if shunt_q.at[id_] == 0:
                r += "   -   "
            else:
                r += "{:7.3f}".format(-shunt_q.at[id_])
            r += "|"
            if np.isnan(dv_bal_p.at[id_]):
                r += "     -   "
            else:
                r += "{:9.3f}".format(dv_bal_p.at[id_])
            r += "|"
            if np.isnan(dv_bal_q.at[id_]):
                r += "     -   "
            else:
                r += "{:9.3f}".format(dv_bal_q.at[id_])
            r += "|"
            r += "\n"
            t.append(r)
        t = "".join(t)
        t += "+-------+-------+-------+---------+---------+------+-------+---------+---------+\n"
        return t

    def _get_branch_details(self):
        t = ""
        t += "\n+" + "-"*78 + "+\n"
        t += "| BRANCH RESULT" + " "*64 + "|\n"
        t += "+-------+-------------+-------------------+-----------------+--------+---------+\n"
        t += "|       |  Terminals  |    Power Flow     |     Voltage     | Losses | Reconst.|\n"
        t += "|       +------+------+----------+--------+--------+--------+--------+---------+\n"
        t += "|       | Src. | Dst. | |S_src|  | PF_src |  Drop  |Angle D.|  Dyn.  |  Kappa  |\n"
        t += "|  ID   | Bus  | Bus  |  (MVA)   |        |  (%)   | (deg)  |  (MW)  |         |\n"
        t += "+-------+------+------+----------+--------+--------+--------+--------+---------+\n"
        scr_branch = self.scenario.branch
        res_branch = self.branch

        if res_branch.empty:
            t += "| No branches present" + " "*58 + "|\n"
            t += "+" + "-"*78 + "+\n"
            return t

        t = [t]
        transformer = scr_branch['type'] == BranchType.TRANSFORMER
        src = scr_branch['src']
        dst = scr_branch['dst']
        dc_bus = self.scenario.bus['type'] == BusType.DC
        S_src = res_branch['s_src']
        S_dst = res_branch['s_dst']
        I_src_abs = res_branch['i_src'].abs()
        I_dst_abs = res_branch['i_dst'].abs()
        I_max = scr_branch['rating'] / self.scenario.base_mva
        congested = self._check_activity(I_src_abs, None, I_max) \
                  | self._check_activity(I_dst_abs, None, I_max)
        highly_loaded = (I_src_abs >= self._high_loading * I_max)\
                      | (I_dst_abs >= self._high_loading * I_max)
        drop = res_branch['v_drop'] * 100
        drop_active = self._check_activity(drop,
                                           scr_branch['drop_min'],
                                           scr_branch['drop_max'])
        angle_diff = res_branch['angle_diff']
        angle_diff_active = self._check_activity(angle_diff,
                                                 scr_branch['angle_min'],
                                                 scr_branch['angle_max'])
        loss_dyn = pd.Series((S_src + S_dst).real, index=res_branch.index)
        kappa = res_branch['rel_err']
        for id_ in res_branch.index:
            r = "|"
            r += "{:6d}".format(id_)
            r += "T" if transformer.at[id_] else " "
            r += "|"
            r += "{:5d}".format(src.at[id_])
            r += "=" if dc_bus.loc[src.at[id_]] else " "
            r += "|"
            r += "{:5d}".format(dst.at[id_])
            r += "=" if dc_bus.loc[dst.at[id_]] else " "
            r += "|"
            r += "*" if congested.at[id_] else ">" if highly_loaded.at[id_] else " "
            r += "{:9.2f}".format(np.abs(S_src.at[id_]))
            r += "|"
            if np.abs(S_src.at[id_]) < self._zero_thres:
                r += "    -   "
            else:
                r += "{:8.3f}".format(np.real(S_src.at[id_]) / np.abs(S_src.at[id_]))
            r += "|"
            r += "*" if drop_active.at[id_] else " "
            r += "{:7.3f}".format(drop.at[id_])
            r += "|"
            r += "*" if angle_diff_active.at[id_] else " "
            if dc_bus.loc[src.at[id_]] and np.abs(angle_diff.at[id_]) < self._zero_thres:
                r += "   -   "
            else:
                r += "{:7.3f}".format(angle_diff.at[id_])
            r += "|"
            r += "{:8.3f}".format(loss_dyn.at[id_])
            r += "|"
            if np.isnan(kappa.at[id_]):
                r += "     -   "
            else:
                r += "{:9.2e}".format(kappa.at[id_])
            r += "|"
            r += "\n"
            t.append(r)
        t = "".join(t)
        t += "+-------+------+------+----------+--------+--------+--------+--------+---------+\n"
        return t

    def _get_converter_details(self):
        t = ""
        t += "\n+" + "-"*78 + "+\n"
        t += "| CONVERTER RESULT" + " "*61 + "|\n"
        t += "+-------+-------------+---------------------+-----------------+----------------+\n"
        t += "|       |  Terminals  |     Power Flow      |Reactive Pwr Inj.|     Losses     |\n"
        t += "|       +------+------+----------+----------+--------+--------+--------+-------+\n"
        t += "|       | Src. | Dst. |  P_src   |  P_dst   | Q_src  | Q_dst  |  Dyn.  |  Fix  |\n"
        t += "|  ID   | Bus  | Bus  |   (MW)   |   (MW)   | (Mvar) | (Mvar) |  (MW)  |  (MW) |\n"
        t += "+-------+------+------+----------+----------+--------+--------+--------+-------+\n"
        scr_converter = self.scenario.converter
        res_converter = self.converter

        if res_converter.empty:
            t += "| No converters present" + " "*56 + "|\n"
            t += "+" + "-"*78 + "+\n"
            return t

        t = [t]
        src = scr_converter['src']
        dst = scr_converter['dst']
        dc_bus = self.scenario.bus['type'] == BusType.DC

        P_src = res_converter['p_src']
        P_dst = res_converter['p_dst']

        Q_src = res_converter['q_src']
        Q_dst = res_converter['q_dst']

        (P_src_active, _) = \
            self._check_cap_region_box_active(P_src + 1j*Q_src,
                                              scr_converter['cap_src'])
        (P_dst_active, _) = \
            self._check_cap_region_box_active(P_dst + 1j*Q_dst,
                                              scr_converter['cap_dst'])

        loss_dyn = P_src + P_dst
        loss_fix = scr_converter['loss_fix']

        for id_ in res_converter.index:
            r = "|"
            r += "{:6d}".format(id_)
            r += " |"
            r += "{:5d}".format(src.at[id_])
            r += "=" if dc_bus.loc[src.at[id_]] else " "
            r += "|"
            r += "{:5d}".format(dst.at[id_])
            r += "=" if dc_bus.loc[dst.at[id_]] else " "
            r += "|"
            r += "*" if P_src_active.at[id_] else " "
            r += "{:9.2f}".format(P_src.at[id_])
            r += "|"
            r += "*" if P_dst_active.at[id_] else " "
            r += "{:9.2f}".format(P_dst.at[id_])
            r += "|"
            if dc_bus.loc[src.at[id_]] and np.abs(Q_src.at[id_]) < self._zero_thres:
                r += "     -  "
            else:
                r += "{:8.2f}".format(Q_src.at[id_])
            r += "|"
            if dc_bus.loc[dst.at[id_]] and np.abs(Q_dst.at[id_]) < self._zero_thres:
                r += "     -  "
            else:
                r += "{:8.2f}".format(Q_dst.at[id_])
            r += "|"
            r += "{:8.3f}".format(loss_dyn.at[id_])
            r += "|"
            if loss_fix.at[id_] == 0:
                r += "   -   "
            else:
                r += "{:7.3f}".format(loss_fix.at[id_])
            r += "|"
            r += "\n"
            t.append(r)
        t = "".join(t)
        t += "+-------+------+------+----------+----------+--------+--------+--------+-------+\n"
        return t

    def _get_injector_details(self):
        t = ""
        t += "\n+" + "-"*78 + "+\n"
        t += "| INJECTOR RESULT" + " "*62 + "|\n"
        t += "+-------+------+--------------------------+-----------------+------------------+\n"
        t += "|       | Term.|        Injection         |      Cost       |       Type       |\n"
        t += "|       +------+----------+--------+------+--------+--------+                  |\n"
        t += "|       |      |    P     |   Q    |  PF  | for P  | for Q  |                  |\n"
        t += "|  ID   | Bus  |   (MW)   | (Mvar) |      | (k$/h) | (k$/h) |                  |\n"
        t += "+-------+------+----------+--------+------+--------+--------+------------------+\n"
        t = [t]
        scr_injector = self.scenario.injector
        res_injector = self.injector
        terminal = scr_injector['bus']
        dc_bus = self.scenario.bus['type'] == BusType.DC
        S = res_injector['s']
        P = pd.Series(S.real, index=res_injector.index)
        Q = pd.Series(S.imag, index=res_injector.index)
        (P_active, _) = self._check_cap_region_box_active(S, scr_injector['cap'])
        cost_p = res_injector['cost_p']
        cost_q = res_injector['cost_q']
        for id_ in res_injector.index:
            r = "|"
            r += "{:6d}".format(id_)
            r += " |"
            r += "{:5d}".format(terminal.at[id_])
            r += "=" if dc_bus.loc[terminal.at[id_]] else " "
            r += "|"
            r += "*" if P_active.at[id_] else " "
            r += "{:9.2f}".format(P.at[id_])
            r += "|"
            if dc_bus.loc[terminal.at[id_]] and np.abs(Q.at[id_]) < self._zero_thres:
                r += "     -  "
            else:
                r += "{:8.2f}".format(Q.at[id_])
            r += "|"
            if ((dc_bus.loc[terminal.at[id_]] and np.abs(Q.at[id_]) < self._zero_thres)
                    or np.abs(S.at[id_]) < self._zero_thres):
                r += "  -   "
            else:
                r += "{:6.3f}".format(P.at[id_] / np.abs(S.at[id_]))
            r += "|"
            if np.isnan(cost_p.at[id_]):
                r += "    -   "
            else:
                r += "{:8.3f}".format(cost_p.at[id_]/1e3)
            r += "|"
            if np.isnan(cost_q.at[id_]):
                r += "    -   "
            else:
                r += "{:8.3f}".format(cost_q.at[id_]/1e3)
            r += "|"
            r += " {:<16s} ".format(truncate_with_ellipsis(
                                    str(scr_injector.at[id_, 'type']), 16))
            r += "|"
            r += "\n"
            t.append(r)
        t = "".join(t)
        t += "+-------+------+----------+--------+------+--------+--------+------------------+\n"
        return t
