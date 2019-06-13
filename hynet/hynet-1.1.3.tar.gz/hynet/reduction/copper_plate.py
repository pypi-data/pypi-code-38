"""
Network reduction to a "copper plate".
"""

import logging
import copy

import numpy as np

from hynet.types_ import BusType
from hynet.utilities.base import Timer
from hynet.scenario.representation import Scenario
from hynet.scenario.capability import CapRegion

_log = logging.getLogger(__name__)


def reduce_to_copper_plate(scenario):
    """
    Return a deep copy of the scenario with the grid reduced to a copper plate.

    In the "copper plate" reduction, every connected grid is reduced to a
    single bus, i.e., the impact of the power grid is neglected and the network
    laws are reduced to simply balance the total injection and total load.
    """
    timer = Timer()
    cpr = Scenario()
    cpr.id = scenario.id
    cpr.name = scenario.name
    cpr.time = scenario.time
    cpr.database_uri = scenario.database_uri
    cpr.grid_name = "COPPER PLATE REDUCTION"
    cpr.base_mva = scenario.base_mva
    cpr.bus = copy.deepcopy(scenario.bus)
    cpr.injector = copy.deepcopy(scenario.injector)

    for island in scenario.get_islands():
        # Define the supplementary bus to which this island is reduced
        ref_bus = island[0]

        # Accumulate all active load at the supplementary bus
        cpr.bus.at[ref_bus, 'load'] = cpr.bus.loc[island, 'load'].real.sum()

        # Eliminate all other buses of the island and init. the supp. bus
        cpr.bus.drop(island[1:], axis='index', inplace=True)
        cpr.bus.at[ref_bus, 'type'] = BusType.DC
        cpr.bus.at[ref_bus, 'ref'] = True
        cpr.bus.at[ref_bus, 'base_kv'] = np.nan
        cpr.bus.at[ref_bus, 'y_tld'] = 0
        cpr.bus.at[ref_bus, 'v_min'] = 1.0
        cpr.bus.at[ref_bus, 'v_max'] = 1.0
        cpr.bus.at[ref_bus, 'annotation'] = ''

        # Connect all injectors of this island to the supplementary bus,
        # eliminate reactive power capability, and deep copy if necessary
        index = cpr.injector.index[cpr.injector['bus'].isin(island)]
        cpr.injector.loc[index, 'bus'] = ref_bus
        for id_ in index:
            cap = cpr.injector.at[id_, 'cap']
            cpr.injector.at[id_, 'cap'] = CapRegion([cap.p_min, cap.p_max])
            cpr.injector.at[id_, 'cost_p'] = \
                copy.deepcopy(cpr.injector.at[id_, 'cost_p'])
            cpr.injector.at[id_, 'cost_q'] = None

    _log.debug("Copper plate reduction ({:.3f} sec.)".format(timer.total()))
    return cpr
