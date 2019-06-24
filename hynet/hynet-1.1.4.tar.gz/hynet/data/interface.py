#pylint: disable=no-member,too-many-lines,too-many-locals,too-many-statements
"""
Interface to access the model data in a *hynet* grid database.
"""

import logging

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import make_transient
from sqlalchemy.orm.exc import NoResultFound

from hynet.data.connection import DBTransaction
from hynet.data.structure import (DBInfo,
                                  DBScenario,
                                  DBBus,
                                  DBBranch,
                                  DBConverter,
                                  DBInjector,
                                  DBCapabilityRegion,
                                  DBSamplePoint,
                                  DBShunt,
                                  DBScenarioLoad,
                                  DBScenarioInjector,
                                  DBScenarioInactivity)
from hynet.scenario.capability import HalfSpace, CapRegion, ConverterCapRegion
from hynet.scenario.cost import PWLFunction
from hynet.scenario.representation import Scenario
from hynet.types_ import (hynet_id_,
                          hynet_float_,
                          hynet_complex_,
                          hynet_eps,
                          BusType,
                          BranchType,
                          InjectorType,
                          EntityType,
                          DBInfoKey)
from hynet.utilities.base import Timer

_log = logging.getLogger(__name__)


# === UTILITY FUNCTIONS =======================================================


def fix_hynet_id(series):
    """
    Fix the data type of the given nullable integer pandas series.

    When reading integer columns that contain NULL values using
    ``pandas.read_sql_table``, they are converted to float [1]_. This may lead
    to errors, e.g. the PWL function foreign keys cause key errors during
    indexing. This function fixes the type.

    References
    ----------
    .. [1] https://github.com/pandas-dev/pandas/issues/13049
    """
    if series.dtype == hynet_id_:
        return series
    series = series.astype(object)
    idx_nan = series.isnull()
    idx_val = ~idx_nan
    if np.any(np.mod(series.loc[idx_val], 1) != 0):
        raise ValueError("Some ID values are non-integer.")
    series.loc[idx_nan] = None
    series.loc[idx_val] = series.loc[idx_val].map(hynet_id_)
    return series


def get_max_bus_id(database):
    """
    Determine the highest bus ID in the specified *hynet* grid database.

    Parameters
    ----------
    database : DBConnection
        Connection to the *hynet* grid database.

    Returns
    -------
    result : .hynet_id_ or None
        The highest bus ID in the database or None if there are no buses.
    """
    with DBTransaction(database) as transaction:
        max_bus_id = transaction.query(
            func.max(DBBus.id).label("max_bus_id")).one().max_bus_id
    return max_bus_id


def get_max_scenario_id(database):
    """
    Determine the highest scenario ID in the specified *hynet* grid database.

    Parameters
    ----------
    database : DBConnection
        Connection to the *hynet* grid database.

    Returns
    -------
    result : .hynet_id_ or None
        The highest scenario ID in the database or None if there are no
        scenarios.
    """
    with DBTransaction(database) as transaction:
        max_scenario_id = transaction.query(
            func.max(DBScenario.id).label("max_scenario_id")).one().max_scenario_id
    return max_scenario_id


# === LOADING OF SCENARIO INFORMATION =========================================


def get_scenario_info(database):
    """
    Load a list of all scenarios from the specified *hynet* grid database.

    Parameters
    ----------
    database : DBConnection
        Connection to the *hynet* grid database.

    Returns
    -------
    pandas.DataFrame
        Data frame with a list of all scenarios, indexed by the *scenario ID*,
        which comprises the following columns:

        ``name``: (``str``)
            Name of the scenario.
        ``time``: (``hynet_float_``)
            Relative time in hours of the scenario (w.r.t. the scenario group
            start time).
        ``annotation``: (``str``)
            Annotation string for supplementary information.

    Raises
    ------
    ValueError
        In case that the database is empty.
    """
    if database.empty:
        raise ValueError("The database is empty.")
    scenario_info = pd.read_sql_table(DBScenario.__tablename__,
                                      database.engine)
    scenario_info.drop('loss_price', axis='columns', inplace=True)
    scenario_info.set_index('id', inplace=True)

    # Move 'name'-column to the front
    columns = scenario_info.columns.tolist()
    columns.insert(0, columns.pop(columns.index('name')))
    return scenario_info.reindex(columns=columns)


# === LOADING OF SCENARIOS ====================================================


def load_scenario(database, scenario_id=0):
    """
    Load the specified scenario from the *hynet* grid database.

    Parameters
    ----------
    database : DBConnection
        Connection to the *hynet* grid database.
    scenario_id : .hynet_id_, optional
        Identifier of the scenario; default is ``0``.

    Returns
    -------
    scenario : hynet.scenario.representation.Scenario
        Scenario object with the loaded data.

    Raises
    ------
    ValueError
        In case that the database is empty or the scenario with the specified
        ID was not found.
    """
    timer = Timer()

    if database.empty:
        raise ValueError("The database is empty.")

    scenario = Scenario()
    scenario.id = scenario_id
    scenario.database_uri = database.database_uri

    scenario.grid_name = database.get_setting(DBInfoKey.GRID_NAME)
    scenario.description = database.get_setting(DBInfoKey.DESCRIPTION)
    scenario.base_mva = hynet_float_(database.get_setting(DBInfoKey.BASE_MVA))

    with DBTransaction(database) as transaction:
        # General grid information
        try:
            scenario_result = \
                transaction.query(DBScenario).filter(
                    DBScenario.id == scenario_id).one()
        except NoResultFound:
            raise ValueError("Scenario with ID {:d} was not found."
                             .format(scenario_id))

        scenario.name = scenario_result.name
        scenario.time = hynet_float_(scenario_result.time)
        scenario.loss_price = hynet_float_(scenario_result.loss_price)
        scenario.annotation = scenario_result.annotation

        # Load the bus data
        scenario.bus = pd.read_sql_table(DBBus.__tablename__,
                                         database.engine)
        scenario.bus.set_index('id', inplace=True)

        # Map the bus types to their enumeration value
        scenario.bus['type'] = \
            scenario.bus['type'].map(lambda t: BusType(t)).values

        # Fix data type issues with the zone column
        scenario.bus['zone'] = fix_hynet_id(scenario.bus['zone'])

        # Load the shunt data (excluding any inactive shunts)
        scenario.bus['y_tld'] = np.zeros(scenario.num_buses,
                                         dtype=hynet_complex_)

        shunts = pd.read_sql_table(DBShunt.__tablename__, database.engine)
        shunts.set_index('id', inplace=True)

        shunt_inactivity = transaction.query(DBScenarioInactivity)\
            .filter(DBScenarioInactivity.scenario_id == scenario_id)\
            .filter(DBScenarioInactivity.entity_type == EntityType.SHUNT)
        try:
            shunts.drop([entity.entity_id for entity in shunt_inactivity],
                        axis='index', inplace=True)
        except KeyError:
            raise ValueError("Shunt inactivity refers to a nonexistent shunt.")
        shunts['y_tld'] = (shunts['p'] + 1j * shunts['q']) / scenario.base_mva

        for bus_id, shunt_value in zip(shunts['bus_id'], shunts['y_tld']):
            scenario.bus.at[bus_id, 'y_tld'] += shunt_value

        # Load the load data
        scenario.bus['load'] = np.zeros(scenario.num_buses,
                                        dtype=hynet_complex_)
        load_results = \
            transaction.query(DBScenarioLoad).filter(
                DBScenarioLoad.scenario_id == scenario_id)
        for load in load_results:
            scenario.bus.at[load.bus_id, 'load'] += load.p + 1j * load.q

        # Load the branch data
        scenario.branch = pd.read_sql_table(DBBranch.__tablename__,
                                            database.engine)
        scenario.branch.set_index('id', inplace=True)
        scenario.branch.rename(columns={'src_id': 'src', 'dst_id': 'dst'},
                               inplace=True)

        # Map the branch types to their enumeration value
        scenario.branch['type'] = \
            scenario.branch['type'].map(lambda t: BranchType(t)).values

        # Calculate the series impedance and shunt admittances
        scenario.branch['z_bar'] = \
            scenario.branch['r'] + 1j * scenario.branch['x']
        scenario.branch['y_src'] = 1j * scenario.branch['b_src']
        scenario.branch['y_dst'] = 1j * scenario.branch['b_dst']
        scenario.branch.drop(['r', 'x', 'b_src', 'b_dst'],
                             axis='columns', inplace=True)

        # Calculate the complex-valued voltage ratios of the transformers
        scenario.branch['rho_src'] = scenario.branch['ratio_src'] * np.exp(
            1j * scenario.branch['phase_src'] * np.pi / 180)
        scenario.branch['rho_dst'] = scenario.branch['ratio_dst'] * np.exp(
            1j * scenario.branch['phase_dst'] * np.pi / 180)
        scenario.branch.drop(['ratio_src', 'phase_src',
                              'ratio_dst', 'phase_dst'],
                             axis='columns', inplace=True)

        # Load the converter data
        scenario.converter = pd.read_sql_table(DBConverter.__tablename__,
                                               database.engine)
        scenario.converter.set_index('id', inplace=True)
        scenario.converter.rename(columns={'src_id': 'src', 'dst_id': 'dst'},
                                  inplace=True)

        # Prepare the conversion of cap. region IDs to cap. region objects
        cap_region = pd.read_sql_table(DBCapabilityRegion.__tablename__,
                                       database.engine)
        cap_region.set_index('id', inplace=True)

        def get_half_space(offset, slope):
            if offset is None or slope is None or \
                    np.isnan(offset) or np.isnan(slope):
                return None
            return HalfSpace(offset, slope)

        def get_cap_region_param(key):
            col = DBCapabilityRegion.__table__.c
            return {'p_bnd': (cap_region.at[key, col.p_min.name],
                              cap_region.at[key, col.p_max.name]),
                    'q_bnd': (cap_region.at[key, col.q_min.name],
                              cap_region.at[key, col.q_max.name]),
                    'lt': get_half_space(cap_region.at[key, col.lt_ofs.name],
                                         cap_region.at[key, col.lt_slp.name]),
                    'rt': get_half_space(cap_region.at[key, col.rt_ofs.name],
                                         cap_region.at[key, col.rt_slp.name]),
                    'lb': get_half_space(cap_region.at[key, col.lb_ofs.name],
                                         cap_region.at[key, col.lb_slp.name]),
                    'rb': get_half_space(cap_region.at[key, col.rb_ofs.name],
                                         cap_region.at[key, col.rb_slp.name])}

        # Map the converter cap. region IDs to objects
        scenario.converter[['cap_src', 'cap_dst']] = \
            scenario.converter[['cap_src_id', 'cap_dst_id']].applymap(
                lambda key: ConverterCapRegion(**get_cap_region_param(key)))
        scenario.converter.drop(['cap_src_id', 'cap_dst_id'],
                                axis='columns', inplace=True)

        # Load the injector data
        scenario.injector = pd.read_sql_table(DBInjector.__tablename__,
                                              database.engine)
        scenario.injector.set_index('id', inplace=True)
        scenario.injector.rename(columns={'bus_id': 'bus'}, inplace=True)

        # Map the injector types to their enumeration value
        scenario.injector['type'] = \
            scenario.injector['type'].map(lambda t: InjectorType(t)).values

        # Map the injector cap. region IDs to objects
        scenario.injector['cap'] = scenario.injector['cap_id'].map(
            lambda key: CapRegion(**get_cap_region_param(key)))
        scenario.injector.drop('cap_id', axis='columns', inplace=True)

        # Fix data type issues with the PWL function foreign keys
        scenario.injector['cost_p_id'] = \
            fix_hynet_id(scenario.injector['cost_p_id'])
        scenario.injector['cost_q_id'] = \
            fix_hynet_id(scenario.injector['cost_q_id'])

        # Prepare the conversion of PWL function IDs to PWL function objects
        sample_point = pd.read_sql_table(DBSamplePoint.__tablename__,
                                         database.engine)
        sample_point.set_index('id', inplace=True)

        def get_pwl_function(key):
            if key is None:
                return None
            x = sample_point.at[key, DBSamplePoint.__table__.c.x.name]
            y = sample_point.at[key, DBSamplePoint.__table__.c.y.name]
            return PWLFunction((x, y))

        # Map the PWL function region IDs to objects
        scenario.injector['cost_p'] = \
            scenario.injector['cost_p_id'].map(get_pwl_function)
        scenario.injector['cost_q'] = \
            scenario.injector['cost_q_id'].map(get_pwl_function)
        scenario.injector.drop(['cost_p_id', 'cost_q_id'],
                               axis='columns', inplace=True)

        # Adapt the injectors according to the scenario data
        injector_adjustment = \
            transaction.query(DBScenarioInjector).filter(
                DBScenarioInjector.scenario_id == scenario_id)

        def scale_pwl_function(pwl_function, scaling):
            if pwl_function is not None:
                pwl_function.scale(scaling)

        for adjustment in injector_adjustment:
            id_ = adjustment.injector_id

            # Adjust the cost function scaling
            scale_pwl_function(scenario.injector.at[id_, 'cost_p'],
                               adjustment.cost_scaling)
            scale_pwl_function(scenario.injector.at[id_, 'cost_q'],
                               adjustment.cost_scaling)

            # Adjust the capability region box constraint
            cap = scenario.injector.at[id_, 'cap']
            cap.p_min = adjustment.p_min
            cap.p_max = adjustment.p_max
            cap.q_min = adjustment.q_min
            cap.q_max = adjustment.q_max

        # Eliminate inactive entities
        # (REMARK: Inactive shunts are excluded via the SQL query above)
        inactive_entities = \
            transaction.query(DBScenarioInactivity).filter(
                DBScenarioInactivity.scenario_id == scenario_id)
        removed_buses = []
        for entity in inactive_entities:
            if entity.entity_type == EntityType.BUS:
                removed_buses.append(entity.entity_id)
            elif entity.entity_type == EntityType.BRANCH:
                scenario.branch.drop(entity.entity_id, inplace=True)
            elif entity.entity_type == EntityType.CONVERTER:
                scenario.converter.drop(entity.entity_id, inplace=True)
            elif entity.entity_type == EntityType.INJECTOR:
                scenario.injector.drop(entity.entity_id, inplace=True)
            elif entity.entity_type != EntityType.SHUNT:
                raise ValueError("Invalid entity is referenced for inactivity "
                                 + "({:s}: {:d}).".format(entity.entity_type,
                                                          entity.entity_id))
        scenario.remove_buses(removed_buses)

    _log.debug("Loaded scenario '{:s}' (id={:d}) of '{:s}' ({:.3f} sec.)"
               .format(scenario.name, scenario.id,
                       scenario.grid_name, timer.total()))
    return scenario


# === SOME SUPPORTING FUNCTIONS FOR THE INTERFACE FUNCTIONS BELOW =============


def _select_scenario_inactivities(scenario_id, transaction):
    return transaction.query(DBScenarioInactivity)\
        .filter(DBScenarioInactivity.scenario_id == scenario_id).all()


def _select_scenario_injectors(scenario_id, transaction):
    return transaction.query(DBScenarioInjector)\
        .filter(DBScenarioInjector.scenario_id == scenario_id).all()


def _select_scenario_loads(scenario_id, transaction):
    return transaction.query(DBScenarioLoad)\
        .filter(DBScenarioLoad.scenario_id == scenario_id).all()


def _select_scenario(scenario_id, transaction):
    return transaction.query(DBScenario)\
        .filter(DBScenario.id == scenario_id).one()


def _nan_to_none(value):
    if value is None:
        return None
    return None if np.isnan(value) else value


def _get_bus_data(scenario):
    counter_shunt_id = 1
    for index, pd_bus in scenario.bus.iterrows():
        bus_id = pd_bus.name  # Series name is the index of the row
        bus = DBBus(id=bus_id,
                    type=pd_bus.type,
                    ref=pd_bus.ref,
                    base_kv=pd_bus.base_kv,
                    v_min=pd_bus.v_min,
                    v_max=pd_bus.v_max,
                    zone=_nan_to_none(pd_bus.zone),
                    annotation=pd_bus.annotation)
        if pd_bus.load != 0:
            load = DBScenarioLoad(scenario_id=scenario.id,
                                  bus_id=bus_id,
                                  p=pd_bus.load.real,
                                  q=pd_bus.load.imag)
        else:
            load = None
        if pd_bus.y_tld != 0:
            shunt = DBShunt(id=counter_shunt_id,
                            bus_id=bus_id,
                            p=pd_bus.y_tld.real * scenario.base_mva,
                            q=pd_bus.y_tld.imag * scenario.base_mva,
                            annotation='')
            counter_shunt_id += 1
        else:
            shunt = None
        yield bus, load, shunt


def _get_branch_data(scenario):
    for index, pd_branch in scenario.branch.iterrows():
        branch_id = pd_branch.name  # Series name is the index of the row
        if pd_branch.y_src.real != 0 or pd_branch.y_dst.real != 0:
            _log.warning("Nonzero shunt conductance of branch {:d} is ignored"
                         .format(branch_id))
        branch = DBBranch(id=branch_id,
                          type=pd_branch.type,
                          src_id=pd_branch.src,
                          dst_id=pd_branch.dst,
                          r=pd_branch.z_bar.real,
                          x=pd_branch.z_bar.imag,
                          b_src=pd_branch.y_src.imag,
                          b_dst=pd_branch.y_dst.imag,
                          ratio_src=np.abs(pd_branch.rho_src),
                          phase_src=np.angle(pd_branch.rho_src) * 180 / np.pi,
                          ratio_dst=np.abs(pd_branch.rho_dst),
                          phase_dst=np.angle(pd_branch.rho_dst) * 180 / np.pi,
                          length=_nan_to_none(pd_branch.length),
                          rating=_nan_to_none(pd_branch.rating),
                          angle_min=_nan_to_none(pd_branch.angle_min),
                          angle_max=_nan_to_none(pd_branch.angle_max),
                          drop_min=_nan_to_none(pd_branch.drop_min),
                          drop_max=_nan_to_none(pd_branch.drop_max),
                          annotation=pd_branch.annotation)
        yield branch


def _get_cap_region_data(scenario, pd_cap_region):
    def get_halfspace_offset(halfspace):
        return None if halfspace is None else halfspace.offset

    def get_halfspace_slope(halfspace):
        return None if halfspace is None else halfspace.slope

    scenario.counter_cap_region_id += 1
    return DBCapabilityRegion(id=scenario.counter_cap_region_id,
                              p_min=pd_cap_region.p_min,
                              p_max=pd_cap_region.p_max,
                              q_min=pd_cap_region.q_min,
                              q_max=pd_cap_region.q_max,
                              lt_ofs=get_halfspace_offset(pd_cap_region.lt),
                              lt_slp=get_halfspace_slope(pd_cap_region.lt),
                              rt_ofs=get_halfspace_offset(pd_cap_region.rt),
                              rt_slp=get_halfspace_slope(pd_cap_region.rt),
                              lb_ofs=get_halfspace_offset(pd_cap_region.lb),
                              lb_slp=get_halfspace_slope(pd_cap_region.lb),
                              rb_ofs=get_halfspace_offset(pd_cap_region.rb),
                              rb_slp=get_halfspace_slope(pd_cap_region.rb),
                              annotation='')


def _get_converter_data(scenario):
    for index, pd_converter in scenario.converter.iterrows():
        converter_id = pd_converter.name  # Series name is the index of the row
        cap_src = _get_cap_region_data(scenario, pd_converter.cap_src)
        cap_dst = _get_cap_region_data(scenario, pd_converter.cap_dst)
        converter = DBConverter(id=converter_id,
                                src_id=pd_converter.src,
                                dst_id=pd_converter.dst,
                                cap_src_id=cap_src.id,
                                cap_dst_id=cap_dst.id,
                                loss_fwd=pd_converter.loss_fwd,
                                loss_bwd=pd_converter.loss_bwd,
                                loss_fix=pd_converter.loss_fix,
                                annotation=pd_converter.annotation)
        yield converter, cap_src, cap_dst


def _get_injector_data(scenario):
    def get_sample_points(pwl_function, function_id):
        sample_points = []
        for x, y in zip(*pwl_function.samples):
            sample_points.append(DBSamplePoint(id=function_id, x=x, y=y))
        return sample_points

    counter_cost_id = 1
    for index, pd_injector in scenario.injector.iterrows():
        injector_id = pd_injector.name  # Series name is the index of the row
        cap_region = _get_cap_region_data(scenario, pd_injector.cap)
        sample_points_p_id = None
        sample_points_p = []
        sample_points_q_id = None
        sample_points_q = []
        if pd_injector.cost_p is not None:
            sample_points_p_id = counter_cost_id
            sample_points_p = get_sample_points(pd_injector.cost_p,
                                                sample_points_p_id)
            counter_cost_id += 1
        if pd_injector.cost_q is not None:
            sample_points_q_id = counter_cost_id
            sample_points_q = get_sample_points(pd_injector.cost_q,
                                                sample_points_q_id)
            counter_cost_id += 1
        injector = DBInjector(id=injector_id,
                              type=pd_injector.type,
                              bus_id=pd_injector.bus,
                              cap_id=cap_region.id,
                              cost_p_id=sample_points_p_id,
                              cost_q_id=sample_points_q_id,
                              cost_start=pd_injector.cost_start,
                              cost_stop=pd_injector.cost_stop,
                              ramp_up=_nan_to_none(pd_injector.ramp_up),
                              ramp_down=_nan_to_none(pd_injector.ramp_down),
                              min_up=_nan_to_none(pd_injector.min_up),
                              min_down=_nan_to_none(pd_injector.min_down),
                              energy_min=_nan_to_none(pd_injector.energy_min),
                              energy_max=_nan_to_none(pd_injector.energy_max),
                              annotation=pd_injector.annotation)

        yield injector, cap_region, sample_points_p + sample_points_q


# === SAVING OF SCENARIOS =====================================================


def initialize_database(database, scenario):
    """
    Initialize an empty *hynet* grid database with the data of the scenario.

    The database is populated with the grid infrastructure and scenario data of
    the given scenario object. In the given scenario object, the scenario ID
    is reset to ``0`` and the database URI is updated.

    Parameters
    ----------
    database : DBConnection
        Connection to the *hynet* grid database.
    scenario : hynet.scenario.representation.Scenario
        Scenario object with the grid infrastructure and scenario data.

    Raises
    ------
    ValueError
        In case the database is not empty or any kind of data integrity or
        validity violation is detected.
    """
    if not database.empty:
        raise ValueError("The specified database is not empty.")

    scenario.verify()
    if np.any(scenario.branch['y_src'].values.real != 0) or \
            np.any(scenario.branch['y_dst'].values.real != 0):
        raise ValueError("Branches with a nonzero shunt conductance are "
                         "not supported.")

    scenario.id = 0
    scenario.database_uri = database.database_uri

    # Helper variable for generating IDs
    scenario.counter_cap_region_id = 0

    # Write general settings
    database.grid_name = scenario.grid_name
    database.description = scenario.description
    database.set_setting(DBInfoKey.BASE_MVA, str(scenario.base_mva))

    # Write grid infrastructure data and scenario data
    with DBTransaction(database) as transaction:

        transaction.add(DBScenario(id=scenario.id,
                                   time=scenario.time,
                                   name=scenario.name,
                                   loss_price=scenario.loss_price,
                                   annotation=scenario.annotation))

        for bus, load, shunt in _get_bus_data(scenario):
            transaction.add(bus)
            if load is not None:
                transaction.add(load)
            if shunt is not None:
                transaction.add(shunt)

        for branch in _get_branch_data(scenario):
            transaction.add(branch)

        for converter, cap_src, cap_dst in _get_converter_data(scenario):
            transaction.add(converter)
            transaction.add(cap_src)
            transaction.add(cap_dst)

        for injector, cap, sample_points in _get_injector_data(scenario):
            transaction.add(injector)
            transaction.add(cap)
            transaction.add_all(sample_points)

    # Delete helper variable for generating IDs
    del scenario.counter_cap_region_id


def save_scenario(database, scenario, auto_id=True):
    """
    Save the provided scenario to the specified *hynet* grid database.

    The scenario information in the provided scenario object is extracted and
    saved to the specified *hynet* grid database. Note that a scenario can only
    capture the following changes:

        * Changes of the load (``scenario.bus['load']``)

        * Selected changes of injectors:

            - Scaling of the cost function for active and reactive power
              (``scenario.injector[['cost_p', 'cost_q']]``). The scaling must
              be the same for both cost functions of an injector.

            - Changes of the box constraints of the capability region
              (``p_min``, ``p_max``, ``q_min``, and ``q_max`` of the objects
              in ``scenario.injector['cap']``). Note that changes of the
              parameters of the half-spaces are *not* supported.)

        * Inactivity of buses, branches, converters, injectors, and shunts.
          For example, to deactivate (decommit) an injector, remove (drop) the
          respective row in the ``injector`` data frame of the scenario.

    Any other changes are considered as a modification of the grid
    infrastructure and cannot be captured as a scenario.

    Parameters
    ----------
    database : DBConnection
        Connection to the *hynet* grid database.
    scenario : Scenario
        Scenario object that represents the new scenario.
    auto_id : bool, optional
        If True (default), the scenario ID is set to the lowest available
        scenario ID in the database. Otherwise, the scenario ID of the
        Scenario object is applied.

    Raises
    ------
    ValueError
        In case the database is empty or any kind of data integrity or validity
        violation is detected.

    See Also
    --------
    hynet.data.interface.initialize_database
    """
    if database.empty:
        raise ValueError("The specified database is empty.")

    scenario.verify()

    # Helper variable for generating IDs
    scenario.counter_cap_region_id = 0

    buses = set()
    loads = []
    shunts = set()
    branches = set()
    converters = set()
    converters_dict = dict()
    cap_regions = []
    injectors = set()
    injectors_dict = dict()
    sample_points = []

    for bus, load, shunt in _get_bus_data(scenario):
        buses.add(bus)
        if load is not None:
            loads.append(load)
        if shunt is not None:
            shunts.add(shunt)

    for branch in _get_branch_data(scenario):
        branches.add(branch)

    for converter, cap_src, cap_dst in _get_converter_data(scenario):
        converters.add(converter)
        converters_dict[converter.id] = converter
        cap_regions.append(cap_src)
        cap_regions.append(cap_dst)

    for injector, cap, sample_points_ in _get_injector_data(scenario):
        injectors.add(injector)
        injectors_dict[injector.id] = injector
        cap_regions.append(cap)
        sample_points += sample_points_

    with DBTransaction(database) as transaction:
        db_buses = set(transaction.query(DBBus))
        db_branches = set(transaction.query(DBBranch))
        db_converters = set(transaction.query(DBConverter))
        db_injectors = set(transaction.query(DBInjector))
        db_shunts = set(transaction.query(DBShunt))
        db_sample_points = transaction.query(DBSamplePoint)

        # Verify that the grid infrastructure is equivalent
        #
        # REMARK: The following set operations utilize specialized equality
        # operators of the DB objects, see ``structure.py``. They consider that
        # the IDs of shunts, sample points, and capability regions may differ.
        # Furthermore, they consider that the cost functions allow for a
        # scaling and that the capability regions may exhibit different box
        # constraints.
        message_prefix = "Difference of the grid infrastructure detected: "

        if buses - db_buses:
            raise ValueError(message_prefix + "Buses differ.")
        if branches - db_branches:
            raise ValueError(message_prefix + "Branches differ.")
        if converters - db_converters:
            raise ValueError(message_prefix + "Converters differ.")
        if injectors - db_injectors:
            raise ValueError(message_prefix + "Injectors differ.")
        if shunts - db_shunts:
            raise ValueError(message_prefix + "Shunts differ.")

        # Check if the capability regions of the converters are equal
        def compare_cap_region(cap1, cap2):
            return (cap1 == cap2 and  # Check half-spaces
                    cap1.p_min == cap2.p_min and
                    cap1.p_max == cap2.p_max and
                    cap1.q_min == cap2.q_min and
                    cap1.q_max == cap2.q_max)

        for converter in db_converters:
            if converter in converters:
                converter_new = converters_dict[converter.id]
                cap_src_new = cap_regions[converter_new.cap_src_id - 1]
                cap_dst_new = cap_regions[converter_new.cap_dst_id - 1]
                if not (compare_cap_region(cap_src_new, converter.cap_src) and
                        compare_cap_region(cap_dst_new, converter.cap_dst)):
                    raise ValueError(message_prefix +
                                     "Converter capability regions differ.")

        def load_sample_points(injector, extract_func_id):
            sp_db = db_sample_points.filter(
                DBSamplePoint.id == extract_func_id(injector)).all()
            sp_new = [sp for sp in sample_points
                      if sp.id == extract_func_id(injectors_dict[injector.id])]
            if len(sp_new) != len(sp_db):
                raise ValueError("Number of cost function samples differs.")

            if len(sp_new) == 0:
                return None, None

            def points2tuples(sample_points):
                x = np.array([sp.x for sp in sample_points])
                y = np.array([sp.y for sp in sample_points])
                idx = np.argsort(x)
                return x[idx], y[idx]

            return points2tuples(sp_db), points2tuples(sp_new)

        def get_function_scaling(injector, extract_func_id):
            sp_db, sp_new = load_sample_points(injector, extract_func_id)
            if sp_new is None:
                return None

            if any(np.abs(sp_db[0] - sp_new[0]) > 10 * hynet_eps):
                raise ValueError("The x-samples of cost functions differ.")

            with np.errstate(divide='ignore', invalid='ignore'):
                scaling = np.true_divide(sp_new[1], sp_db[1])
            scaling = scaling[np.abs(sp_db[1]) > 1e-6]
            if not scaling.size:
                if any(np.abs(sp_new[1]) > 1e-6):
                    raise ValueError("Scaling of zero cost is invalid.")
                return None
            if any(np.abs(scaling - scaling[0]) > 10 * hynet_eps):
                raise ValueError("Some cost function samples are not scaled "
                                 "uniformly.")
            return scaling[0]

        for injector in db_injectors:
            if injector in injectors:
                cap_new = cap_regions[injectors_dict[injector.id].cap_id - 1]
                if cap_new != injector.cap:
                    raise ValueError("The half-spaces of some injector "
                                     "capability regions differ.")

                scaling_p = get_function_scaling(injector,
                                                 lambda x: x.cost_p_id)
                scaling_q = get_function_scaling(injector,
                                                 lambda x: x.cost_q_id)

                if scaling_p is None and scaling_q is None:
                    injector.cost_scaling = 1.0
                elif scaling_p is not None and scaling_q is None:
                    injector.cost_scaling = scaling_p
                elif scaling_p is None and scaling_q is not None:
                    injector.cost_scaling = scaling_q
                else:
                    if not np.isclose(scaling_p, scaling_q):
                        raise ValueError("Some active and reactive cost "
                                         "functions are not scaled jointly.")
                    injector.cost_scaling = scaling_p

        # Verification passed. Save the scenario to the database.
        if auto_id:
            scenario.id = get_max_scenario_id(database) + 1
        scenario.database_uri = database.database_uri

        transaction.add(DBScenario(id=scenario.id,
                                   time=scenario.time,
                                   name=scenario.name,
                                   loss_price=scenario.loss_price,
                                   annotation=scenario.annotation))

        # Save load information
        for load in loads:
            load.scenario_id = scenario.id
        transaction.add_all(loads)

        # Save injector information
        for index, pd_injector in scenario.injector.iterrows():
            db_injector = None
            for injector in db_injectors:
                if injector.id == pd_injector.name:
                    db_injector = injector
                    break
            assert db_injector is not None  # This is already checked above...

            # Skip injector reconfiguration if there was no modification
            if (np.isclose(db_injector.cost_scaling, 1.0) and
                    db_injector.cap.p_min == pd_injector.cap.p_min and
                    db_injector.cap.p_max == pd_injector.cap.p_max and
                    db_injector.cap.q_min == pd_injector.cap.q_min and
                    db_injector.cap.q_max == pd_injector.cap.q_max):
                continue

            transaction.add(
                DBScenarioInjector(scenario_id=scenario.id,
                                   injector_id=pd_injector.name,
                                   p_min=pd_injector.cap.p_min,
                                   p_max=pd_injector.cap.p_max,
                                   q_min=pd_injector.cap.q_min,
                                   q_max=pd_injector.cap.q_max,
                                   cost_scaling=db_injector.cost_scaling))

        # Save inactivity information
        inactive_buses = db_buses - buses
        inactive_branches = db_branches - branches
        inactive_converters = db_converters - converters
        inactive_shunts = db_shunts - shunts
        inactive_injectors = db_injectors - injectors

        def create_inactivity_datasets(entity_type, inactive_entities):
            return map(lambda entity:
                       DBScenarioInactivity(scenario_id=scenario.id,
                                            entity_type=entity_type,
                                            entity_id=entity.id),
                       inactive_entities)

        transaction.add_all(create_inactivity_datasets(EntityType.BUS,
                                                       inactive_buses))
        transaction.add_all(create_inactivity_datasets(EntityType.BRANCH,
                                                       inactive_branches))
        transaction.add_all(create_inactivity_datasets(EntityType.CONVERTER,
                                                       inactive_converters))
        transaction.add_all(create_inactivity_datasets(EntityType.SHUNT,
                                                       inactive_shunts))
        transaction.add_all(create_inactivity_datasets(EntityType.INJECTOR,
                                                       inactive_injectors))

    # Delete helper variable for generating IDs
    del scenario.counter_cap_region_id


# === REMOVING OF SCENARIOS ===================================================


def remove_scenarios(database, scenario_ids):
    """
    Remove the specified scenarios from the *hynet* grid database file.

    Parameters
    ----------
    database : DBConnection
        Connection to the *hynet* grid database.
    scenario_ids : list[.hynet_id_]
        List of identifiers for the scenarios that shall be removed.

    Raises
    ------
    ValueError
        In case that a scenario with the specified ID was not found.
    """
    # Check if all scenarios exist
    scenario_info = get_scenario_info(database)
    for scenario_id in scenario_ids:
        if not scenario_info.index.contains(scenario_id):
            raise ValueError("The database does not contain a scenario with "
                             "the ID '{:d}'.".format(scenario_id))

    # Remove the scenarios
    for scenario_id in scenario_ids:
        with DBTransaction(database) as transaction:
            scenario = \
                _select_scenario(scenario_id, transaction)
            scenarios_loads = \
                _select_scenario_loads(scenario_id, transaction)
            scenario_injectors = \
                _select_scenario_injectors(scenario_id, transaction)
            scenario_inactivities = \
                _select_scenario_inactivities(scenario_id, transaction)

            transaction.delete_all(scenarios_loads)
            transaction.delete_all(scenario_injectors)
            transaction.delete_all(scenario_inactivities)
            transaction.delete(scenario)


# === COPYING OF SCENARIOS ====================================================


def copy_scenarios(source_database, destination_database,
                   scenario_ids=None, bus_id_map=None):
    """
    Copy the scenarios from the source to the destination *hynet* grid database.

    **Caution:** Note that this function does *not* verify that the grid
    infrastructure of the source and destination database is compatible, it
    only copies the content of the scenario information tables for the
    requested scenarios. In case a scenario with a specified ID already exists
    in the destination database, it is *skipped*.

    Parameters
    ----------
    source_database : DBConnection
        Connection to the source *hynet* grid database.
    destination_database : DBConnection
        Connection to the destination *hynet* grid database.
    scenario_ids : list[.hynet_id_], optional
        List of scenario identifiers that shall be copied. By default, all
        scenarios except the "base case" with scenario ID 0 are copied.
    bus_id_map : pandas.Series, optional
        If provided, this series, *indexed by the bus IDs in the source
        database*, specifies the mapping of a bus ID in the source database to
        a bus ID in the destination database. This is necessary, e.g., after
        a network reduction, where certain buses are combined and the load
        shall be accumulated at the aggregated bus. By default, a one-to-one
        mapping is considered.
    """
    if scenario_ids is None:
        scenario_ids = get_scenario_info(source_database).index

    dst_scenario_ids = get_scenario_info(destination_database).index

    if bus_id_map is None:
        _id_range = range(get_max_bus_id(source_database) + 1)
        bus_id_map = pd.Series(_id_range, index=_id_range)

    for scenario_id in scenario_ids:
        if dst_scenario_ids.contains(scenario_id):
            _log.warning("Scenario with ID '{:d}' already exists. Skipping it."
                         .format(scenario_id))
            continue

        with DBTransaction(source_database) as src_transaction, \
                DBTransaction(destination_database) as dst_transaction:
            # Load scenario information from the source database
            scenario = \
                _select_scenario(scenario_id, src_transaction)
            loads = \
                _select_scenario_loads(scenario_id, src_transaction)
            injectors = \
                _select_scenario_injectors(scenario_id, src_transaction)
            inactivities = \
                _select_scenario_inactivities(scenario_id, src_transaction)

            # Prepare data for copying
            make_transient(scenario)

            new_loads = dict()
            for load in loads:
                make_transient(load)
                load.bus_id = int(bus_id_map.at[load.bus_id])

                # Accumulate the load for every bus
                if load.bus_id in new_loads:
                    new_loads[load.bus_id].p += load.p
                    new_loads[load.bus_id].q += load.q
                else:
                    new_loads[load.bus_id] = load

            for injector in injectors:
                make_transient(injector)

            for inactivity in inactivities:
                make_transient(inactivity)
                if inactivity.entity_type == EntityType.BUS:
                    inactivity.entity_id = \
                        int(bus_id_map.at[inactivity.entity_id])

            # Write scenario information to the destination database
            dst_transaction.add(scenario)
            dst_transaction.add_all(new_loads.values())
            dst_transaction.add_all(injectors)
            dst_transaction.add_all(inactivities)
