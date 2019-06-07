"""
Combined network reduction strategy.
"""

import logging

import pandas as pd

from hynet.opf.calc import calc_opf
from hynet.utilities.base import Timer

from hynet.reduction.large_scale.features import (add_feature_columns,
                                                  add_standard_features)
from hynet.reduction.large_scale.topology import reduce_by_topology
from hynet.reduction.large_scale.coupling import (reduce_by_coupling,
                                                  get_critical_injector_features)
from hynet.reduction.large_scale.market import reduce_by_market
from hynet.reduction.large_scale.evaluation import (evaluate_reduction,
                                                    show_reduction_evaluation)
from hynet.reduction.large_scale.subgrid import (create_bus_id_map,
                                                 preserve_aggregation_info)

_log = logging.getLogger(__name__)


def reduce_system(scenario, solver=None, max_island_size=None,
                  rel_impedance_thres=0.05, feature_depth=5,
                  critical_mw_diff=None, max_price_diff=0.0,
                  show_evaluation=False, return_bus_id_map=False,
                  preserve_aggregation=False):
    """
    Apply a feature- and structure-preserving network reduction.

    This function applies the feature- and structure-preserving network
    reduction described in [1]_ to the scenario. It comprises a topology-based,
    electrical coupling-based, and market-based reduction stage, which
    identifies and aggregates appropriate subgrids that do not contain any
    features and exhibit a minor impact on the overall behavior of the system.
    Features are defined by a Boolean-valued column ``feature`` of the bus
    and branch data frame of the scenario. If these columns are not present
    upon the call of this function, the standard features described in
    Section III in [1]_ are added.

    Depending on the parameterization, this function performs an extensive
    model analysis and several OPF computations, due to which its execution may
    take quite some time. To track the progress, the logging of info messages
    may be activated via

    >>> import logging
    >>> logging.basicConfig(level=logging.INFO)

    With a corresponding parameterization, the individual reduction stages
    can be activated or deactivated in this combined reduction strategy.
    However, in case the need arises, the individual reduction stages as well
    as their evaluation may also be performed "manually" to customize the
    reduction process, please refer to the "See Also" section for directions
    to the respective modules.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    solver : SolverInterface, optional
        Solver for the OPF problems. The default selects the most appropriate
        solver among those installed.
    max_island_size : int, optional
        Maximum size of an "island" in terms of its number of buses. By
        default, it is set to approximately 1% of the total number of buses.
        Set this parameter to ``0`` to disable the reduction of "islands",
        i.e., only single buses and lines of buses are reduced, or to ``-1`` to
        disable the entire topology-based reduction, i.e., the reduction of
        single buses, lines of buses, and "islands".
    rel_impedance_thres : float, optional
        Relative threshold :math:`\\tau` w.r.t. the maximum series impedance
        modulus that defines a strong coupling of buses (see equation (3)
        in [1]_). Default is ``0.05`` (5%). Set this parameter to ``0`` to
        disable the electrical coupling-based reduction.
    feature_depth : int, optional
        Depth :math:`\\vartheta` for which buses in the vicinity of a critical
        injector are declared as features, i.e., these buses can be reached
        from the terminal bus of a critical injector by traversing a maximum
        of :math:`\\vartheta` branches. Default is ``5``. Set this parameter to
        ``0`` to disable the feature refinement.
    critical_mw_diff : float, optional
        Absolute threshold in MW on the active power dispatch difference of an
        injector to consider it as critical. The default is 0.02% of the
        total active power load.
    max_price_diff : float, optional
        Threshold :math:`\\delta` in $/MW on fluctuations of the nodal price
        (LMP) from the center of a price cluster to consider the respective
        buses to be part of the cluster (cf. equation (4) in [1]_). Set this
        parameter to ``0`` to disable the marked-based reduction.
    show_evaluation : bool, optional
        If ``True`` (default is ``False``), the evaluation of the individual
        reduction stages is visualized.
    return_bus_id_map : bool, optional
        If ``True`` (default is ``False``), a mapping from the buses of the
        original system to the buses of the reduced system is returned.
    preserve_aggregation : bool, optional
        If ``True`` (default is ``False``), the information on aggregated buses
        in the column ``aggregation`` of the bus data frame is copied to the
        bus annotation to preserve it when storing the reduced system to a grid
        database. After loading from the grid database, the column can be
        restored via ``restore_aggregation_info``.

    Returns
    -------
    evaluation : pandas.DataFrame
        Data frame with information on the extent and accuracy of the reduction
        in the individual reduction stages. This data frame is indexed by the
        name of the reduction stage, with the original system named ``''``,
        and comprises the following columns:

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

    bus_id_map : pandas.Series
        Only returned if ``return_bus_id_map`` is ``True``. This series is
        *indexed* by the bus IDs *before* network reduction, while the *values*
        are the bus IDs *after* network reduction, i.e., it maps the buses of
        the original system to the buses in the reduced system.

    See Also
    --------
    hynet.reduction.large_scale.features:
        Specification of features.
    hynet.reduction.large_scale.topology:
        Topology-based network reduction.
    hynet.reduction.large_scale.coupling:
        Electrical coupling-based network reduction.
    hynet.reduction.large_scale.market:
        Market-based network reduction.
    hynet.reduction.large_scale.evaluation:
        Evaluation of the extent and accuracy of a reduction.
    hynet.reduction.large_scale.sweep:
        Parameter sweeps to support the configuration process.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    timer = Timer()

    _log.info("Feature- and structure-preserving network reduction ~ Starting")

    # Calculate the reference OPF
    opf_reference = calc_opf(scenario.copy(), solver=solver)
    evaluation = evaluate_reduction(opf_reference, opf_reference, name='')
    evaluation = pd.DataFrame().append(evaluation)
    evaluation.loc['', 'opf'] = opf_reference

    def append_evaluation(scenario, name):
        """
        Append the evaluation of a reduction to the evaluation data frame.
        """
        nonlocal evaluation, opf_reference, solver
        result = calc_opf(scenario.copy(), solver=solver)
        evaluation = evaluation.append(
            evaluate_reduction(opf_reference, result, name=name), sort=False)
        evaluation.loc[name, 'opf'] = result

    if add_feature_columns(scenario):
        # If there were no features yet, add the standard features
        add_standard_features(scenario, opf_reference)

    # 1) Perform topology-based reduction
    if max_island_size is None or max_island_size >= 0:
        reduce_by_topology(scenario, max_island_size)
        append_evaluation(scenario, name='Topology')

    # 2) Perform electrical coupling-based reduction
    if rel_impedance_thres > 0:
        if feature_depth < 1:
            reduce_by_coupling(scenario, rel_impedance_thres)
            append_evaluation(scenario, name='Coupling')
        else:
            # Perform an initial reduction to identify "critical injectors"
            reduction = scenario.copy()
            reduce_by_coupling(reduction, rel_impedance_thres)
            append_evaluation(reduction, name='Coupling I')

            # Determine additional bus features based on the critical injectors
            critical_buses = get_critical_injector_features(
                opf_reference=evaluation['opf'].iloc[-2],
                opf_reduction=evaluation['opf'].iloc[-1],
                feature_depth=feature_depth,
                critical_mw_diff=critical_mw_diff)
            scenario.bus.loc[critical_buses, 'feature'] = True

            # Perform the reduction considering the additional features
            reduce_by_coupling(scenario, rel_impedance_thres)
            append_evaluation(scenario, name='Coupling II')

    # 3) Perform market-based reduction
    if max_price_diff > 0:
        reduce_by_market(scenario, evaluation['opf'].iloc[-1], max_price_diff)
        append_evaluation(scenario, name='Market')

    _log.info("Feature- and structure-preserving network reduction ~ "
              "Reduced {:.1%} buses ({:.3f} sec.)"
              .format(evaluation['bus_reduction'].iloc[-1], timer.total()))

    evaluation.name = "Reduction of '" + scenario.grid_name + "'"

    if preserve_aggregation:
        preserve_aggregation_info(scenario)

    if show_evaluation:
        show_reduction_evaluation(evaluation)

    if return_bus_id_map:
        return evaluation, create_bus_id_map(scenario)
    else:
        return evaluation
