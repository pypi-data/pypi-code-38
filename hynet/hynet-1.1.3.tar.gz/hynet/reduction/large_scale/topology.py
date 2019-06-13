"""
Topology-based subgrid selection and reduction.
"""

import logging

import numpy as np

import hynet
from hynet.utilities.base import Timer

from hynet.reduction.large_scale.subgrid import reduce_subgrid
from hynet.reduction.large_scale.utilities import (add_parallel_branch_info,
                                                   remove_parallel_branch_info,
                                                   add_adjacent_bus_info,
                                                   remove_adjacent_bus_info)

_log = logging.getLogger(__name__)


def reduce_single_buses(scenario):
    """
    Reduce single buses within the scenario.

    This function reduces buses that only exhibit one adjacent bus, see
    Section IV-B in [1]_. This function may be called repeatedly to reduce
    "lines of buses" as considered in [1]_.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.

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

    add_adjacent_bus_info(scenario)
    single_buses = scenario.bus.index[scenario.bus['num_adjacent'] == 1]
    remove_adjacent_bus_info(scenario)

    for bus_id in single_buses:
        adjacent = np.union1d(
            scenario.branch.loc[scenario.branch['dst'] == bus_id, 'src'].values,
            scenario.branch.loc[scenario.branch['src'] == bus_id, 'dst'].values
        )

        if not adjacent.size:
            # There was a subgrid comprising only two buses, where one of them
            # was already reduced. We skip the second one...
            continue
        elif adjacent.size != 1:
            raise RuntimeError("The candidate's adjacent bus is not unique.")

        reduce_subgrid(scenario, representative_bus=adjacent[0], subgrid=[bus_id])

    _log.info("Reduction of single buses ~ Reduced {:d} buses ({:.3f} sec.)"
              .format(num_buses_before - scenario.num_buses, timer.total()))

    return num_buses_before - scenario.num_buses


def identify_islands(scenario, max_island_size):
    """
    Identify "islands" at the boundary of the grid.

    In the context of the topology-based network reduction, "islands" are
    clusters of buses that are connected to the main grid via a single
    corridor. This function identifies these "islands" by testing every
    corridor, i.e., the branches in the corridor are removed, islanding of
    a subgrid is detected and, if its size does not exceed the defined
    maximum island size, it is considered an "island".

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be examined.
    max_island_size : int
        Maximum size of an "island" in terms of its number of buses.

    Returns
    -------
    island_info : list[tuple(.hynet_id_, pandas.Index[.hynet_id_])]
        Information on the "islands" within the system. The returned list
        contains an item for every island, which is a tuple comprising the
        island's representative bus (i.e., the bus of the main grid to which
        the island is connected) and a pandas index with the bus ID of all
        buses of the island.
    """
    timer = Timer()
    island_info = []

    if max_island_size < 1:
        return island_info

    _log.info("Identification of islands ~ Starting (max. 'island' size {:d})"
              .format(max_island_size))

    if len(scenario.get_islands()) != 1:
        raise ValueError("This function only supports connected grids.")

    add_parallel_branch_info(scenario)

    for branch_id in scenario.branch.index:
        branch = scenario.branch.loc[branch_id]

        # Identify the branches in this corridor
        if branch['parallel']:
            if branch['parallel_main_id'] != branch_id:
                continue
            remove_ids = scenario.branch.index[
                scenario.branch['parallel_main_id'] == branch_id]
        else:
            remove_ids = branch_id

        # Remove all branches in the corridor, identify the islands, and
        # restore the original data
        branch_bkp = scenario.branch
        scenario.branch = scenario.branch.drop(remove_ids, axis='index')
        islands = scenario.get_islands()
        scenario.branch = branch_bkp

        # Identify the smaller island check if it qualifies for reduction
        if len(islands) == 1:
            continue
        elif len(islands) != 2:
            raise RuntimeError("Unexpected program state.")

        if len(islands[0]) < len(islands[1]):
            island = islands[0]
        else:
            island = islands[1]

        if island.size > max_island_size:
            continue

        # Identify the representative bus and initiate the reduction
        if branch['src'] in island:
            representative_bus = branch['dst']
        elif branch['dst'] in island:
            representative_bus = branch['src']
        else:
            raise RuntimeError("Unexpected program state.")

        island_info.append((representative_bus, island))

    remove_parallel_branch_info(scenario)

    _log.info("Identification of islands ~ Identified {:d} islands ({:.3f} sec.)"
              .format(len(island_info), timer.total()))

    return island_info


def reduce_islands(scenario, max_island_size):
    """
    Reduce "islands" within the scenario.

    This function reduces "islands" at the boundary of the grid, see
    Section IV-B in [1]_.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    max_island_size : int
        Maximum size of an "island" in terms of its number of buses.

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

    island_info = identify_islands(scenario, max_island_size)
    if not island_info:
        _log.info("Reduction of islands ~ No islands are present ({:.3f} sec.)"
                  .format(timer.total()))
        return 0
    idx_sort = \
        np.argsort([len(island) for representative_bus, island in island_info])
    island_info = np.array(island_info, dtype=object)[idx_sort[::-1]]

    for representative_bus, island in island_info:
        was_removed = ~island.isin(scenario.bus.index)
        if np.all(was_removed):
            # We already reduced a larger island that contained this one...
            continue
        if np.any(was_removed):
            # Due to the sorting, a subgrid must be a subset of a larger one...
            raise RuntimeError("Unexpected program state.")
        reduce_subgrid(scenario, representative_bus, subgrid=island)

    _log.info("Reduction of islands ~ Reduced {:d} buses ({:.3f} sec.)"
              .format(num_buses_before - scenario.num_buses, timer.total()))

    return num_buses_before - scenario.num_buses


def reduce_by_topology(scenario, max_island_size=None):
    """
    Apply a topology-based network reduction to the scenario.

    This function performs the topology-based network reduction described in
    Section IV-B in [1]_.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    max_island_size : int, optional
        Maximum size of an "island" in terms of its number of buses. By
        default, it is set to approximately 1% of the total number of buses.
        Set this parameter to ``0`` to disable the reduction of "islands".

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

    if max_island_size is None:
        max_island_size = int(np.ceil(0.01 * scenario.num_buses))

    _log.info("Topology-based network reduction ~ Starting (max. 'island' "
              "size {:d})".format(max_island_size))

    while reduce_single_buses(scenario) > 0:
        pass

    if max_island_size is None or max_island_size > 0:
        reduce_islands(scenario, max_island_size)

    _log.info("Topology-based network reduction ~ "
              "Reduced {:d} buses ({:.3f} sec.)"
              .format(num_buses_before - scenario.num_buses, timer.total()))

    return num_buses_before - scenario.num_buses
