"""
Electrical coupling-based subgrid selection and reduction.
"""

import logging

import numpy as np
import pandas as pd

from hynet.types_ import SolverStatus
from hynet.utilities.base import Timer

from hynet.reduction.large_scale.subgrid import reduce_subgrid
from hynet.reduction.large_scale.features import has_bus_features

_log = logging.getLogger(__name__)


def reduce_by_coupling(scenario, rel_impedance_thres=0.05):
    """
    Apply an electrical coupling-based network reduction to the scenario.

    This function performs the electrical coupling-based network reduction
    described in Section IV-C in [1]_.

    Parameters
    ----------
    scenario : hynet.Scenario
        Scenario that shall be processed.
    rel_impedance_thres : float, optional
        Relative threshold :math:`\\tau` w.r.t. the maximum series impedance
        modulus that defines a strong coupling of buses (see equation (3)
        in [1]_). Default is ``0.05`` (5%).

    Returns
    -------
    int
        Number of buses that were reduced.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    timer = Timer()
    num_buses_before = scenario.num_buses

    _log.info("Electrical coupling-based network reduction ~ Starting "
              "(tau = {:.1%})".format(rel_impedance_thres))

    # Compute the series resistance in Ohms
    v_base = pd.Series(
        scenario.bus.loc[scenario.branch['src'].values, 'base_kv'].values,
        index=scenario.branch.index)
    z_base = (v_base ** 2) / scenario.base_mva
    z_bar = scenario.branch['z_bar'] * z_base

    # For the parallel branches, compute the equivalent series resistance
    for parallel_branches in scenario.get_parallel_branches():
        z_bar.loc[parallel_branches[0]] = \
            1 / np.sum(1 / z_bar.loc[parallel_branches].values)
        z_bar.drop(parallel_branches[1:], inplace=True)

    # Consider the modulus and filter according to the relative threshold
    z_bar_abs = z_bar.abs()
    z_bar_abs = z_bar_abs[z_bar_abs <= rel_impedance_thres * z_bar_abs.max()]

    # Reduce these branches
    for branch_id in z_bar_abs.index:
        if branch_id not in scenario.branch.index:
            # A branch may have already been removed by preceding reductions
            # (Example: In a loop of 3 candidate branches, the first removal
            #  renders the other two parallel and the third branch is removed
            #  alongside the second one.)
            continue

        # Choose one adjacent bus as the representative bus: The reduced bus
        # must not be a feature, so let's try our best to avoid it...
        representative_bus = scenario.branch.at[branch_id, 'src']
        subgrid_bus = scenario.branch.at[branch_id, 'dst']
        if has_bus_features(scenario, [subgrid_bus]):
            representative_bus, subgrid_bus = subgrid_bus, representative_bus

        reduce_subgrid(scenario,
                       representative_bus=representative_bus,
                       subgrid=[subgrid_bus])

    _log.info("Electrical coupling-based network reduction ~ "
              "Reduced {:d} buses ({:.3f} sec.)"
              .format(num_buses_before - scenario.num_buses, timer.total()))

    return num_buses_before - scenario.num_buses


def get_critical_injector_features(opf_reference, opf_reduction, feature_depth,
                                   critical_mw_diff=None):
    """
    Determine bus features to mitigate the reduction error at critical injectors.

    It has been observed that the majority of the dispatch error induced by the
    electrical coupling-based reduction is often due to a comparably small
    number of injectors. This effect may be mitigated by declaring the buses
    in the vicinity of critical injectors as features, see also Section V-A
    in [1]_. This function identifies these buses and returns their IDs.

    Parameters
    ----------
    opf_reference : OPFResult
        OPF result of the scenario *before* the reduction.
    opf_reduction : OPFResult
        OPF result of the scenario *after* the reduction.
    feature_depth : int
        Depth :math:`\\vartheta` for which buses in the vicinity of a critical
        injector are declared as features, i.e., these buses can be reached
        from the terminal bus of a critical injector by traversing a maximum
        of :math:`\\vartheta` branches.
    critical_mw_diff : float, optional
        Absolute threshold in MW on the active power dispatch difference of an
        injector to consider it as critical. The default is 0.02% of the
        total active power load.

    Returns
    -------
    critical_buses : numpy.ndarray[.hynet_id_]
        Array of bus IDs that should be marked as a feature.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    scenario = opf_reference.scenario

    if opf_reference.solver_status != SolverStatus.SOLVED or \
            opf_reduction.solver_status != SolverStatus.SOLVED:
        raise ValueError("The feature identification requires successfully "
                         "solved OPFs.")

    if critical_mw_diff is None:
        critical_mw_diff = 0.0002 * scenario.bus['load'].sum().real

    # Identify the critical injectors
    dispatch_ref = pd.Series(opf_reference.injector['s'].real,
                             index=opf_reference.injector.index)
    dispatch_red = pd.Series(opf_reduction.injector['s'].real,
                             index=opf_reduction.injector.index)

    if not dispatch_red.index.equals(dispatch_ref.index):
        raise ValueError("The injectors of the two systems do not match.")

    dispatch_diff = (dispatch_ref - dispatch_red).abs()
    critical_injectors = dispatch_diff.index[dispatch_diff >= critical_mw_diff]

    # Identify the corresponding terminal buses
    critical_buses = scenario.injector.loc[critical_injectors, 'bus'].values
    critical_buses = np.unique(critical_buses)

    _log.info("Identified {:d} buses with critical injectors."
              .format(critical_buses.size))

    # Identify the associated buses that should be considered as features
    iteration = 0
    while iteration < feature_depth:
        adjacent_src = \
            scenario.branch.loc[scenario.branch['dst'].isin(critical_buses), 'src']
        adjacent_dst = \
            scenario.branch.loc[scenario.branch['src'].isin(critical_buses), 'dst']

        critical_buses = np.unique(np.concatenate([critical_buses,
                                                   adjacent_src.values,
                                                   adjacent_dst.values]))
        iteration += 1

    _log.info("Identified {:d} buses within depth {:d} of critical injectors."
              .format(critical_buses.size, feature_depth))

    return critical_buses
