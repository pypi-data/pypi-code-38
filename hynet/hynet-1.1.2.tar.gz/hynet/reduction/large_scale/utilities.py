"""
Utility functions for the network reduction.
"""

import pandas as pd

from hynet.types_ import hynet_id_


def add_parallel_branch_info(scenario):
    """
    Add information about parallel branches to the scenario.

    This function adds/updates the following columns to the branch data frame:

    ``parallel``: (``bool``)
        ``True`` if the branch is parallel to another one and ``False`` otherwise.
    ``parallel_main_id``: (``hynet_id_``)
        Branch ID of the (arbitrarily selected) main branch among the group of
        parallel branches. With this information, groups of parallel branches
        can be determined by filtering this column w.r.t. the main branch ID.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    """
    scenario.branch['parallel'] = False
    scenario.branch['parallel_main_id'] = scenario.branch.index

    for idx_parallel in scenario.get_parallel_branches():
        scenario.branch.loc[idx_parallel, 'parallel'] = True
        scenario.branch.loc[idx_parallel, 'parallel_main_id'] = idx_parallel[0]


def remove_parallel_branch_info(scenario):
    """
    Remove the information about parallel branches.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    """
    if 'parallel' in scenario.branch.columns:
        scenario.branch.drop('parallel', axis='columns', inplace=True)

    if 'parallel_main_id' in scenario.branch.columns:
        scenario.branch.drop('parallel_main_id', axis='columns', inplace=True)


def add_adjacent_bus_info(scenario):
    """
    Add information about adjacent buses to the scenario.

    This function adds/updates the following columns to the bus data frame:

    ``num_adjacent``: (``int``)
        Number of adjacent buses.
    ``adjacent``: (``pandas.Index[hynet_id_]``)
        Pandas index with the bus ID of all adjacent buses.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    """
    scenario.bus['num_adjacent'] = hynet_id_(0)
    scenario.bus['adjacent'] = None

    for bus_id in scenario.bus.index:
        adjacent_buses = set()

        adjacent_buses.update(
            scenario.branch.loc[scenario.branch['src'] == bus_id, 'dst'])

        adjacent_buses.update(
            scenario.branch.loc[scenario.branch['dst'] == bus_id, 'src'])

        scenario.bus.at[bus_id, 'num_adjacent'] = len(adjacent_buses)
        scenario.bus.at[bus_id, 'adjacent'] = pd.Index(adjacent_buses)


def remove_adjacent_bus_info(scenario):
    """
    Remove the information about adjacent buses.

    Parameters
    ----------
    scenario : Scenario
        Scenario that shall be processed.
    """
    if 'num_adjacent' in scenario.bus.columns:
        scenario.bus.drop('num_adjacent', axis='columns', inplace=True)

    if 'adjacent' in scenario.bus.columns:
        scenario.bus.drop('adjacent', axis='columns', inplace=True)
