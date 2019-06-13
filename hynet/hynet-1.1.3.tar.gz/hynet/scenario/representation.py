#pylint: disable=too-many-instance-attributes,too-many-public-methods
"""
Representation of a steady-state scenario in *hynet*.
"""

import logging
import copy
from collections import namedtuple, OrderedDict
import os.path

import numpy as np
import pandas as pd

from hynet.types_ import (hynet_id_,
                          hynet_int_,
                          hynet_float_,
                          hynet_complex_,
                          BusType,
                          BranchType,
                          InjectorType)
from hynet.utilities.base import truncate_with_ellipsis, Timer
from hynet.utilities.graph import (eliminate_parallel_edges,
                                   is_acyclic_graph,
                                   get_graph_components)
from hynet.scenario.capability import CapRegion, ConverterCapRegion
from hynet.scenario.cost import PWLFunction
from hynet.scenario.verification import (verify_scenario,
                                         verify_hybrid_architecture)

_log = logging.getLogger(__name__)


class Scenario:
    """
    Specification of a steady-state grid scenario.

    Parameters
    ----------
    id : .hynet_id_
        Identifier of the scenario.
    name : str
        Name of the scenario.
    time : .hynet_float_
        Time in hours, relative to the scenario collection start time.
    database_uri : str
        URI of the associated *hynet* grid database.
    grid_name : str
        Name of the grid.
    base_mva : .hynet_float_
        Apparent power normalization constant in MVA.
    loss_price : .hynet_float_
        Artificial price for losses in $/MWh. The corresponding cost of losses
        is taken into account for the minimum-cost dispatch.
    description : str
        Description of the grid database.
    annotation : str
        Annotation string for supplementary information.
    bus : pandas.DataFrame
        Data frame with one data set per bus, indexed by the *bus ID*, which
        comprises the following columns:

        ``type``: (``BusType``)
            Type of voltage waveform at the bus.
        ``ref``: (``bool``)
            ``True`` if the bus serves as a reference.
        ``base_kv``: (``hynet_float_``)
            Base voltage in kV.
        ``y_tld``: (``hynet_complex_``)
            Shunt admittance in p.u.. For example, to add a shunt compensator
            that injects ``q`` Mvar and dissipates ``p`` MW at 1 p.u., set
            ``y_tld`` to ``(p + 1j*q) / base_mva``.
        ``load``: (``hynet_complex_``)
            Aggregated inelastic apparent power load in MVA.
        ``v_min``: (``hynet_float_``)
            Voltage lower bound in p.u..
        ``v_max``: (``hynet_float_``)
            Voltage upper bound in p.u..
        ``zone``: (``hynet_id_`` or ``None``)
            Zone ID or ``None`` if not available.
        ``annotation``: (``str``)
            Annotation string for supplementary information.

    branch : pandas.DataFrame
        Data frame with one data set per branch, indexed by the *branch ID*,
        which comprises the following columns:

        ``type``: (``BranchType``)
            Type of entity modeled by the branch.
        ``src``: (``hynet_id_``)
            Source bus ID.
        ``dst``: (``hynet_id_``)
            Destination bus ID.
        ``z_bar``: (``hynet_complex_``)
            Series impedance of the pi-equivalent in p.u..
        ``y_src``: (``hynet_complex_``)
            Shunt admittance at the source side of the pi-equivalent in p.u..
        ``y_dst``: (``hynet_complex_``)
            Shunt admittance at the destination side of the pi-equivalent in
            p.u..
        ``rho_src``: (``hynet_complex_``)
            Complex voltage ratio of the ideal transformer at the source side.
        ``rho_dst``: (``hynet_complex_``)
            Complex voltage ratio of the ideal transformer at the destination
            side.
        ``length``: (``hynet_float_``)
            Line length in kilometers or ``numpy.nan`` if not available.
        ``rating``: (``hynet_float_``)
            Ampacity in terms of a long-term MVA rating at a bus voltage of
            1 p.u. (i.e., the current limit is ``rating/base_mva``)  or
            ``numpy.nan`` if omitted.
        ``angle_min``: (``hynet_float_``)
            Angle difference lower bound in degrees or ``numpy.nan`` if
            omitted.
        ``angle_max``: (``hynet_float_``)
            Angle difference upper bound in degrees or ``numpy.nan`` if
            omitted.
        ``drop_min``: (``hynet_float_``)
            Voltage drop lower bound in percent or ``numpy.nan`` if omitted.
        ``drop_max``: (``hynet_float_``)
            Voltage drop upper bound in percent or ``numpy.nan`` if omitted.
        ``annotation``: (``str``)
            Annotation string for supplementary information.

    converter : pandas.DataFrame
        Data frame with one data set per converter, indexed by the *converter
        ID*, which comprises the following columns:

        ``src``: (``hynet_id_``)
            Source bus ID.
        ``dst``: (``hynet_id_``)
            Destination bus ID.
        ``cap_src``: (``ConverterCapRegion``)
            Specification of the converter's capability region in the P/Q-plane
            (in MW and Mvar, respectively) at the source bus. The P-axis is the
            active power flow *into the converter* and the Q-axis is the
            reactive power injection *into the grid*.
        ``cap_dst``: (``ConverterCapRegion``)
            Specification of the converter's capability region in the P/Q-plane
            (in MW and Mvar, respectively) at the destination bus. The P-axis
            is the active power flow *into the converter* and the Q-axis is the
            reactive power injection *into the grid*.
        ``loss_fwd``: (``hynet_float_``)
            Loss factor in percent for the *forward flow* of active power. This
            proportional loss factor describes the dynamic conversion losses if
            active power flows from the source bus to the destination bus.
        ``loss_bwd``: (``hynet_float_``)
            Loss factor in percent for the *backward flow* of active power. This
            proportional loss factor describes the dynamic conversion losses if
            active power flows from the destination bus to the source bus.
        ``loss_fix``: (``hynet_float_``)
            Static losses in MW (considered at the converter's source bus).
        ``annotation``: (``str``)
            Annotation string for supplementary information.

    injector : pandas.DataFrame
        Data frame with one data set per injector, indexed by the *injector
        ID*, which comprises the following columns:

        ``type``: (``InjectorType``)
            Type of entity modeled by the injector.
        ``bus``: (``hynet_id_``)
            Terminal bus ID.
        ``cap``: (``CapRegion``)
            Specification of the injector's capability region in the P/Q-plane
            (in MW and Mvar, respectively).
        ``cost_p``: (``PWLFunction`` or ``None``)
            Piecewise linear cost function for active power, which specifies
            the cost in dollars for an active power injection in MW, or
            ``None`` in case of zero costs.
        ``cost_q``: (``PWLFunction`` or ``None``)
            Piecewise linear cost function for reactive power, which specifies
            the cost in dollars for a reactive power injection in Mvar, or
            ``None`` in case of zero costs.
        ``cost_start``: (``hynet_float_``)
            Startup cost in dollars.
        ``cost_stop``: (``hynet_float_``)
            Shutdown cost in dollars.
        ``ramp_up``: (``hynet_float_``)
            Maximum upramping rate for active power in MW/h or ``numpy.nan`` if
            the upramping rate is not limited.
        ``ramp_down``: (``hynet_float_``)
            Maximum downramping rate for active power in MW/h or ``numpy.nan``
            if the downramping rate is not limited.
        ``min_up``: (``hynet_float_``)
            Minimum uptime in hours or ``numpy.nan`` if it is not limited.
        ``min_down``: (``hynet_float_``)
            Minimum downtime in hours or ``numpy.nan`` if it is not limited.
        ``energy_min``: (``hynet_float_``)
            Energy lower bound in MWh or ``numpy.nan`` if it is not limited.
        ``energy_max``: (``hynet_float_``)
            Energy upper bound in MWh or ``numpy.nan`` if it is not limited.
        ``annotation``: (``str``)
            Annotation string for supplementary information.

    See Also
    --------
    hynet.data.interface.load_scenario:
        Load a scenario from a *hynet* grid database.
    """
    def __init__(self):
        self.id = 0
        self.name = ''
        self.time = 0
        self.database_uri = ''
        self.grid_name = ''
        self.base_mva = np.nan
        self.loss_price = 0
        self.description = ''
        self.annotation = ''

        # The data frames are initialized with empty arrays to indicate the
        # data type and, in case of the absence of converters, this is also
        # necessary to avoid warnings from SciPy. To preserve the column
        # order, the initialization is performed via an ordered dictionary.
        # (This necessitates pandas 0.23.0 or higher.)

        self.bus = pd.DataFrame(OrderedDict(
            [('type', np.ndarray(0, dtype=BusType)),
             ('ref', np.ndarray(0, dtype=bool)),
             ('base_kv', np.ndarray(0, dtype=hynet_float_)),
             ('y_tld', np.ndarray(0, dtype=hynet_complex_)),
             ('load', np.ndarray(0, dtype=hynet_complex_)),
             ('v_min', np.ndarray(0, dtype=hynet_float_)),
             ('v_max', np.ndarray(0, dtype=hynet_float_)),
             ('zone', np.ndarray(0, dtype=hynet_id_)),
             ('annotation', np.ndarray(0, dtype=str))
             ]))
        self.bus.index = pd.Index([], name='id', dtype=hynet_id_)

        self.branch = pd.DataFrame(OrderedDict(
            [('type', np.ndarray(0, dtype=BranchType)),
             ('src', np.ndarray(0, dtype=hynet_id_)),
             ('dst', np.ndarray(0, dtype=hynet_id_)),
             ('z_bar', np.ndarray(0, dtype=hynet_complex_)),
             ('y_src', np.ndarray(0, dtype=hynet_complex_)),
             ('y_dst', np.ndarray(0, dtype=hynet_complex_)),
             ('rho_src', np.ndarray(0, dtype=hynet_complex_)),
             ('rho_dst', np.ndarray(0, dtype=hynet_complex_)),
             ('length', np.ndarray(0, dtype=hynet_float_)),
             ('rating', np.ndarray(0, dtype=hynet_float_)),
             ('angle_min', np.ndarray(0, dtype=hynet_float_)),
             ('angle_max', np.ndarray(0, dtype=hynet_float_)),
             ('drop_min', np.ndarray(0, dtype=hynet_float_)),
             ('drop_max', np.ndarray(0, dtype=hynet_float_)),
             ('annotation', np.ndarray(0, dtype=str))
             ]))
        self.branch.index = pd.Index([], name='id', dtype=hynet_id_)

        self.converter = pd.DataFrame(OrderedDict(
            [('src', np.ndarray(0, dtype=hynet_id_)),
             ('dst', np.ndarray(0, dtype=hynet_id_)),
             ('cap_src', np.ndarray(0, dtype=ConverterCapRegion)),
             ('cap_dst', np.ndarray(0, dtype=ConverterCapRegion)),
             ('loss_fwd', np.ndarray(0, dtype=hynet_float_)),
             ('loss_bwd', np.ndarray(0, dtype=hynet_float_)),
             ('loss_fix', np.ndarray(0, dtype=hynet_float_)),
             ('annotation', np.ndarray(0, dtype=str))
             ]))
        self.converter.index = pd.Index([], name='id', dtype=hynet_id_)

        self.injector = pd.DataFrame(OrderedDict(
            [('type', np.ndarray(0, dtype=InjectorType)),
             ('bus', np.ndarray(0, dtype=hynet_id_)),
             ('cap', np.ndarray(0, dtype=CapRegion)),
             ('cost_p', np.ndarray(0, dtype=PWLFunction)),
             ('cost_q', np.ndarray(0, dtype=PWLFunction)),
             ('cost_start', np.ndarray(0, dtype=hynet_float_)),
             ('cost_stop', np.ndarray(0, dtype=hynet_float_)),
             ('ramp_up', np.ndarray(0, dtype=hynet_float_)),
             ('ramp_down', np.ndarray(0, dtype=hynet_float_)),
             ('min_up', np.ndarray(0, dtype=hynet_float_)),
             ('min_down', np.ndarray(0, dtype=hynet_float_)),
             ('energy_min', np.ndarray(0, dtype=hynet_float_)),
             ('energy_max', np.ndarray(0, dtype=hynet_float_)),
             ('annotation', np.ndarray(0, dtype=str))
             ]))
        self.injector.index = pd.Index([], name='id', dtype=hynet_id_)

    def __eq__(self, other):
        """Return True if the scenarios are equal."""
        def fix_sorting(dataframe):
            return dataframe.sort_index(axis='columns').sort_index(axis='index')

        def compare_dataframe(dataframe1, dataframe2):
            return fix_sorting(dataframe1).equals(fix_sorting(dataframe2))

        # REMARK: The complex voltage ratios need to be treated separately
        # as they are converted between polar and rectangular form during
        # loading and saving, which causes slight numerical differences.
        rho_columns = ['rho_src', 'rho_dst']
        if self.branch.shape == other.branch.shape:
            rho_equal = \
                np.all(np.isclose(fix_sorting(self.branch[rho_columns]),
                                  fix_sorting(other.branch[rho_columns])))
        else:
            rho_equal = False
        self_branch = self.branch.drop(rho_columns, axis='columns')
        other_branch = other.branch.drop(rho_columns, axis='columns')

        return (rho_equal and
                self.id == other.id and
                self.name == other.name and
                self.time == other.time and
                self.database_uri == other.database_uri and
                self.grid_name == other.grid_name and
                self.base_mva == other.base_mva and
                self.loss_price == other.loss_price and
                self.description == other.description and
                self.annotation == other.annotation and
                compare_dataframe(self.bus, other.bus) and
                compare_dataframe(self_branch, other_branch) and
                compare_dataframe(self.converter, other.converter) and
                compare_dataframe(self.injector, other.injector))

    def copy(self):
        """Return a deep copy of this scenario."""
        timer = Timer()
        scr = copy.deepcopy(self)
        # The deep copy on object columns is not supported, see
        #   https://github.com/pandas-dev/pandas/issues/12663
        # Due to this, we deep copy those manually.
        for l, (cap_src, cap_dst) in enumerate(zip(self.converter['cap_src'],
                                                   self.converter['cap_dst'])):
            id_ = self.converter.index[l]
            scr.converter.at[id_, 'cap_src'] = copy.deepcopy(cap_src)
            scr.converter.at[id_, 'cap_dst'] = copy.deepcopy(cap_dst)
        for j, (cap, cost_p, cost_q) in enumerate(zip(self.injector['cap'],
                                                      self.injector['cost_p'],
                                                      self.injector['cost_q'])):
            id_ = self.injector.index[j]
            scr.injector.at[id_, 'cap'] = copy.deepcopy(cap)
            scr.injector.at[id_, 'cost_p'] = copy.deepcopy(cost_p)
            scr.injector.at[id_, 'cost_q'] = copy.deepcopy(cost_q)
        _log.debug("Scenario deep copy ({:.3f} sec.)".format(timer.total()))
        return scr

    def verify(self):
        """
        Verify the integrity and validity of the scenario.

        This method performs an extensive series of checks on the scenario
        to ensure that the data is consistent (e.g., the references between
        data frames), proper (e.g., constraint limits), and valid (i.e.,
        compliant with all preconditions as assumed by *hynet*).

        Besides errors being reported via an exception, critical settings are
        reported by issuing a warning via the logging system.

        Raises
        ------
        ValueError
            In case any kind of integrity or validity violation is detected.
        """
        verify_scenario(self)

    @property
    def num_buses(self):
        """Return the number of buses."""
        return len(self.bus.index)

    @property
    def num_branches(self):
        """Return the number of branches."""
        return len(self.branch.index)

    @property
    def num_converters(self):
        """Return the number of converters."""
        return len(self.converter.index)

    @property
    def num_injectors(self):
        """Return the number of injectors."""
        return len(self.injector.index)

    @property
    def e_src(self):
        """
        Return the branch source bus indices as a pandas series.

        **Remark:** This property is *index-based* and intended for internal use.
        """
        return pd.Series(self.get_bus_index(self.branch['src'].values),
                         index=self.branch.index)

    @property
    def e_dst(self):
        """
        Return the branch destination bus indices as a pandas series.

        **Remark:** This property is *index-based* and intended for internal use.
        """
        return pd.Series(self.get_bus_index(self.branch['dst'].values),
                         index=self.branch.index)

    @property
    def c_src(self):
        """
        Return the converter source bus indices as a pandas series.

        **Remark:** This property is *index-based* and intended for internal use.
        """
        return pd.Series(self.get_bus_index(self.converter['src'].values),
                         index=self.converter.index)

    @property
    def c_dst(self):
        """
        Return the converter destination bus indices as a pandas series.

        **Remark:** This property is *index-based* and intended for internal use.
        """
        return pd.Series(self.get_bus_index(self.converter['dst'].values),
                         index=self.converter.index)

    @property
    def n_src(self):
        """
        Return the injector terminal bus indices as a pandas series.

        **Remark:** This property is *index-based* and intended for internal use.
        """
        return pd.Series(self.get_bus_index(self.injector['bus'].values),
                         index=self.injector.index)

    def get_bus_index(self, bus_id):
        """
        Return the bus index for the given bus identifier.

        **Remark:** This result is *index-based* and intended for internal use.
        """
        return np.array([self.bus.index.get_loc(key) for key in bus_id],
                        dtype=hynet_int_)

    def get_ref_buses(self):
        """
        Return an array with the bus index of the reference buses.

        **Remark:** This result is *index-based* and intended for internal use.
        """
        return np.nonzero(self.bus['ref'].values)[0]

    def has_hybrid_architecture(self):
        """
        Return ``True`` if the scenario features the *hybrid architecture*.

        The *hybrid architecture* denotes a particular class of power systems
        that, under very mild conditions, induces exactness to the semidefinite
        and second-order cone relaxation of the OPF problem in case that no
        *pathological price profile* emerges, see [1]_, [2]_, and [3]_. This
        method assumes validity of the scenario, see ``Scenario.verify``.

        References
        ----------
        .. [1] M. Hotz and W. Utschick, "A Hybrid Transmission Grid
               Architecture Enabling Efficient Optimal Power Flow," in IEEE
               Trans. Power Systems, vol. 31, no. 6, pp. 4504-4516, Nov. 2016.
        .. [2] M. Hotz and W. Utschick, "The Hybrid Transmission Grid
               Architecture: Benefits in Nodal Pricing," in IEEE Trans. Power
               Systems, vol. 33, no. 2, pp. 1431-1442, Mar. 2018.
        .. [3] M. Hotz and W. Utschick, "hynet: An optimal power flow framework
               for hybrid AC/DC power systems," arXiv:1811.10496, Nov. 2018.
               [Online]. Available: http://arxiv.org/abs/1811.10496

        See Also
        --------
        hynet.scenario.representation.Scenario.verify
        """
        return verify_hybrid_architecture(self)

    def has_acyclic_subgrids(self):
        """
        Return ``True`` if all subgrids are acyclic and ``False`` otherwise.
        """
        return is_acyclic_graph(np.arange(self.num_buses),
                                (self.e_src.values, self.e_dst.values))

    def has_acyclic_ac_subgrids(self):
        """
        Return ``True`` if all AC subgrids are acyclic and ``False`` otherwise.
        """
        ac_buses = np.where(np.equal(self.bus['type'].values, BusType.AC))[0]
        mask = np.logical_and(np.isin(self.e_src.values, ac_buses),
                              np.isin(self.e_dst.values, ac_buses))
        return is_acyclic_graph(ac_buses, (self.e_src.values[mask],
                                           self.e_dst.values[mask]))

    def has_acyclic_dc_subgrids(self):
        """
        Return ``True`` if all DC subgrids are acyclic and ``False`` otherwise.
        """
        dc_buses = np.where(np.equal(self.bus['type'].values, BusType.DC))[0]
        mask = np.logical_and(np.isin(self.e_src.values, dc_buses),
                              np.isin(self.e_dst.values, dc_buses))
        return is_acyclic_graph(dc_buses, (self.e_src.values[mask],
                                           self.e_dst.values[mask]))

    def get_ac_subgrids(self):
        """
        Return a list with a pandas index of bus IDs for every AC subgrid.
        """
        ac_buses = np.where(np.equal(self.bus['type'].values, BusType.AC))[0]
        mask = np.logical_and(np.isin(self.e_src.values, ac_buses),
                              np.isin(self.e_dst.values, ac_buses))
        subgrids = get_graph_components(ac_buses, (self.e_src.values[mask],
                                                   self.e_dst.values[mask]))
        return [self.bus.index[subgrid] for subgrid in subgrids]

    def get_dc_subgrids(self):
        """
        Return a list with a pandas index of bus IDs for every DC subgrid.
        """
        dc_buses = np.where(np.equal(self.bus['type'].values, BusType.DC))[0]
        mask = np.logical_and(np.isin(self.e_src.values, dc_buses),
                              np.isin(self.e_dst.values, dc_buses))
        subgrids = get_graph_components(dc_buses, (self.e_src.values[mask],
                                                   self.e_dst.values[mask]))
        return [self.bus.index[subgrid] for subgrid in subgrids]

    def get_islands(self):
        """
        Return a list with a pandas index of bus IDs for every islanded grid.
        """
        islands = get_graph_components(np.arange(self.num_buses),
                                       (np.concatenate((self.e_src.values,
                                                        self.c_src.values)),
                                        np.concatenate((self.e_dst.values,
                                                        self.c_dst.values))))
        return [self.bus.index[island] for island in islands]

    def analyze_cycles(self):
        """
        Return a data frame with an analysis of cyclic connections of buses.

        The information about cyclic connections of buses is relevant in the
        study of transitions to the *hybrid architecture*, which establishes
        exactness of the semidefinite and second-order cone relaxation of the
        OPF problem under normal operating conditions, cf. [1]_.

        Returns
        -------
        result : pandas.DataFrame
            Data frame with the cycle analysis result for every subgrid, which
            comprises the following columns:

            ``num_cycles``: (``hynet_int_``)
                Number of cycles in the subgrid.
            ``type``: (``BusType``)
                Type of the subgrid.
            ``buses``: (``pandas.Index``)
                Pandas index with the *bus IDs* of the buses that are part of
                the subgrid.

        References
        ----------
        .. [1] M. Hotz and W. Utschick, "The Hybrid Transmission Grid
               Architecture: Benefits in Nodal Pricing," in IEEE Trans. Power
               Systems, vol. 33, no. 2, pp. 1431-1442, Mar. 2018.
        """
        subgrids = self.get_ac_subgrids() + self.get_dc_subgrids()
        src = self.branch['src']
        dst = self.branch['dst']

        result = pd.DataFrame(OrderedDict(
            [('num_cycles', np.ndarray(0, dtype=hynet_int_)),
             ('type', np.ndarray(0, dtype=BusType)),
             ('buses', np.ndarray(0, dtype=object))
             ]))
        result.index = pd.Index([], name='subgrid', dtype=hynet_id_)

        for n, subgrid in enumerate(subgrids):
            idx = src.isin(subgrid) | dst.isin(subgrid)
            num_corridors = len(eliminate_parallel_edges((src.loc[idx].values,
                                                          dst.loc[idx].values))[0])
            result.loc[n + 1] = (num_corridors - (len(subgrid) - 1),
                                 self.bus.at[subgrid[0], 'type'],
                                 subgrid)
        return result

    def get_branches_in_corridors(self, corridors):
        """
        Return a pandas index of branch IDs that reside in these corridors.

        **Remark:** This property is *index-based* and intended for internal use.

        Parameters
        ----------
        corridors : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
            Tuple of NumPy arrays that state the source *bus index* and
            destination *bus index* of the corridors.

        Returns
        -------
        index : pandas.Index
            Pandas index with the *branch IDs* of those branches that reside in
            the specified corridors.
        """
        if self.branch.empty or not corridors[0].size:
            return pd.Index([], dtype=hynet_id_, name=self.branch.index.name)

        edges = (self.e_src.values, self.e_dst.values)
        E = np.column_stack((edges[0], edges[1]))
        E.sort(axis=1)

        C = np.column_stack((corridors[0], corridors[1]))
        C.sort(axis=1)

        resident = np.zeros(self.num_branches, dtype=bool)
        for n in range(C.shape[0]):
            resident |= (E[:, 0] == C[n, 0]) & (E[:, 1] == C[n, 1])
        return self.branch.index[resident]

    def _get_parallel_branch_indices(self):
        """
        Return a list with an array of *branch indices* for parallel branches.
        """
        parallel_branches = []
        if self.branch.empty:
            return parallel_branches

        E = np.column_stack((self.e_src.values, self.e_dst.values))
        E.sort(axis=1)

        (C, count) = np.unique(E, axis=0, return_counts=True)
        C = C[count > 1]
        for n in range(C.shape[0]):
            parallel_branches.append(
                np.where((E[:, 0] == C[n, 0]) & (E[:, 1] == C[n, 1]))[0])
        return parallel_branches

    def get_parallel_branches(self):
        """
        Return a list with a pandas index of branch IDs for parallel branches.
        """
        index = self.branch.index
        return [index[x] for x in self._get_parallel_branch_indices()]

    def get_ac_branches(self):
        """
        Return a pandas index with the branch IDs of all AC branches.
        """
        mask = self.bus.loc[self.branch['src'], 'type'].values == BusType.AC
        return self.branch.index[mask]

    def get_dc_branches(self):
        """
        Return a pandas index with the branch IDs of all DC branches.
        """
        mask = self.bus.loc[self.branch['src'], 'type'].values == BusType.DC
        return self.branch.index[mask]

    def remove_buses(self, buses):
        """
        Remove the specified buses and attached branches, converters, and injectors.

        Parameters
        ----------
        buses : Iterable[.hynet_id_]
            Iterable of bus IDs that specifies the buses to be removed.

        Returns
        -------
        branches : pandas.Index
            Removed branches, which were connected to the removed buses.
        converters : pandas.Index
            Removed converters, which were connected to the removed buses.
        injectors : pandas.Index
            Removed injectors, which were connected to the removed buses.
        """
        bus_idx = pd.Index(buses)
        self.bus.drop(bus_idx, axis=0, inplace=True)

        bus_lst = bus_idx.tolist()

        branches = self.branch.index[self.branch['src'].isin(bus_lst) |
                                     self.branch['dst'].isin(bus_lst)]
        self.branch.drop(branches, axis=0, inplace=True)

        converters = self.converter.index[self.converter['src'].isin(bus_lst) |
                                          self.converter['dst'].isin(bus_lst)]
        self.converter.drop(converters, axis=0, inplace=True)

        injectors = self.injector.index[self.injector['bus'].isin(bus_lst)]
        self.injector.drop(injectors, axis=0, inplace=True)
        return branches, converters, injectors

    def get_time_tuple(self):
        """
        Return the scenario time stamp as ``(days, hours, minutes, seconds)``.
        """
        (min_, sec_) = divmod(round(self.time * 3600), 60)
        (hrs_, min_) = divmod(min_, 60)
        (dys_, hrs_) = divmod(hrs_, 24)
        time_ = namedtuple('time', ['days', 'hours', 'minutes', 'seconds'])
        return time_(hynet_int_(dys_), hynet_int_(hrs_),
                     hynet_int_(min_), hynet_int_(sec_))

    def get_time_string(self):
        """
        Return the scenario time stamp as ``Dd HH:MM:SS``.
        """
        return "{0.days}d {0.hours:02d}:{0.minutes:02d}:{0.seconds:02d}"\
               .format(self.get_time_tuple())

    def set_conservative_rating(self):
        """
        Adjust the branch rating to a conservative setting (MATPOWER compat.).

        In the *hynet* data format, the branch rating is an ampacity rating in
        terms of the apparent power flow at 1 p.u. (due to reasons stated in
        [1]_, Section III), i.e., the rating divided by ``base_mva`` is the
        ampacity rating. In the MATPOWER format, the rating is an apparent
        power rating, i.e., it is independent of the voltage. To ensure
        feasibility w.r.t. MATPOWER's apparent power rating, the *hynet* rating
        may be converted to a more conservative rating as described in [1]_,
        Remark 1, which is performed by this method.

        References
        ----------
        .. [1] M. Hotz and W. Utschick, "A Hybrid Transmission Grid
               Architecture Enabling Efficient Optimal Power Flow," in IEEE
               Trans. Power Systems, vol. 31, no. 6, pp. 4504-4516, Nov. 2016.
        """
        v_max = self.bus['v_max']
        v_max_branch = np.maximum(v_max.loc[self.branch['src']].values,
                                  v_max.loc[self.branch['dst']].values)
        self.branch['rating'] /= v_max_branch

    def set_minimum_series_resistance(self, min_resistance):
        """
        Set the series resistance of all branches to a minimum of ``min_resistance``.

        Very small values of the series resistance of branches may lead to
        numerical issues during the solution of the OPF problem. With this
        method, the series resistance is enforced to be ``>= min_resistance``.

        Parameters
        ----------
        min_resistance : float
            Minimum resistance for the series resistance of all branches. If a
            branch has a series resistance below this value, it is replaced by
            ``min_resistance``.
        """
        idx = self.branch['z_bar'].real < min_resistance
        self.branch.loc[idx, 'z_bar'] =\
            min_resistance + 1j*self.branch.loc[idx, 'z_bar'].imag

    def ensure_reference(self):
        """
        Automatically add a reference bus to all AC subgrids without a reference.

        All AC subgrids are required to have a dedicated reference bus.
        However, cases may arise in which certain AC subgrids have no
        predefined reference, e.g., due to the partitioning or islanding of AC
        subgrids in a simulated branch outage. This method automatically
        assigns a reference bus to all AC subgrids without a reference, where
        the reference bus is set to the bus with the injector of highest
        capacity therein, if available.
        """
        for subgrid in self.get_ac_subgrids():
            if self.bus.loc[subgrid, 'ref'].any():
                continue
            injectors = self.injector.loc[self.injector['bus'].isin(subgrid)]
            ref_bus = subgrid[0]
            p_max = 0
            for id_, (bus, cap) in injectors[['bus', 'cap']].iterrows():
                if cap.p_max > p_max:
                    ref_bus = bus
                    p_max = cap.p_max
            self.bus.at[ref_bus, 'ref'] = True

    def add_compensator(self, bus, q_max, q_min=None, cost_q=None):
        """
        Add a reactive power compensator to this scenario.

        Parameters
        ----------
        bus : .hynet_id_
            Bus ID of the terminal bus for the compensator.
        q_max : .hynet_float_
            Maximum reactive power in Mvar that can be injected.
        q_min : .hynet_float_, optional
            Lower bound in Mvar (default ``-q_max``) on the reactive power
            injection.
        cost_q : PWLFunction, optional
            Piecewise linear cost function for reactive power. By default,
            the reactive power is provided at zero cost.

        Returns
        -------
        injector_id : .hynet_id_
            Injector ID of the added compensator.
        """
        if q_min is None:
            q_min = -q_max

        if self.injector.empty:
            injector_id = 1
        else:
            injector_id = self.injector.index.max() + 1

        compensator = pd.DataFrame({
            'type': [InjectorType.COMPENSATION],
            'bus': [hynet_id_(bus)],
            'cap': [CapRegion(p_bnd=(0, 0), q_bnd=(q_min, q_max))],
            'cost_p': [None],
            'cost_q': [cost_q],
            'cost_start': [hynet_float_(0.0)],
            'cost_stop': [hynet_float_(0.0)],
            'ramp_up': [hynet_float_(np.nan)],
            'ramp_down': [hynet_float_(np.nan)],
            'min_up': [hynet_float_(np.nan)],
            'min_down': [hynet_float_(np.nan)],
            'energy_min': [hynet_float_(np.nan)],
            'energy_max': [hynet_float_(np.nan)],
            'annotation': ['']
        }, index=[injector_id])

        self.injector = self.injector.append(compensator, sort=False)
        return injector_id

    def __repr__(self):
        return ("\n+" + "-"*78 + "+\n"
                "| SCENARIO" + " "*69 + "|\n"
                "+" + "-"*78 + "+\n"
                "| Grid name:      {1:<61s}" + "|\n"
                "| Database:       {2:<61s}" + "|\n"
                "| Scenario ID:    {3:<61s}" + "|\n"
                "| Scenario name:  {4:<61s}" + "|\n"
                "| Scenario time:  {5:<61s}" + "|\n"
                "| MVA base:       {6:<61s}" + "|\n"
                "| Loss price:     {7:<61s}" + "|\n"
                "+" + "-"*78 + "+\n\n"
                "+" + "-"*78 + "+\n"
                "| BUS DATA" + " "*69 + "|\n"
                "+" + "-"*78 + "+\n\n{0.bus}\n\n"
                "+" + "-"*78 + "+\n"
                "| BRANCH DATA" + " "*66 + "|\n"
                "+" + "-"*78 + "+\n\n{0.branch}\n\n"
                "+" + "-"*78 + "+\n"
                "| CONVERTER DATA" + " "*63 + "|\n"
                "+" + "-"*78 + "+\n\n{0.converter}\n\n"
                "+" + "-"*78 + "+\n"
                "| INJECTOR DATA" + " "*64 + "|\n"
                "+" + "-"*78 + "+\n\n{0.injector}\n"
                ).format(self,
                         truncate_with_ellipsis(self.grid_name, 61),
                         truncate_with_ellipsis(
                             os.path.basename(self.database_uri), 61),
                         str(self.id),
                         truncate_with_ellipsis(self.name, 61),
                         self.get_time_string(),
                         str(self.base_mva) + " MVA",
                         str(self.loss_price) + " $/MWh")
