"""
Parameter sweeps to assist the selection of an appropriate network reduction.
"""

import logging

import numpy as np
import pandas as pd

from hynet.utilities.base import Timer
from hynet.distributed.server import start_optimization_server

from hynet.reduction.large_scale.features import (add_feature_columns,
                                                  add_standard_features)
from hynet.reduction.large_scale.coupling import (reduce_by_coupling,
                                                  get_critical_injector_features)
from hynet.reduction.large_scale.market import reduce_by_market
from hynet.reduction.large_scale.evaluation import (evaluate_reduction,
                                                    show_reduction_evaluation)

_log = logging.getLogger(__name__)


def sweep_rel_impedance_thres(scenario, values=None, server=None, solver=None,
                              opf_reference=None, show_evaluation=True):
    """
    Sweep the relative impedance threshold :math:`\tau`.

    The electrical coupling-based network reduction is parameterized by the
    relative impedance threshold :math:`\tau`, cf. Section IV-C and (3) in
    [1]_. To assist the selection of an appropriate threshold, this function
    provides the evaluation of the electrical coupling-based network reduction
    for different threshold values (cf. Fig. 4 in [1]_).

    If the ``feature`` columns are not present upon the call of this function,
    the standard features described in Section III in [1]_ are considered.

    Parameters
    ----------
    scenario : hynet.Scenario
        Scenario that shall be evaluated.
    values : list[float], optional
        List of (ascending) values for the relative impedance threshold
        :math:`\\tau`. By default, the 15 values in the interval [0.005, 0.1]
        shown in Fig. 4 in [1]_ are considered.
    server : OptimizationServer, optional
        *hynet* optimization server for the computation of the OPFs. By
        default, a server in local mode is used.
    solver : SolverInterface, optional
        Solver for the OPF problems. The default selects the most appropriate
        solver among those installed.
    opf_reference : OPFResult, optional
        OPF result of the scenario *before* the reduction to evaluate the
        reduction accuracy. By default, an OPF for the provided scenario is
        utilized.
    show_evaluation : bool, optional
        If ``True`` (default), the results of the sweep are visualized.

    Returns
    -------
    evaluation : pandas.DataFrame
        Data frame with information on the extent and accuracy of the reduction
        for the individual threshold values. This data frame is indexed by the
        threshold and comprises the following columns:

        ``bus_reduction``: (``hynet_float_``)
            Ratio of the number of reduced buses w.r.t. the total number of
            buses before the reduction.
        ``branch_reduction``: (``hynet_float_``)
            Ratio of the number of reduced branches w.r.t. the total number of
            branches before the reduction.
        ``cycle_reduction``: (``hynet_float_``)
            Ratio of the number of reduced cycles w.r.t. the total number of
            cycles before the reduction.
        ``error_disp``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power dispatch error
            as defined in equation (1) in [1]_.
        ``error_disp_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power dispatch
            error.
        ``error_flow``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power branch flow
            error as defined in equation (2) in [1]_.
        ``error_flow_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power branch flow
            error.
        ``opf``: (``hynet.OPFResult``)
            OPF result for the respective scenario.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    timer = Timer()

    if values is None:
        values = list(np.around(np.concatenate([np.linspace(0.005, 0.05, 10),
                                                np.linspace(0.06, 0.1, 5)]),
                                decimals=3))
    if not values or np.any(np.array(values) <= 0):
        raise ValueError("Please provide one or more positive sweep values.")

    _log.info("Sweep of the relative impedance threshold ~ Starting")

    if server is None:
        server = start_optimization_server(local=True)

    # Calculate the reference OPF
    scenario = scenario.copy()
    opf_before_reduction = server.calc_jobs([scenario],
                                            solver=solver,
                                            show_progress=False)[0]
    if opf_reference is None:
        opf_reference = opf_before_reduction
    evaluation = evaluate_reduction(opf_reference, opf_before_reduction, name=0.0)
    evaluation = pd.DataFrame().append(evaluation)
    evaluation.loc[0.0, 'opf'] = opf_before_reduction
    evaluation.index.name = r'Threshold $\tau$'

    if add_feature_columns(scenario):
        add_standard_features(scenario, opf_before_reduction)

    reductions = []
    for rel_impedance_thres in values:
        reductions.append(scenario.copy())
        reduce_by_coupling(reductions[-1], rel_impedance_thres)

    opf_results = server.calc_jobs(reductions, solver=solver)

    for i, result in enumerate(opf_results):
        try:
            evaluation = evaluation.append(evaluate_reduction(opf_reference,
                                                              result,
                                                              name=values[i]),
                                           sort=False)
            evaluation.loc[values[i], 'opf'] = result
        except ValueError as exception:
            _log.error("Tau = {:.1%} failed: ".format(values[i]) + str(exception))

    _log.info("Sweep of the relative impedance threshold ~ "
              "Evaluated {:d} values ({:.3f} sec.)"
              .format(len(values), timer.total()))

    evaluation.name = ("Sweep of the relative impedance threshold for '" +
                       scenario.grid_name + "'")

    if show_evaluation:
        show_reduction_evaluation(evaluation)

    return evaluation


def sweep_feature_depth(scenario, rel_impedance_thres, values=None,
                        critical_mw_diff=None, server=None, solver=None,
                        opf_reference=None, show_evaluation=True):
    """
    Sweep the feature depth :math:`\\vartheta`

    After and initial electrical coupling-based network reduction, additional
    bus features may be added to reduce the dispatch error at critical
    injectors, which is parameterized by the feature depth :math:`\\vartheta`,
    cf. Section V-A and Fig. 5 in [1]_. To assist the selection of an
    appropriate depth, this function provides the evaluation of the two-stage
    electrical coupling-based network reduction for different feature depths.

    If the ``feature`` columns are not present upon the call of this function,
    the standard features described in Section III in [1]_ are considered.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be evaluated.
    rel_impedance_thres : float, optional
        Relative threshold :math:`\\tau` for the electrical coupling-based
        network reduction.
    values : list[int], optional
        List of (ascending) values for the feature depth :math:`\\vartheta`. By
        default, the depths 0 to 10 are considered.
    critical_mw_diff : float, optional
        Absolute threshold in MW on the active power dispatch difference of an
        injector to consider it as critical. The default is 0.02% of the
        total active power load.
    server : OptimizationServer, optional
        *hynet* optimization server for the computation of the OPFs. By
        default, a server in local mode is used.
    solver : SolverInterface, optional
        Solver for the OPF problems. The default selects the most appropriate
        solver among those installed.
    opf_reference : OPFResult, optional
        OPF result of the scenario *before* the reduction to evaluate the
        reduction accuracy. By default, an OPF for the provided scenario is
        utilized.
    show_evaluation : bool, optional
        If ``True`` (default), the results of the sweep are visualized.

    Returns
    -------
    evaluation : pandas.DataFrame
        Data frame with information on the extent and accuracy of the reduction
        for the individual feature depths. This data frame is indexed by the
        depth and comprises the following columns:

        ``bus_reduction``: (``hynet_float_``)
            Ratio of the number of reduced buses w.r.t. the total number of
            buses before the reduction.
        ``branch_reduction``: (``hynet_float_``)
            Ratio of the number of reduced branches w.r.t. the total number of
            branches before the reduction.
        ``cycle_reduction``: (``hynet_float_``)
            Ratio of the number of reduced cycles w.r.t. the total number of
            cycles before the reduction.
        ``error_disp``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power dispatch error
            as defined in equation (1) in [1]_.
        ``error_disp_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power dispatch
            error.
        ``error_flow``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power branch flow
            error as defined in equation (2) in [1]_.
        ``error_flow_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power branch flow
            error.
        ``opf``: (``hynet.OPFResult``)
            OPF result for the respective scenario.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    timer = Timer()

    if values is None:
        values = list(range(11))
    if not values or np.any(np.array(values) < 0):
        raise ValueError("Please provide one or more nonnegative sweep values.")

    _log.info("Sweep of the feature depth ~ Starting")

    if server is None:
        server = start_optimization_server(local=True)

    # Calculate the reference OPF
    scenario = scenario.copy()
    opf_before_reduction = server.calc_jobs([scenario],
                                            solver=solver,
                                            show_progress=False)[0]
    if opf_reference is None:
        opf_reference = opf_before_reduction
    evaluation = pd.DataFrame()
    evaluation.index.name = r'Depth $\vartheta$'

    if add_feature_columns(scenario):
        add_standard_features(scenario, opf_before_reduction)

    # Perform an initial reduction to identify "critical injectors"
    reduction = scenario.copy()
    reduce_by_coupling(reduction, rel_impedance_thres)
    opf_reduction = server.calc_jobs([reduction],
                                     solver=solver,
                                     show_progress=False)[0]

    reductions = []
    for feature_depth in values:
        reductions.append(scenario.copy())

        # Determine additional bus features based on the critical injectors
        critical_buses = get_critical_injector_features(
            opf_reference=opf_before_reduction,
            opf_reduction=opf_reduction,
            feature_depth=feature_depth,
            critical_mw_diff=critical_mw_diff)
        reductions[-1].bus.loc[critical_buses, 'feature'] = True

        # Perform the reduction considering the additional features
        reduce_by_coupling(reductions[-1], rel_impedance_thres)

    opf_results = server.calc_jobs(reductions, solver=solver)

    for i, result in enumerate(opf_results):
        try:
            evaluation = evaluation.append(evaluate_reduction(opf_reference,
                                                              result,
                                                              name=values[i]),
                                           sort=False)
            evaluation.loc[values[i], 'opf'] = result
        except ValueError as exception:
            _log.error("Depth {:d} failed: ".format(values[i]) + str(exception))

    _log.info("Sweep of the feature depth ~ "
              "Evaluated {:d} values ({:.3f} sec.)"
              .format(len(values), timer.total()))

    evaluation.name = ("Sweep of the feature depth for '" +
                       scenario.grid_name + "'")

    if show_evaluation:
        show_reduction_evaluation(evaluation)

    return evaluation


def sweep_max_price_diff(scenario, values, server=None, solver=None,
                         opf_reference=None, show_evaluation=True):
    """
    Sweep the maximum nodal price fluctuation :math:`\delta` for clustering.

    The market-based network reduction is parameterized by the threshold
    :math:`\delta` in $/MW on fluctuations of the nodal price (LMP) from the
    center of a price cluster, cf. Section IV-D and (4) in [1]_. To assist the
    selection of an appropriate threshold, this function provides the
    evaluation of the market-based network reduction for different threshold
    values (cf. Fig. 6 in [1]_).

    If the ``feature`` columns are not present upon the call of this function,
    the standard features described in Section III in [1]_ are considered.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be evaluated.
    values : list[float]
        List of (ascending) values for the threshold :math:`\delta` in $/MW on
        fluctuations of the nodal price. To identify a reasonable range for
        the threshold values, it may be helpful to calculate an OPF and
        inspect the LMP profile via ``hynet.show_lmp_profile``.
    server : OptimizationServer, optional
        *hynet* optimization server for the computation of the OPFs. By
        default, a server in local mode is used.
    solver : SolverInterface, optional
        Solver for the OPF problems. The default selects the most appropriate
        solver among those installed.
    opf_reference : OPFResult, optional
        OPF result of the scenario *before* the reduction to evaluate the
        reduction accuracy. By default, an OPF for the provided scenario is
        utilized.
    show_evaluation : bool, optional
        If ``True`` (default), the results of the sweep are visualized.

    Returns
    -------
    evaluation : pandas.DataFrame
        Data frame with information on the extent and accuracy of the reduction
        for the individual threshold values. This data frame is indexed by the
        threshold and comprises the following columns:

        ``bus_reduction``: (``hynet_float_``)
            Ratio of the number of reduced buses w.r.t. the total number of
            buses before the reduction.
        ``branch_reduction``: (``hynet_float_``)
            Ratio of the number of reduced branches w.r.t. the total number of
            branches before the reduction.
        ``cycle_reduction``: (``hynet_float_``)
            Ratio of the number of reduced cycles w.r.t. the total number of
            cycles before the reduction.
        ``error_disp``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power dispatch error
            as defined in equation (1) in [1]_.
        ``error_disp_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power dispatch
            error.
        ``error_flow``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power branch flow
            error as defined in equation (2) in [1]_.
        ``error_flow_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power branch flow
            error.
        ``opf``: (``hynet.OPFResult``)
            OPF result for the respective scenario.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    timer = Timer()

    if not values or np.any(np.array(values) <= 0):
        raise ValueError("Please provide one or more positive sweep values.")

    _log.info("Sweep of the price fluctuation threshold ~ Starting")

    if server is None:
        server = start_optimization_server(local=True)

    # Calculate the reference OPF
    scenario = scenario.copy()
    opf_before_reduction = server.calc_jobs([scenario],
                                            solver=solver,
                                            show_progress=False)[0]
    if opf_reference is None:
        opf_reference = opf_before_reduction
    evaluation = evaluate_reduction(opf_reference, opf_before_reduction, name=0.0)
    evaluation = pd.DataFrame().append(evaluation)
    evaluation.loc[0.0, 'opf'] = opf_before_reduction
    evaluation.index.name = r'Threshold $\delta$'

    if add_feature_columns(scenario):
        add_standard_features(scenario, opf_before_reduction)

    reductions = []
    for max_price_diff in values:
        reductions.append(scenario.copy())
        reduce_by_market(reductions[-1], opf_before_reduction, max_price_diff)

    opf_results = server.calc_jobs(reductions, solver=solver)

    for i, result in enumerate(opf_results):
        try:
            evaluation = evaluation.append(evaluate_reduction(opf_reference,
                                                              result,
                                                              name=values[i]),
                                           sort=False)
            evaluation.loc[values[i], 'opf'] = result
        except ValueError as exception:
            _log.error("Delta = {:.3f} failed: ".format(values[i]) + str(exception))

    _log.info("Sweep of the price fluctuation threshold ~ "
              "Evaluated {:d} values ({:.3f} sec.)"
              .format(len(values), timer.total()))

    evaluation.name = ("Sweep of the price fluctuation threshold for '" +
                       scenario.grid_name + "'")

    if show_evaluation:
        show_reduction_evaluation(evaluation)

    return evaluation
