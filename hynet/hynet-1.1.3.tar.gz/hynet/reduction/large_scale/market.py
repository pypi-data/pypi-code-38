"""
Market-based subgrid selection and reduction.
"""

import logging

import numpy as np
import pandas as pd

from hynet.utilities.base import Timer
from hynet.types_ import SolverStatus

from hynet.reduction.large_scale.features import has_features
from hynet.reduction.large_scale.subgrid import reduce_subgrid
from hynet.reduction.large_scale.utilities import (add_adjacent_bus_info,
                                                   remove_adjacent_bus_info)

_log = logging.getLogger(__name__)


def identify_price_clusters(opf_result, max_price_diff):
    """
    Identify clusters of buses that exhibit a similar nodal price.

    The dual variable of the active power balance constraint is considered as
    the nodal price (i.e., the locational marginal price if the OPF problem
    exhibits strong duality). After the price clusters were identified,
    overlapping clusters are combined, such that a bus of the system may only
    be part of one cluster.

    Parameters
    ----------
    opf_result : OPFResult
        OPF result based on which price clusters shall be identified.
    max_price_diff : float
        Threshold :math:`\delta` in $/MW on fluctuations of the nodal price
        (LMP) from the center of a price cluster to consider the respective
        buses to be part of the cluster.

    Returns
    -------
    clusters : pandas.DataFrame
        Data frame with information on the price clusters, whose index consists
        of the bus ID of the cluster centers and the following columns:

        ``cluster``: (``hynet_int_``)
            Number of cycles in the subgrid.
        ``price_ref``: (``.hynet_float_``)
            Reference price for the cluster. Note that, due to the combining
            of overlapping clusters, the price difference within a cluster
            may exceed the threshold on the price fluctuations.
    """
    timer = Timer()

    scenario = opf_result.scenario
    add_adjacent_bus_info(scenario)
    nodal_price = opf_result.bus['dv_bal_p']

    # Initialize a data frame with the cluster center candidates:
    #  1) Find buses with at least 2 adjacent buses
    #  2) Exclude all buses with features from this set of buses
    #  3) Create a data frame for the cluster candidates:
    #      - Index is the cluster center bus ID
    #      - Column 'cluster' is a set with all buses of the cluster
    #      - Column 'price_ref' is the cluster's reference price
    candidates = scenario.bus.index[scenario.bus['num_adjacent'] >= 2]
    candidates = candidates[[not has_features(scenario, [bus_id])
                             for bus_id in candidates]]
    candidates = pd.DataFrame({'cluster': candidates}, index=candidates)
    candidates = candidates.applymap(lambda x: set([x]))
    candidates['price_ref'] = nodal_price.loc[candidates.index]
    candidates.index.name = 'center'

    clusters = pd.DataFrame(columns=candidates.columns)
    clusters.index.name = candidates.index.name

    while not candidates.empty:
        candidate = candidates.iloc[0]
        cluster = candidate['cluster']
        price_ref = candidate['price_ref']

        adjacent = set(np.concatenate(scenario.bus.loc[cluster, 'adjacent'].values))
        adjacent -= cluster

        # Check the adjacent buses of the cluster if they should join
        num_extensions = 0
        for bus_id in adjacent:
            if abs(nodal_price.at[bus_id] - price_ref) > max_price_diff:
                continue
            if has_features(scenario, list(cluster) + [bus_id]):
                continue
            cluster.add(bus_id)  # This updates ``candidates`` as well...
            num_extensions += 1

        # If this cluster does not expand any more:
        #  1) Add it to the identified clusters (if it's more than one bus)
        #  2) Remove it from the candidate data frame
        if not num_extensions:
            if len(cluster) > 1:
                clusters = clusters.append(candidate, sort=False)
            candidates = candidates.iloc[1:]

    remove_adjacent_bus_info(scenario)

    _log.info("Identification of price clusters ~ "
              "Identified {:d} clusters for combination ({:.3f} sec.)"
              .format(len(clusters.index), timer.interval()))

    clusters = combine_overlapping_clusters(clusters)

    _log.info("Identification of price clusters ~ "
              "Combination yielded {:d} clusters ({:.3f} sec.)"
              .format(len(clusters.index), timer.interval()))

    return clusters


def combine_overlapping_clusters(candidates):
    """Combine any overlapping clusters to a single cluster."""
    clusters = pd.DataFrame(columns=candidates.columns)
    clusters.index.name = candidates.index.name

    while not candidates.empty:
        # Pop the last candidate
        candidate = candidates.iloc[-1]
        candidates = candidates.iloc[0:-1]

        cluster = candidate['cluster']

        # Check the intersection of this cluster with the others
        was_combined = False
        for center in candidates.index:
            if cluster.intersection(candidates.at[center, 'cluster']):
                candidates.at[center, 'cluster'].update(cluster)
                was_combined = True
                continue

        # If there was no overlap, add it to the final cluster data frame
        if not was_combined:
            clusters = clusters.append(candidate, sort=False)

    return clusters


def reduce_by_market(scenario, opf_result, max_price_diff):
    """
    Apply a market-based network reduction to the scenario.

    This function performs the marked-based network reduction described in
    Section IV-D in [1]_.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    opf_result : OPFResult
        OPF result of the provided scenario.
    max_price_diff : float
        Threshold :math:`\delta` in $/MW on fluctuations of the nodal price
        (LMP) from the center of a price cluster to consider the respective
        buses to be part of the cluster (cf. equation (4) in [1]_).

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

    if opf_result.solver_status != SolverStatus.SOLVED:
        raise ValueError("The provided OPF result contains no valid solution.")

    _log.info("Market-based network reduction ~ Starting (delta = {:.3f})"
              .format(max_price_diff))

    clusters = identify_price_clusters(opf_result, max_price_diff)

    for center in clusters.index:
        reduce_subgrid(scenario,
                       representative_bus=center,
                       subgrid=clusters.at[center, 'cluster'] - set([center]))

    _log.info("Market-based network reduction ~ "
              "Reduced {:d} buses ({:.3f} sec.)"
              .format(num_buses_before - scenario.num_buses, timer.total()))

    return num_buses_before - scenario.num_buses
