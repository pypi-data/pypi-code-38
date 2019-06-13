"""
Verification of a steady-state scenario.
"""

import logging

import numpy as np
import pandas as pd

from hynet.types_ import hynet_eps, BusType, BranchType
from hynet.utilities.base import Timer
from hynet.utilities.graph import get_graph_components

_log = logging.getLogger(__name__)


def verify_hybrid_architecture(scr):
    """
    Return ``True`` if the scenario features the *hybrid architecture*.

    This function is actually part of the ``Scenario`` class. Due to its extent,
    it was moved to a separate module in order to improve code readability.
    """

    # Topological requirements
    if not scr.has_acyclic_subgrids():
        return False

    # Prepare for checking the remaining requirements
    requirements_satisfied = True
    warning_exactness = \
        " This can be detrimental to the exactness of the relaxation."

    e_src = scr.e_src

    z_bar = scr.branch['z_bar']
    y_src = scr.branch['y_src']
    y_dst = scr.branch['y_dst']

    rho = pd.Series(np.multiply(scr.branch['rho_src'].values.conj(),
                                scr.branch['rho_dst'].values),
                    index=scr.branch.index)
    rho_angle = pd.Series(np.angle(rho.values) * 180/np.pi,
                          index=scr.branch.index)

    angle_min = scr.branch['angle_min']
    angle_max = scr.branch['angle_max']

    # Electrical requirements

    if np.any(z_bar.values.real <= 0):
        requirements_satisfied = False
        _log.info("The series resistance of some branches is zero or "
                  "negative." + warning_exactness)

    if np.any(z_bar.values.imag < 0):
        requirements_satisfied = False
        _log.info("The series reactance of some branches is capacitive."
                  + warning_exactness)

    if np.any(y_src.values.real < 0) or np.any(y_dst.values.real < 0):
        requirements_satisfied = False
        _log.info("The shunt conductance of some branches is negative."
                  + warning_exactness)

    if np.any(np.multiply(y_src.abs(), z_bar.abs()) > 1) or \
            np.any(np.multiply(y_dst.abs(), z_bar.abs()) > 1):
        requirements_satisfied = False
        _log.info("Some branches are not properly insulated."
                  + warning_exactness)

    for parallel_branches in scr._get_parallel_branch_indices():
        idx = e_src.values[parallel_branches] == e_src.values[parallel_branches[0]]
        rho_diff = np.concatenate((rho.values[parallel_branches[idx]],
                                   rho.values[parallel_branches[~idx]].conj()))
        rho_diff -= rho.values[parallel_branches[0]]
        if np.any(np.abs(rho_diff) > hynet_eps):
            requirements_satisfied = False
            _log.info("In the group "
                      + str(list(scr.branch.index[parallel_branches]))
                      + " of parallel branches the total voltage "
                        "ratios do not agree." + warning_exactness)

    # Constraint requirements

    if np.any(angle_min > -rho_angle) or np.any(angle_max < -rho_angle):
        requirements_satisfied = False
        _log.info("Some angle difference constraints do not enclose "
                  "the negated total phase shift." + warning_exactness)

    return requirements_satisfied


def verify_scenario(scr):
    """
    Verify the integrity and validity of the scenario.

    This function is actually part of the ``Scenario`` class. Due to its extent,
    it was moved to a separate module in order to improve code readability.

    Raises
    ------
    ValueError
        In case any kind of integrity or validity violation is detected.
    """
    timer = Timer()
    e_src = scr.e_src
    e_dst = scr.e_dst

    z_bar = scr.branch['z_bar']
    y_src = scr.branch['y_src']
    y_dst = scr.branch['y_dst']

    rho_src = scr.branch['rho_src']
    rho_dst = scr.branch['rho_dst']
    rho = pd.Series(np.multiply(rho_src.values.conj(), rho_dst.values),
                    index=scr.branch.index)
    rho_angle = pd.Series(np.angle(rho.values) * 180/np.pi,
                          index=scr.branch.index)

    base_kv = scr.bus['base_kv']

    angle_min = scr.branch['angle_min']
    angle_max = scr.branch['angle_max']

    if scr.base_mva <= 0:
        raise ValueError("The MVA base is invalid (positive number expected).")

    if scr.loss_price < 0:
        raise ValueError("The loss price is invalid (nonnegative number expected).")

    # Topological checks

    if scr.num_buses < 1:
        raise ValueError("The grid does not comprise any buses.")

    if scr.num_injectors < 1:
        raise ValueError("There is no injector connected to the grid.")

    if not (np.all(np.isin(scr.branch['src'], scr.bus.index)) and
            np.all(np.isin(scr.branch['dst'], scr.bus.index))):
        raise ValueError("Some branches connect to non-existing buses.")

    if not (np.all(np.isin(scr.converter['src'], scr.bus.index)) and
            np.all(np.isin(scr.converter['dst'], scr.bus.index))):
        raise ValueError("Some converters connect to non-existing buses.")

    if not np.all(np.isin(scr.injector['bus'], scr.bus.index)):
        raise ValueError("Some injectors connect to non-existing buses.")

    if np.any(np.equal(scr.branch['src'], scr.branch['dst'])):
        raise ValueError("The grid contains branch-based self-loops.")

    if np.any(np.logical_and(np.not_equal(base_kv.iloc[e_src],
                                          base_kv.iloc[e_dst]),
                             scr.branch['type'] != BranchType.TRANSFORMER)):
        raise ValueError("Some non-transformer branches connect buses "
                         "with a different base voltage.")

    if np.any(np.equal(scr.converter['src'], scr.converter['dst'])):
        raise ValueError("The grid contains converter-based self-loops.")

    for subgrid in get_graph_components(np.arange(scr.num_buses),
                                        (e_src.values, e_dst.values)):
        subgrid = np.sort(subgrid)
        num_ref = np.count_nonzero(scr.bus['ref'].iloc[subgrid])
        if num_ref > 1:
            _log.warning("Ambiguous references detected. Bus IDs: "
                         + str(list(scr.bus.iloc[subgrid].query('ref').index)))
        bus_type = scr.bus['type'].iloc[subgrid]
        is_ac = np.all(bus_type == BusType.AC)
        is_dc = np.all(bus_type == BusType.DC)
        if not (is_ac or is_dc):
            raise ValueError("Inconsistent bus types in the subgrid comprising "
                             "the buses " + str(list(scr.bus.index[subgrid])))
        if is_ac and num_ref < 1:
            # We only require AC subgrids to have a reference bus
            raise ValueError("Reference is missing in the AC subgrid comprising "
                             "the buses " + str(list(scr.bus.index[subgrid])))

    if not scr.has_acyclic_dc_subgrids():
        raise ValueError("The grid contains meshed DC subgrids. hynet only "
                         "supports radial DC subgrids.")

    # Electrical checks

    if np.any(z_bar.values.real < 0):
        _log.warning("The series resistance of some branches is negative.")

    if np.any(z_bar.abs() < 1e-6):
        _log.warning("Some branches are close to an electrical short. "
                     "This leads to a bad conditioning of the OPF problem "
                     "and may cause numerical and/or convergence issues.")

    if np.any(y_src.values.real < 0) or np.any(y_dst.values.real < 0):
        raise ValueError("The shunt conductance of some branches is negative.")

    if np.any(rho.abs() == 0):
        raise ValueError("Some branches exhibit a total voltage ratio of zero.")

    if np.any(rho_angle.abs() > 90):
        raise ValueError("Some branches exhibit a total phase ratio of "
                         "more than 90 degrees.")

    if np.any(scr.converter[['loss_fwd', 'loss_bwd']] < 0) or \
            np.any(scr.converter[['loss_fwd', 'loss_bwd']] >= 100):
        raise ValueError("Some converter loss factors are not within [0,100).")

    if np.any(scr.converter[['loss_fwd', 'loss_bwd']] == 0):
        _log.warning("Some converters are lossless. Due to modeling with "
                     "a forward and backward flow, this leads to "
                     "an ambiguity in the optimal converter state, which "
                     "may be detrimental to solver convergence.")

    # Electrical checks: Restrictions for DC grids

    dc_bus = scr.bus.loc[scr.bus['type'] == BusType.DC]

    if np.any(dc_bus['y_tld'] != 0):
        raise ValueError("Some bus shunts in the DC subgrids are nonzero.")

    if np.any(dc_bus['load'].imag != 0):
        raise ValueError("Some loads in the DC subgrids demand reactive power.")

    dc_branch = scr.branch.loc[
        scr.bus.loc[scr.branch['src'], 'type'].values == BusType.DC]

    if np.any(dc_branch['rho_src'] != 1) or np.any(dc_branch['rho_dst'] != 1):
        raise ValueError("Some transformers of the DC branches are non-unity.")

    if np.any(dc_branch['y_src'] != 0) or np.any(dc_branch['y_dst'] != 0):
        raise ValueError("Some shunt admittances of the DC branches are nonzero.")

    if np.any(dc_branch['z_bar'].real <= 0):
        raise ValueError("Some DC branches are lossless or active.")

    if np.any(dc_branch['z_bar'].imag != 0):
        raise ValueError("Some series impedances of the DC branches "
                         "exhibit a nonzero reactance.")

    if np.any(~np.isnan(dc_branch['angle_min'])) or \
            np.any(~np.isnan(dc_branch['angle_max'])):
        _log.warning("Some DC branches include angle difference limits.")

    # if np.any(~np.isnan(dc_branch['drop_min'])) or \
    #         np.any(~np.isnan(dc_branch['drop_max'])):
    #     _log.warning("Some DC branches include voltage drop limits.")

    dc_converter_src = scr.converter.loc[
        scr.bus.loc[scr.converter['src'], 'type'].values == BusType.DC]
    dc_converter_dst = scr.converter.loc[
        scr.bus.loc[scr.converter['dst'], 'type'].values == BusType.DC]
    for id_, cap in zip(np.concatenate((dc_converter_src.index,
                                        dc_converter_dst.index)),
                        np.concatenate((dc_converter_src['cap_src'].values,
                                        dc_converter_dst['cap_dst'].values))):
        if cap.q_max != 0 or cap.q_min != 0:
            raise ValueError(("Converter {0} offers reactive power on the "
                              "DC side.").format(id_))

    dc_injector = scr.injector.loc[
        scr.bus.loc[scr.injector['bus'], 'type'].values == BusType.DC]
    for id_, cap in zip(dc_injector.index, dc_injector['cap'].values):
        if cap.q_max != 0 or cap.q_min != 0:
            raise ValueError(("Injector {0} offers reactive power to a "
                              "DC subgrid.").format(id_))

    # Constraint checks

    if not (np.all(scr.bus['v_min'] > 0) and
            np.all(scr.bus['v_max'] >= scr.bus['v_min'])):
        raise ValueError("Some voltage limits are infeasible, zero, or missing.")

    if np.any(scr.branch['rating'] <= 0):
        raise ValueError("Some branch ratings are infeasible or zero.")

    if np.any(angle_min < -89) or np.any(angle_max > 89) or \
            np.any(angle_min >= angle_max):
        raise ValueError("Some angle difference limits are infeasible, "
                         "equal, or not within [-89, 89] degrees")

    if np.any(scr.branch['drop_min'] < -100) or \
            np.any(scr.branch['drop_max'] <= scr.branch['drop_min']):
        raise ValueError("Some voltage drop limits are infeasible, "
                         "equal, or not within [-100, +inf).")

    for n, cap in enumerate(np.concatenate((scr.converter['cap_src'].values,
                                            scr.converter['cap_dst'].values,
                                            scr.injector['cap'].values))):
        # Note that only the box constraint needs to be checked, proper
        # specification of the half-spaces is ensured in CapRegion
        if not (cap.p_max >= cap.p_min and cap.q_max >= cap.q_min):
            raise ValueError(("Some {0:s} capability regions are infeasible "
                              "or incompletely specified.").format(
                             'converter'
                             if n < 2*scr.num_converters else 'injector'))
        if cap.has_polyhedron():
            if cap.p_max == cap.p_min and cap.q_max == cap.q_min != 0:
                _log.warning("Singleton capability regions with nonzero "
                             "reactive power and polyhedral constraints are "
                             "present. This potentially causes infeasibility.")
            elif not cap.q_min <= 0 <= cap.q_max:
                _log.info("Capability regions with polyhedral constraints "
                          "are present, where the reactive power limits "
                          "do not include zero. This is not recommended, "
                          "as the specification becomes intricate to "
                          "understand (and, consequently, error-prone).")

    for island in scr.get_islands():
        injectors = scr.injector.loc[scr.injector['bus'].isin(island)]
        if injectors.empty:
            raise ValueError("There's no injector connected to the island "
                             "comprising the buses " + str(list(island)))
        # A simple plausibility check of sufficient injection/load
        # (This can be helpful, e.g., in the simulation of contingencies,
        # where a line/transformer/converter fault can cause load or
        # generation buses to be islanded.)
        total_load = scr.bus.loc[island, 'load'].sum()
        if np.abs(total_load.real) < hynet_eps:
            _log.warning("There is no fixed load in the island comprising "
                         "the buses " + str(list(island)))
        if total_load.real > np.sum([x.p_max for x in injectors['cap']]):
            _log.warning("The active power load exceeds the injector "
                         "active power capacity in the island comprising "
                         "the buses " + str(list(island)))
        if total_load.real < np.sum([x.p_min for x in injectors['cap']]):
            _log.warning("The minimum active power injection exceeds the "
                         "active power load in the island comprising the "
                         "buses " + str(list(island)))

    # Objective checks

    for j, (cost_p, cost_q) in enumerate(zip(scr.injector['cost_p'].values,
                                             scr.injector['cost_q'].values)):
        if cost_p is not None:
            if not cost_p.is_convex():
                raise ValueError(("The P-cost function of injector {0} is "
                                  "nonconvex.").format(scr.injector.index[j]))
        if cost_q is not None:
            if not cost_q.is_convex():
                raise ValueError(("The Q-cost function of injector {0} is "
                                  "nonconvex.").format(scr.injector.index[j]))

    _log.debug("Scenario verification ({:.3f} sec.)".format(timer.total()))
