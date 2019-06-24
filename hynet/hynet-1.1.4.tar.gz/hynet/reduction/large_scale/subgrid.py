"""
Subgrid reduction: Aggregate the buses of a subgrid to the representative bus.
"""

import re

import numpy as np
import pandas as pd

from hynet.types_ import hynet_id_

from hynet.reduction.large_scale.features import (has_bus_features,
                                                  has_branch_features)

"""
Retain the line charging during reduction: If ``True``, the shunt admittances
(line charging) of the branches within the subgrid that are reduced are moved
to the representative bus as shunt compensation (to more accurately model the
reactive power demand).
"""
RETAIN_LINE_CHARGING = True


def reduce_subgrid(scenario, representative_bus, subgrid):
    """
    Reduce the subgrid buses to the representative bus, if it contains no features.

    If the subgrid *does not contain any features*, it is reduced to the
    representative bus as described in Section IV-A in [1]_. In case of the
    latter, a column ``aggregation`` is added/updated in the bus data frame
    that contains a list with the bus ID of all buses that were aggregated to
    the respective bus.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    representative_bus : .hynet_id_
        Bus ID of the representative bus.
    subgrid : Iterable[.hynet_id_]
        Iterable with the bus IDs of the subgrid that shall be aggregated at
        the representative bus. It *must not* contain the representative bus.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    subgrid = list(set(subgrid))  # Create a list of unique bus IDs

    if representative_bus in subgrid:
        raise ValueError("The representative bus must be specified separately "
                         "from the subgrid's other buses.")

    # Check for features: The representative bus may be a feature, as it
    # remains part of the reduced model. All other buses of the subgrid as well
    # as the branches that are removed during reduction must not be a feature.
    if has_bus_features(scenario, subgrid):
        return
    if has_branch_features(scenario, subgrid + [representative_bus]):
        return

    if (scenario.branch['src'] == scenario.branch['dst']).any():
        # We require that the scenario does not contain any self-loops...
        raise ValueError("The scenario contains self-loops.")

    # Add the 'aggregation' column if it was not yet created
    if 'aggregation' not in scenario.bus.columns:
        scenario.bus['aggregation'] = None
        for bus in scenario.bus.index:
            scenario.bus.at[bus, 'aggregation'] = []

    # REMARK: It is necessary to copy the list of aggregated buses, as the deep
    # copying of scenarios (e.g. as required for the initial coupling-based
    # reduction to determine critical injector features) does not deep copy the
    # list objects and, thus, they would be linked across the different
    # scenario objects.
    aggregation = list(scenario.bus.at[representative_bus, 'aggregation'])

    for bus in subgrid:
        # If applicable, inherit the reference to the representative bus
        scenario.bus.at[representative_bus, 'ref'] |= scenario.bus.at[bus, 'ref']

        # Set the terminal bus of all injectors to the representative bus
        scenario.injector.loc[
            scenario.injector['bus'] == bus, 'bus'] = representative_bus

        # Move the load and shunt compensation to the representative bus
        scenario.bus.at[representative_bus, 'load'] += \
            scenario.bus.at[bus, 'load']
        scenario.bus.at[representative_bus, 'y_tld'] += \
            scenario.bus.at[bus, 'y_tld']

        # Update the branch and converter source and destination buses
        # (This can introduce self-loops, which are resolved below)
        scenario.branch.loc[
            scenario.branch['src'] == bus, 'src'] = representative_bus
        scenario.branch.loc[
            scenario.branch['dst'] == bus, 'dst'] = representative_bus

        scenario.converter.loc[
            scenario.converter['src'] == bus, 'src'] = representative_bus
        scenario.converter.loc[
            scenario.converter['dst'] == bus, 'dst'] = representative_bus

        # Inherit the aggregated buses to the representative bus
        aggregation += scenario.bus.at[bus, 'aggregation']

    scenario.remove_buses(subgrid)

    # Update the 'aggregation' column with the newly aggregated buses
    scenario.bus.at[representative_bus, 'aggregation'] = aggregation + subgrid

    # Remove the branches that connected buses within the subgrid
    idx_self_loop = \
        scenario.branch.index[scenario.branch['src'] == scenario.branch['dst']]
    if RETAIN_LINE_CHARGING:
        # If desired, retain the line charging as shunts at the representative bus
        scenario.bus.at[representative_bus, 'y_tld'] += \
            scenario.branch.loc[idx_self_loop, ['y_src', 'y_dst']].sum().sum()
    scenario.branch.drop(idx_self_loop, inplace=True)

    # Remove the converters that connected buses within the subgrid
    idx_self_loop = \
        scenario.converter.index[scenario.converter['src'] == scenario.converter['dst']]
    scenario.converter.drop(idx_self_loop, inplace=True)


def create_bus_id_map(scenario):
    """
    Create a mapping from the original buses to the reduced buses.

    During the network reduction, certain buses are aggregated at other buses.
    This function creates a mapping from the buses of the original system to
    the buses of the reduced system.

    Parameters
    ----------
    scenario : Scenario
        Scenario that was subject to network reduction.

    Returns
    -------
    bus_id_map : pandas.Series
        This series is *indexed* by the bus IDs *before* network reduction,
        while the *values* are the bus IDs *after* network reduction, i.e.,
        it maps the buses of the original system to the buses in the reduced
        system.
    """
    if 'aggregation' not in scenario.bus.columns:
        return pd.Series(data=scenario.bus.index.values,
                         name='bus_id_post',
                         index=scenario.bus.index.copy(name='bus_id_pre',
                                                       dtype=hynet_id_))

    bus_id_pre = np.concatenate([scenario.bus.index.values,
                                 *scenario.bus['aggregation'].values])

    bus_id_pre, counts = np.unique(bus_id_pre, return_counts=True)
    if np.any(counts != 1):
        raise RuntimeError("Some buses were aggregated to multiple buses.")

    bus_id_map = pd.Series(data=np.zeros(len(bus_id_pre), dtype=hynet_id_),
                           name='bus_id_post',
                           index=pd.Index(bus_id_pre,
                                          name='bus_id_pre',
                                          dtype=hynet_id_))

    # Buses that are still present: 1:1 mapping
    bus_id_map.loc[scenario.bus.index] = scenario.bus.index

    # Buses that were aggregated
    for bus_id_post in scenario.bus.index:
        bus_id_map.loc[scenario.bus.at[bus_id_post, 'aggregation']] = bus_id_post

    return bus_id_map


def preserve_aggregation_info(scenario):
    """
    Copy the information on aggregated buses to the bus annotation.

    During the network reduction, certain buses are aggregated at other buses,
    where the aggregated buses are documented in the column ``aggregation``.
    As this is an extension to *hynet*'s scenario format, it is not stored to
    the grid database upon saving. To this end, this information is preserved
    using the bus annotation.

    Parameters
    ----------
    scenario : Scenario
        Scenario that was subject to network reduction.
    """
    if 'aggregation' not in scenario.bus.columns:
        return

    for bus in scenario.bus.index:
        aggregation = scenario.bus.at[bus, 'aggregation']
        if not aggregation:
            continue
        aggregation = "aggregates " + str(aggregation)

        annotation = scenario.bus.at[bus, 'annotation']
        if annotation:
            scenario.bus.at[bus, 'annotation'] = annotation + ", " + aggregation
        else:
            scenario.bus.at[bus, 'annotation'] = aggregation


def restore_aggregation_info(scenario):
    """
    Restore the information on aggregated buses from the bus annotation.

    Parameters
    ----------
    scenario : Scenario
        Scenario that was subject to network reduction.

    See Also
    --------
    hynet.reduction.large_scale.subgrid.preserve_aggregation_info
    """
    if 'aggregation' in scenario.bus.columns:
        raise ValueError("The scenario already contains aggregation information.")

    scenario.bus['aggregation'] = None

    for bus in scenario.bus.index:
        aggregation = re.findall(r"aggregates \[([0-9, ]*)\]",
                                 scenario.bus.at[bus, 'annotation'])

        if not aggregation:
            scenario.bus.at[bus, 'aggregation'] = []
            continue

        if len(aggregation) > 1:
            raise ValueError("Some bus annotations contain more than one "
                             "bus aggregation specification.")

        scenario.bus.at[bus, 'aggregation'] = \
            list(map(hynet_id_, aggregation[0].split(',')))
