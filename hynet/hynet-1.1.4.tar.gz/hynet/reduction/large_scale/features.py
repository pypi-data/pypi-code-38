"""
Declaration of features for the network reduction.
"""

import logging

import numpy as np
import pandas as pd

from hynet.types_ import InjectorType, BranchType, SolverStatus

_log = logging.getLogger(__name__)


def add_feature_columns(scenario):
    """
    Ensure that the provided scenario contains the feature columns.

    For the network reduction, buses and branches of particular interest can be
    marked as features of the system to prevent their reduction. This function
    adds the respective columns to the data frames of the scenario, in case
    that they do no exist already.

    Parameters
    ----------
    scenario : Scenario
        Scenario that should contain the feature columns.

    Returns
    -------
    bool
        ``False`` if one or more feature columns already existed (i.e., feature
        information is present) and ``True`` otherwise.
    """
    bus_features_missing = 'feature' not in scenario.bus.columns
    branch_features_missing = 'feature' not in scenario.branch.columns

    if bus_features_missing:
        scenario.bus['feature'] = False
    if branch_features_missing:
        scenario.branch['feature'] = False

    return bus_features_missing and branch_features_missing


def add_bus_features(scenario):
    """
    Add the standard bus-related features.

    The terminal buses of conventional generators as well as all reference
    buses are marked as features.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    """
    add_feature_columns(scenario)

    terminals = scenario.injector.loc[
            scenario.injector['type'] == InjectorType.CONVENTIONAL, 'bus'].values
    scenario.bus.loc[terminals, 'feature'] = True

    scenario.bus.loc[scenario.bus['ref'], 'feature'] = True


def add_converter_features(scenario):
    """
    Add the standard converter-related features.

    The terminal buses of converters are marked as features.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    """
    add_feature_columns(scenario)

    scenario.bus.loc[scenario.converter['src'].values, 'feature'] = True
    scenario.bus.loc[scenario.converter['dst'].values, 'feature'] = True


def add_branch_features(scenario, length_threshold):
    """
    Add the standard branch-related features.

    The transformers as well as long branches are marked as features.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    length_threshold : float
        Threshold in kilometers on the length of a branch to consider it as
        long.
    """
    add_feature_columns(scenario)

    transformer = scenario.branch['type'] == BranchType.TRANSFORMER
    scenario.branch.loc[transformer, 'feature'] = True

    long_branch = scenario.branch['length'] >= length_threshold
    scenario.branch.loc[long_branch, 'feature'] = True


def add_congestion_features(scenario, result, loading_threshold, dv_threshold):
    """
    Add the standard congestion-related features.

    Branches that are highly loaded or that exhibit binding constraints are
    marked as features.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    result: OPFResult
        OPF result of the scenario.
    loading_threshold: float
        Relative threshold on the branch flow w.r.t. its effective rating
        to consider it as highly loaded.
    dv_threshold : float
        Threshold on the dual variables of the ampacity and angle difference
        constraint.
    """
    add_feature_columns(scenario)

    if result.solver_status != SolverStatus.SOLVED:
        raise ValueError("A successfully solved OPF is expected.")

    mva_flow = np.maximum(result.branch['s_src'].abs().values,
                          result.branch['s_dst'].abs().values)
    mva_rating = result.branch['effective_rating'].values
    loading = pd.Series(np.true_divide(mva_flow, mva_rating),
                        index=result.branch.index)
    scenario.branch.loc[loading >= loading_threshold, 'feature'] = True

    for column in ['dv_i_max_src', 'dv_i_max_dst',
                   'dv_angle_min', 'dv_angle_max',
                   'dv_drop_min', 'dv_drop_max']:
        if column in result.branch.columns:
            scenario.branch.loc[
                result.branch[column] >= dv_threshold, 'feature'] = True


def add_standard_features(scenario, result, length_threshold=50,
                          loading_threshold=0.8, dv_threshold=1.0):
    """
    Add the standard features for feature-preserving network reduction.

    The feature-preserving network reduction permits the preservation of
    certain entities of particular importance. This function marks the entities
    described in Section III in [1]_ as features, i.e., it adds the standard
    bus-, branch-, converter- and injector-related features to the scenario.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    result: OPFResult
        OPF result of the scenario.
    length_threshold : float, optional
        Threshold in kilometers on the length of a branch to consider it as
        long (default is 50km).
    loading_threshold: float, optional
        Relative threshold on the branch flow w.r.t. its effective rating
        to consider it as highly loaded (default is 0.8, i.e., 80% utilization).
    dv_threshold : float, optional
        Threshold on the dual variables of the ampacity and angle difference
        constraint (default is 1.0).

    See Also
    --------
    hynet.reduction.large_scale.features.add_feature_columns:
        Add the feature columns to the scenario.
    hynet.reduction.large_scale.features.add_bus_features:
        Add the standard bus-related features.
    hynet.reduction.large_scale.features.add_converter_features:
        Add the standard converter-related features.
    hynet.reduction.large_scale.features.add_branch_features:
        Add the standard branch-related features.
    hynet.reduction.large_scale.features.add_congestion_features:
        Add the standard congestion-related features.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    add_feature_columns(scenario)
    num_features_before = count_features(scenario)

    add_bus_features(scenario)
    add_converter_features(scenario)
    add_branch_features(scenario, length_threshold)
    add_congestion_features(scenario, result, loading_threshold, dv_threshold)

    _log.info("Network reduction ~ Added {:d} features"
              .format(count_features(scenario) - num_features_before))


def count_features(scenario):
    """
    Return the number of features of the scenario.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.

    Returns
    -------
    int
        The number of bus and branch features.
    """
    add_feature_columns(scenario)
    return np.count_nonzero(scenario.bus['feature']) \
        + np.count_nonzero(scenario.branch['feature'])


def has_bus_features(scenario, subgrid):
    """
    Return ``True`` if the subgrid contains any bus features.

    Parameters
    ----------
    scenario : Scenario
        Scenario that contains the subgrid.
    subgrid : list[.hynet_id_]
        List with the bus IDs of the subgrid.

    Returns
    -------
    bool
        ``True`` if the subgrid contains any bus features and ``False``
        otherwise.
    """
    add_feature_columns(scenario)
    return scenario.bus.loc[subgrid, 'feature'].any()


def has_branch_features(scenario, subgrid):
    """
    Return ``True`` if the subgrid contains any branch features.

    Parameters
    ----------
    scenario : Scenario
        Scenario that contains the subgrid.
    subgrid : list[.hynet_id_]
        List with the bus IDs of the subgrid.

    Returns
    -------
    bool
        ``True`` if the subgrid contains any branch features and ``False``
        otherwise.
    """
    add_feature_columns(scenario)

    idx_branch = scenario.branch['src'].isin(subgrid) \
               & scenario.branch['dst'].isin(subgrid)

    return scenario.branch.loc[idx_branch, 'feature'].any()


def has_features(scenario, subgrid):
    """
    Return ``True`` if the subgrid contains any bus or branch features.

    Parameters
    ----------
    scenario : Scenario
        Scenario that contains the subgrid.
    subgrid : list[.hynet_id_]
        List with the bus IDs of the subgrid.

    Returns
    -------
    bool
        ``True`` if the subgrid contains any bus or branch features and
        ``False`` otherwise.
    """
    return (has_bus_features(scenario, subgrid) or
            has_branch_features(scenario, subgrid))
